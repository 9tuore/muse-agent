#!/usr/bin/env python3
"""Collect original licensing files for a resolved Cargo source inventory.

This deliberately includes build/dev/other-target packages in supplied metadata;
it does not claim these are precisely the libraries linked into a shipped binary.
No network, Cargo build, user profile, or credential access is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit, urlunsplit

LICENSE_NAME = re.compile(r'^(?:licen[cs]e|copying|copyright|notice|authors|unlicense)(?:[. _-].*)?$', re.I)
LICENSE_DIRS = {'licenses', 'licences', 'license', 'licence'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public_url(value):
    if not value:
        return None
    # Cargo path+file package IDs and machine-local locations never enter index.
    value = re.sub(r'^(?:git|registry)\+', '', value)
    parsed = urlsplit(value)
    if parsed.scheme not in {'https', 'http', 'ssh', 'git'} or not parsed.hostname:
        return None
    host = parsed.hostname
    if parsed.port:
        host += ':' + str(parsed.port)
    return urlunsplit((parsed.scheme, host, parsed.path, '', ''))


def direct_documents(directory, boundary):
    documents = []
    if not directory.is_dir():
        return documents
    for child in sorted(directory.iterdir()):
        if child.is_file() and LICENSE_NAME.match(child.name):
            if child.resolve().is_relative_to(boundary):
                documents.append(child)
        elif child.is_dir() and not child.is_symlink() and child.name.lower() in LICENSE_DIRS:
            for item in sorted(child.rglob('*')):
                if item.is_file() and item.resolve().is_relative_to(boundary):
                    documents.append(item)
    return documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--kernel-source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = args.metadata.read_bytes()
    metadata = json.loads(raw)
    sdk = args.sdk.resolve()
    roots = {'OctoSense': sdk, 'Makepad': sdk/'.sources/makepad',
             'OctoSense-App-Hub': sdk/'.sources/app-hub',
             'OctoScript': sdk/'.sources/octoscript',
             'OctoScript-Makepad': sdk/'.sources/octoscript-makepad',
             'Octos-Kernel-source': args.kernel_source.resolve()}
    roots = {label: path.resolve() for label, path in roots.items()}
    for label, root in roots.items():
        if not root.is_dir():
            raise ValueError(f'Required source directory missing: {label}')
    out = args.out.absolute()
    out.mkdir(parents=True, exist_ok=False)
    copies = {}
    cache = {}

    def copy_document(path):
        data = path.read_bytes()
        sha = digest(data)
        if sha not in copies:
            name = re.sub(r'[^A-Za-z0-9._-]', '_', path.name) or 'document'
            relative = Path('texts')/sha/name
            destination = out/relative
            destination.parent.mkdir(parents=True)
            destination.write_bytes(data)
            if digest(destination.read_bytes()) != sha:
                raise IOError('License copy did not match its source')
            copies[sha] = {'path': relative.as_posix(), 'sha256': sha, 'bytes': len(data)}
        return copies[sha]

    def documents(directory, boundary):
        key = (directory, boundary)
        if key not in cache:
            cache[key] = direct_documents(directory, boundary)
        return cache[key]

    def boundary_for(directory, registry):
        if registry:
            return directory
        matches = [r for r in roots.values() if directory.is_relative_to(r)]
        if matches:
            return max(matches, key=lambda p: len(p.parts))
        # Git source metadata points into a checkout. Stop at its repository;
        # never scan a home directory or any sibling/user data.
        for parent in [directory, *list(directory.parents)[:8]]:
            if (parent/'.git').exists():
                return parent
        return directory

    def collect(directory, boundary, explicit=None):
        found = {}
        if explicit and explicit.is_file() and explicit.resolve().is_relative_to(boundary):
            found[explicit.resolve()] = 'declared_license_file'
        current = directory
        while current.is_relative_to(boundary):
            for path in documents(current, boundary):
                found.setdefault(path.resolve(), 'package' if current == directory else 'source_ancestor')
            if current == boundary:
                break
            current = current.parent
        refs = [{'source_relative_path': str(path.relative_to(boundary)),
                 'scope': scope, **copy_document(path)} for path, scope in sorted(found.items())]
        declarations = []
        if not refs:
            # Keep the actual declaration when a distribution omits license
            # texts. Do not invent a copyright holder or substitute a license.
            for filename in ['Cargo.toml', 'Cargo.toml.orig', 'README.md', 'ABOUT.md']:
                candidate = directory/filename
                if candidate.is_file() and candidate.resolve().is_relative_to(boundary):
                    if filename.endswith('.md') and not re.search(rb'licen[cs]|copyright', candidate.read_bytes(), re.I):
                        continue
                    declarations.append({'source_relative_path': str(candidate.relative_to(boundary)),
                                         'scope': 'declaration_only_not_license_text', **copy_document(candidate)})
        return refs, declarations

    components = []
    for package in sorted(metadata['packages'], key=lambda p: (p['name'], p['version'], p.get('source') or '', p['manifest_path'])):
        directory = Path(package['manifest_path']).resolve().parent
        kind = (package.get('source') or 'path').split('+', 1)[0]
        boundary = boundary_for(directory, kind == 'registry')
        explicit = package.get('license_file')
        explicit = (directory/explicit).resolve() if explicit else None
        refs, declarations = collect(directory, boundary, explicit)
        components.append({'name': package['name'], 'version': package['version'],
                           'declared_license': package.get('license'),
                           'source_kind': kind, 'repository': public_url(package.get('repository')),
                           'source_url': public_url(package.get('source')),
                           'source_revision': (package.get('source') or '').rsplit('#', 1)[-1]
                               if kind == 'git' and '#' in (package.get('source') or '') else None,
                           'package_relative_path': str(directory.relative_to(boundary)),
                           'license_documents': refs, 'declaration_documents': declarations,
                           'status': 'SOURCE_DOCUMENTS_COLLECTED' if refs else 'DECLARATION_ONLY_NO_LICENSE_TEXT_FOUND'})
    repositories = []
    for label, root in roots.items():
        refs, declarations = collect(root, root)
        revision = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        remote = subprocess.run(['git', '-C', str(root), 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        repositories.append({'name': label, 'revision': revision.stdout.strip() if revision.returncode == 0 else None,
                             'source_url': public_url(remote.stdout.strip()) if remote.returncode == 0 else None,
                             'license_documents': refs, 'declaration_documents': declarations,
                             'status': 'SOURCE_DOCUMENTS_COLLECTED' if refs else 'DECLARATION_ONLY_NO_LICENSE_TEXT_FOUND'})
    summary = {'resolved_cargo_packages': len(components),
               'packages_with_source_license_documents': sum(bool(c['license_documents']) for c in components),
               'packages_with_declarations_only': sum(not c['license_documents'] for c in components),
               'explicit_source_repositories': len(repositories), 'unique_source_documents': len(copies),
               'copied_bytes': sum(c['bytes'] for c in copies.values())}
    index = {'schema': 1, 'scope': 'Resolved Host Cargo metadata, including build/dev/other-target dependencies, plus explicitly named source repositories. Not an exact runtime-linkage or legal compliance determination.',
             'model_licenses': 'Qwen and llama.cpp license files remain separately, unchanged, under Resources/local-model/licenses.',
             'metadata_sha256': digest(raw), 'summary': summary, 'repositories': repositories, 'packages': components}
    encoded = json.dumps(index, ensure_ascii=False, indent=2)+'\n'
    if any(str(root) in encoded for root in roots.values()) or '/Users/' in encoded or '/home/' in encoded:
        raise ValueError('A machine absolute path entered the portable index')
    (out/'index.json').write_text(encoded)
    (out/'README.txt').write_text('Third-party source notices\n\nOriginal files are preserved byte for byte under texts/, deduplicated by SHA-256. index.json identifies their original names, source scope and each package license declaration. Source-ancestor documents are identified separately from package-local files.\n\nThis inventory includes the supplied Cargo resolution across build, development and target-specific packages, plus the SDK, Makepad, App Hub, OctoScript and Octos source roots. It is not an exact list of runtime-linked libraries. When a source distribution has no license text, its original manifest/declaration is retained and that absence is identified in the index. No replacement text or copyright holder is invented.\n\nQwen and llama.cpp notices are preserved separately at Resources/local-model/licenses.\n', encoding='utf-8')
    hashes = {str(p.relative_to(out)): digest(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'SHA256.json').write_text(json.dumps(hashes, indent=2)+'\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()

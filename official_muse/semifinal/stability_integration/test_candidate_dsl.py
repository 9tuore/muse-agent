"""Portable static patch checks and SYNTHETIC candidate mapping counterexamples."""
import json
from pathlib import Path
import tempfile
import unittest

from audit_candidate_mapping import audit, sha, view_contract

OWNED = Path(__file__).resolve().parent


class HistoricalPatchChecks(unittest.TestCase):
    def test_only_ui_expansion_and_reset_are_added(self):
        patch = (OWNED / 'action_chain_dsl.patch').read_text()
        added = '\n'.join(l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++'))
        self.assertIn('let ac_dsl_open = false', added)
        self.assertIn('if ac_dsl_open {', added)
        self.assertIn('chain.to_json()', added)
        self.assertIn('ac_dsl_open = !ac_dsl_open ac_refresh()', added)
        for forbidden in ('host.request', 'storage.', 'select_goal(', 'ac_state(', 'fn ac_projection(', 'start_timeout', 'ui_layout_save'):
            self.assertNotIn(forbidden, added)
        removed = [l for l in patch.splitlines() if l.startswith('-') and not l.startswith('---')]
        self.assertEqual(len(removed), 2)
        self.assertTrue(all('ac_choose' in l or 'ac_selected_chat' in l for l in removed))

    def test_patch_identity(self):
        identity = json.loads((OWNED / 'action_chain_dsl_identity.json').read_text())
        self.assertEqual(identity['patch_sha256'], sha((OWNED / 'action_chain_dsl.patch').read_bytes()))
        self.assertEqual(identity['status'], 'PROPOSED_NOT_VM_TESTED')


class MappingChecks(unittest.TestCase):
    def prepare(self, root):
        source, artifact = b'// SYNTHETIC\nabc\n', b'\nabc\n'
        manifest = {'id': 'synthetic', 'version': 'test', 'host_api': {'required': {'runtime.list': 1}}, 'capabilities': ['runtime']}
        for name, data in [('readable-bundle', source), ('bundle', artifact)]:
            (root / name).mkdir()
            (root / name / 'main.splash').write_bytes(data)
            (root / name / 'manifest.json').write_text(json.dumps(manifest))
        identity = {'id': 'synthetic', 'version': 'test', 'source_sha256': sha(source), 'artifact_sha256': sha(artifact),
                    'required': {'runtime.list': 1}, 'capabilities': ['runtime'],
                    'source_transform': {'source_sha256': sha(source), 'artifact_sha256': sha(artifact), 'bytes_before': len(source), 'bytes_after': len(artifact)}}
        (root / 'identity.json').write_text(json.dumps(identity))

    def test_synthetic_mapping_is_not_runtime_acceptance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.prepare(root)
            result, code = audit(root)
            self.assertEqual(code, 0)
            self.assertEqual(result['final_20_runs'], 'NOT_TESTED')
            self.assertEqual(result['token_opcode_equivalence'], 'NOT_TESTED')

    def test_changed_artifact_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.prepare(root)
            (root / 'bundle/main.splash').write_bytes(b'changed')
            result, code = audit(root)
            self.assertEqual(code, 1)
            self.assertFalse(result['checks']['artifact_sha'])

    def test_changed_manifest_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.prepare(root)
            (root / 'bundle/manifest.json').write_text('{}')
            result, code = audit(root)
            self.assertEqual(code, 1)
            self.assertFalse(result['checks']['manifest_identity'])

    def test_missing_artifact_is_not_tested(self):
        with tempfile.TemporaryDirectory() as d:
            result, code = audit(Path(d))
            self.assertEqual(code, 2)
            self.assertEqual(result['status'], 'NOT_TESTED')


# SYNTHETIC interface fixture, never a claim of Splash VM execution.
VIEW = b'''fn dsl_view(kind,records){
    return {schema_version: "muse.view/1" kind: kind read_only: true
        tool_authority: false records: records}
}
Label{text: dsl_view("action_chain",[chain]).to_json()}
'''


class ViewContractChecks(unittest.TestCase):
    def test_read_only_envelope_and_compact_spacing(self):
        self.assertTrue(all(view_contract(VIEW).values()))
        compact_fixture = VIEW.replace(b'    ', b'').replace(b': ', b':').replace(b'\n', b' ')
        self.assertTrue(all(view_contract(compact_fixture).values()))

    def test_authority_escalation_fails(self):
        self.assertFalse(view_contract(VIEW.replace(b'tool_authority: false', b'tool_authority: true'))['view_helper_read_only'])

    def test_schema_change_fails(self):
        self.assertFalse(view_contract(VIEW.replace(b'muse.view/1', b'muse.execute/1'))['view_helper_read_only'])

    def test_raw_projection_does_not_satisfy_new_interface(self):
        self.assertFalse(view_contract(VIEW.replace(b'dsl_view("action_chain",[chain]).to_json()', b'chain.to_json()'))['action_chain_view_call'])

    def test_old_candidate_requires_explicit_envelope_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); MappingChecks().prepare(root)
            result, code = audit(root, require_view_envelope=True)
            self.assertEqual(code, 1)
            self.assertFalse(result['checks']['readable_view_helper_read_only'])


if __name__ == '__main__':
    unittest.main()

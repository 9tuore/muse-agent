"""Actual GPT01 Kernel JSONL client; tool planning is an explicit parent fixture."""
import hashlib, json, queue, shutil, subprocess, sys, threading
from pathlib import Path

PINNED_KERNEL = '56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270'
CENTRAL_FIXTURES = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/night-004')


def prompt_object(prompt, marker):
    if prompt.count(marker) != 1:
        raise ValueError('Expected one production prompt marker: '+marker)
    value, _ = json.JSONDecoder().raw_decode(prompt.split(marker, 1)[1].lstrip())
    if not isinstance(value, dict):
        raise ValueError('Production prompt arguments must be an object')
    return value


def fixture_turn_payload(payload):
    """Keep original payload, including text/trigger; add separate fixture inputs."""
    if not isinstance(payload.get('text'), str) or any(k.startswith('fixture_') for k in payload):
        raise ValueError('Original VM text required; fixture fields belong to parent only')
    text = payload['text']
    if '精确 calendar.add_event 参数：' in text:
        args = prompt_object(text, '精确 calendar.add_event 参数：')
        if set(args) != {'title','start','end','timezone','location','notes','request_id'} or not args['request_id']:
            raise ValueError('Incomplete production create arguments')
        steps = [dict(tool='calendar.add_event', args=args),
                 dict(tool='calendar.get_event', args={'id': {'$tool_result': 0, 'path': ['id']}})]
    elif '2. calendar.update_event 精确参数：' in text:
        args = prompt_object(text, '2. calendar.update_event 精确参数：')
        if set(args) != {'id','expected','title','start','end','timezone','location','notes'}:
            raise ValueError('Incomplete production update arguments')
        expected = args['expected']
        if not isinstance(expected, dict) or set(expected) != {'id','request_id','title','start','end','timezone','location','notes'} or args['id'] != expected['id']:
            raise ValueError('Exact selected old event is required')
        # Preserve the selected snapshot verbatim. Actual update_event CAS refuses
        # any divergence found by the first real get; never substitute a newer event.
        steps = [dict(tool='calendar.get_event', args={'id': args['id']}),
                 dict(tool='calendar.update_event', args=args),
                 dict(tool='calendar.get_event', args={'id': args['id']})]
    else:
        raise ValueError('No supported native create/update production prompt')
    result = dict(payload, fixture_tool_plan=steps, fixture_approval='once')
    assert result['text'] == payload['text'] and result.get('trigger') == payload.get('trigger')
    return result


def validate_candidate(settings, out, source_sha, source_file):
    bundle_main = Path(settings['signed_bundle'])/'main.splash'
    bundle_sha = hashlib.sha256(bundle_main.read_bytes()).hexdigest()
    assert settings['main_sha256'] == bundle_sha, 'Explicit signed candidate SHA differs'
    mapping = {'upstream_source_sha256':source_sha,'signed_main_sha256':bundle_sha}
    if bundle_sha != source_sha:
        # prepare_bundle.py changes only the displayed version before running
        # the repository's actual compact CLI. Verify both steps, not metadata alone.
        identity_path = Path(settings.get('candidate_identity',str(bundle_main.parent.parent/'bundle-identity.json')))
        candidate = json.loads(identity_path.read_text())
        readable = identity_path.parent/'readable-bundle'
        source = source_file.read_text()
        assert hashlib.sha256(source.encode()).hexdigest() == source_sha
        assert candidate['upstream_source_sha256'] == source_sha
        assert source.count('Muse · 0.3.27-rc18') == 1
        assert source.replace('Muse · 0.3.27-rc18','Muse · '+candidate['version']) == (readable/'main.splash').read_text()
        assert hashlib.sha256((readable/'main.splash').read_bytes()).hexdigest() == candidate['transform']['source_sha256']
        assert bundle_sha == candidate['transform']['artifact_sha256']
        compact_tool = Path(__file__).resolve().parents[6]/'official_muse/ui_memory/compact_bundle.py'
        reproduced = out/'candidate-recompact'
        result = subprocess.run([sys.executable,str(compact_tool),'--source',str(readable),'--out',str(reproduced)],
                                capture_output=True,text=True,check=True)
        assert (reproduced/'main.splash').read_bytes() == bundle_main.read_bytes(), 'Actual compact replay differs from signed main'
        mapping.update(readable_source_sha256=candidate['transform']['source_sha256'],
                       candidate_identity_sha256=hashlib.sha256(identity_path.read_bytes()).hexdigest(),
                       compact_tool_sha256=hashlib.sha256(compact_tool.read_bytes()).hexdigest(),
                       actual_compact_replay=json.loads(result.stdout),version=candidate['version'])
    return mapping


class KernelBridge:
    def __init__(self, *, bridge, test_binary, kernel, config, out, source_sha, source_file):
        self.out, self.serial, self.pending, self.lock = out, 0, {}, threading.Lock()
        self.frames, self.reader_error = [], None
        config = config.resolve(strict=True)
        settings = json.loads(config.read_text())
        fixture_root = Path(settings['fixture_root']).resolve(strict=True)
        fixture_root.relative_to(CENTRAL_FIXTURES.resolve(strict=True))
        assert fixture_root != CENTRAL_FIXTURES and (fixture_root/'FIXTURE_ONLY').is_file()
        mapping = validate_candidate(settings,out,source_sha,source_file)
        assert hashlib.sha256(kernel.read_bytes()).hexdigest() == PINNED_KERNEL
        helper = out/'kernel-helper'; helper.mkdir()
        for name in ('bridge.py','plan_model.py'):
            shutil.copy2(bridge.parent/name, helper/name)
        shutil.copy2(config, helper/'config.json')
        shutil.copy2(test_binary.resolve(strict=True), helper/'shell-test-bin')
        self.identity = dict(source_sha256=source_sha, kernel_sha256=PINNED_KERNEL,
            test_binary_sha256=hashlib.sha256((helper/'shell-test-bin').read_bytes()).hexdigest(),
            bridge_sha256=hashlib.sha256((helper/'bridge.py').read_bytes()).hexdigest(),
            model_sha256=hashlib.sha256((helper/'plan_model.py').read_bytes()).hexdigest(),
            config_sha256=hashlib.sha256(config.read_bytes()).hexdigest(), fixture_root=str(fixture_root),candidate_mapping=mapping)
        self.log = (out/'kernel-wrapper-stderr.log').open('w')
        self.ready_queue = queue.Queue()
        self.process = subprocess.Popen([sys.executable,str(helper/'bridge.py'),
            '--test-binary',str(helper/'shell-test-bin'),'--kernel',str(kernel.resolve()),
            '--config',str(helper/'config.json')], stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=self.log,text=True,bufsize=1)
        self.thread = threading.Thread(target=self._read,daemon=True); self.thread.start()
        try:
            self.ready = self.ready_queue.get(timeout=60)
            if isinstance(self.ready,Exception): raise self.ready
            assert self.ready.get('is_ok') is True and self.ready['data']['source_main_sha256'] == mapping['signed_main_sha256']
            assert self.ready['data']['kernel_sha256'] == PINNED_KERNEL
        except Exception:
            self.process.stdin.close()
            try: self.process.wait(timeout=10)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait()
            self.log.close()
            raise

    def _read(self):
        try:
            with (self.out/'kernel-wrapper-stdout.jsonl').open('w') as raw:
                for line in self.process.stdout:
                    raw.write(line); raw.flush()
                    reply = json.loads(line); self.frames.append(reply)
                    if reply.get('method') == 'fixture.ready': self.ready_queue.put(reply)
                    else:
                        with self.lock: target = self.pending.get(reply.get('request_id'))
                        if target is None: raise ValueError('Unmatched actual Kernel request_id')
                        target.put(reply)
        except Exception as error:
            self.reader_error = str(error)
        finally:
            failure = RuntimeError(self.reader_error or 'Actual Kernel bridge closed its output')
            self.ready_queue.put(failure)
            with self.lock:
                for target in self.pending.values(): target.put(failure)

    def call(self, method, payload, timeout=195):
        outbound = fixture_turn_payload(payload) if method == 'octos.turn.start' else dict(payload)
        with self.lock:
            self.serial += 1; request_id = 'gpt02-kernel-'+str(self.serial)
            target = self.pending[request_id] = queue.Queue()
            request = dict(request_id=request_id,method=method,payload=outbound)
            with (self.out/'kernel-parent-requests.jsonl').open('a') as log:
                log.write(json.dumps(dict(original_payload=payload,request=request),ensure_ascii=False)+'\n')
            self.process.stdin.write(json.dumps(request,ensure_ascii=False)+'\n'); self.process.stdin.flush()
        try:
            reply = target.get(timeout=timeout)
            if isinstance(reply,Exception): raise reply
            assert reply['request_id'] == request_id and reply['method'] == method
            # Transport fields only are removed. History/result/error remain actual bytes' values.
            return {k:v for k,v in reply.items() if k not in ('request_id','method')}
        finally:
            with self.lock: self.pending.pop(request_id,None)

    def close(self):
        try: self.call('fixture/quit',{},timeout=15)
        except Exception as error: self.identity['quit_error'] = str(error)
        self.process.stdin.close()
        try: self.identity['exit_code'] = self.process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            self.process.kill(); self.identity['exit_code'] = self.process.wait()
            self.identity['forced_stop'] = True
        self.thread.join(timeout=5)
        self.log.close()
        self.identity['reader_error'] = self.reader_error

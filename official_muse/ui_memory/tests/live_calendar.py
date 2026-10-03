#!/usr/bin/env python3
"""Real system calendar test for the one explicitly approved synthetic event.

Run create-update and cleanup only after the person approves the exact changes.
No TCC decisions, Host mocks, service patching or automatic write retries.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote

TEST_ID = 'MUSE-R2-UI-GLOBAL-20261003-032'
START = '2026-10-04T15:00:00+08:00'
END = '2026-10-04T15:20:00+08:00'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--stage', choices=('create-update', 'cleanup'), required=True)
    p.add_argument('--port', type=int, default=8411)
    a = p.parse_args()
    jail = a.candidate.resolve() / 'private/apps/muse-goals'
    expected = json.loads((a.candidate / 'candidate.json').read_text())
    assert hashlib.sha256((jail / 'bundle/main.splash').read_bytes()).hexdigest() == expected['source_sha256']
    r = Remote(a.port)
    report = json.loads((a.out / 'report.json').read_text())
    assert report['title'] == TEST_ID and report['source_sha256'] == expected['source_sha256']

    def save():
        (a.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def state():
        path = jail / 'calendar-state.json'
        # A fresh app has no persisted receipts until its first actual write.
        return json.loads(path.read_text()) if path.exists() else {'links': [], 'receipts': []}

    def receipts(service):
        return [v for v in state()['receipts'] if v['service'] == service and v['status'] == 'verified']

    def wait_receipt(service, before):
        for _ in range(240):
            values = receipts(service)
            if len(values) > before:
                return values[-1]
            time.sleep(.1)
        raise TimeoutError('System receipt not verified; inspect state without retrying the write')

    def scroll(dy):
        x, y, w, h = r.find('calendar_editor')['r']
        r.scroll(int(x+w/2), int(y+h/2), dy)

    def field(key, value):
        scroll(-10000)
        for _ in range(45):
            try:
                if r.find(key)['r'][3] >= 30:
                    break
            except AssertionError:
                pass
            scroll(100)
        else:
            raise RuntimeError('Input not reachable: '+key)
        r.set_text(key, value)

    def preview():
        r.click_scroll('查询当前候选冲突', 'calendar_editor', 45)
        time.sleep(.3)
        r.click_scroll('预览精确日历操作', 'calendar_editor', 45)
        reveal_confirmation()

    def reveal_confirmation():
        for _ in range(25):
            try:
                if r.find('确认执行这项系统日历操作')['r'][3] >= 30:
                    return
            except AssertionError:
                pass
            scroll(100)
        raise RuntimeError('Confirmation is not reachable')

    try:
        if a.stage == 'create-update':
            assert not receipts('calendar.create'), 'Existing write must not be repeated'
            r.click('确认执行这项系统日历操作')
            created = wait_receipt('calendar.create', 0)
            assert json.loads(created['payload_json'])['title'] == TEST_ID
            assert created['event_id'] and created['version']
            report.update(created_verified_receipt=created, writes=True, status='CREATE_VERIFIED')
            save()
            r.shot(a.out / 'created-readback.png')
            scroll(-10000)
            r.click_scroll('修改所选', 'calendar_editor', 45)
            field('calendar_end', END)
            preview()
            r.shot(a.out / 'update-confirmation.png')
            before = len(receipts('calendar.update'))
            r.click('确认执行这项系统日历操作')
            updated = wait_receipt('calendar.update', before)
            assert updated['event_id'] == created['event_id'] and updated['version'] != created['version']
            assert json.loads(updated['payload_json'])['end'] == END
            report.update(updated_verified_receipt=updated, status='CREATE_UPDATE_READBACK_PASS_CLEANUP_PENDING')
            r.shot(a.out / 'updated-readback.png')
        else:
            r.click_scroll('日历', 'shortcuts')
            r.click_scroll('工作 · 可写', 'calendar_editor', 45)
            r.click_scroll('日程', 'calendar_editor', 45)
            r.click_scroll('＋ 新建日程', 'calendar_editor', 45)
            field('calendar_range_start', START)
            field('calendar_range_end', '2026-10-04T15:30:00+08:00')
            scroll(-10000)
            r.click_scroll('查询选中日历与范围', 'calendar_editor', 45)
            time.sleep(.3)
            scroll(-10000)
            r.click_scroll(TEST_ID, 'calendar_editor', 45)
            r.click_scroll('删除所选', 'calendar_editor', 45)
            field('calendar_delete_id', TEST_ID)
            r.click_scroll('预览精确日历操作', 'calendar_editor', 45)
            reveal_confirmation()
            r.shot(a.out / 'delete-confirmation.png')
            before = len(receipts('calendar.delete'))
            r.click('确认执行这项系统日历操作')
            deleted = wait_receipt('calendar.delete', before)
            assert deleted['event_id'] == report['created_verified_receipt']['event_id']
            report.update(deleted_verified_receipt=deleted, cleanup_independent_get_found_false=True, status='PASS')
            r.shot(a.out / 'deleted-readback.png')
        save()
        print(json.dumps({'stage': a.stage, 'status': report['status'],
                          'source_sha256': report['source_sha256'], 'system_host': True}))
    except Exception as error:
        report['last_error'] = str(error)
        save()
        raise


if __name__ == '__main__':
    main()

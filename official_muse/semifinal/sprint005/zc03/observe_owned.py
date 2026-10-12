#!/usr/bin/env python3
"""Bounded passive PID sampling. Never opens GUI, services, profile or process arguments."""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import time


def read_pid(pid):
    result = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'lstart=',
                             '-o', '%cpu=', '-o', 'rss='], capture_output=True, text=True, timeout=3)
    if result.returncode or not result.stdout.strip():
        return None
    fields = result.stdout.strip().split()
    assert len(fields) == 7
    # macOS ps comm is kernel-truncated even with -ww. Use the actual SDK-defined
    # proc_pidpath ABI for the executable, without reading argv or profile paths.
    library = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    buffer = ctypes.create_string_buffer(4096)  # PROC_PIDPATHINFO_MAXSIZE
    if library.proc_pidpath(pid, buffer, len(buffer)) <= 0:
        raise RuntimeError('Cannot verify owner executable with proc_pidpath')
    return dict(executable=buffer.value.decode('utf-8'), started=' '.join(fields[:5]),
                 cpu_percent_ps=float(fields[-2]), rss_kib=int(fields[-1]))


def summarize(rows):
    assert rows and all(r['rss_kib'] >= 0 and r['cpu_percent_ps'] >= 0 for r in rows)
    rss = [r['rss_kib'] for r in rows]
    return dict(samples=len(rows), observed_peak_rss_kib=max(rss), median_rss_kib=statistics.median(rss),
                endpoint_rss_delta_kib=rss[-1]-rss[0],
                observed_peak_cpu_percent_ps=max(r['cpu_percent_ps'] for r in rows),
                sampled_span_seconds=rows[-1]['elapsed_seconds']-rows[0]['elapsed_seconds'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pid', type=int, required=True, help='Explicit owner PID supplied by Root')
    p.add_argument('--executable', type=Path, required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--duration', type=float, default=1800)
    p.add_argument('--interval', type=float, default=5)
    p.add_argument('--deadline', required=True, help='Timezone-aware cutoff; never extends it')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    assert a.pid > 1 and 0 < a.duration <= 3600 and 1 <= a.interval <= 60
    assert a.duration / a.interval <= 720 and not a.out.exists()
    deadline = datetime.fromisoformat(a.deadline)
    assert deadline.tzinfo is not None
    executable = a.executable.resolve(strict=True)
    assert hashlib.sha256(executable.read_bytes()).hexdigest() == a.sha256
    owner = read_pid(a.pid)
    assert owner and Path(owner['executable']).resolve() == executable, 'Owner executable differs'
    rows = []
    started = time.monotonic()
    status = 'OBSERVED_NOT_FUNCTIONAL_SOAK'
    observation_error = None
    while time.monotonic()-started <= a.duration and datetime.now(timezone.utc) < deadline:
        try:
            current = read_pid(a.pid)
        except (RuntimeError, subprocess.TimeoutExpired, AssertionError) as error:
            status = 'OWNER_UNVERIFIABLE'
            observation_error = type(error).__name__
            break
        if not current:
            status = 'OWNER_EXITED'
            break
        if current['started'] != owner['started'] or Path(current['executable']).resolve() != executable:
            status = 'OWNER_CHANGED'
            break
        rows.append(dict(elapsed_seconds=time.monotonic()-started,
                         cpu_percent_ps=current['cpu_percent_ps'], rss_kib=current['rss_kib']))
        remaining = min(a.duration-(time.monotonic()-started),
                        (deadline-datetime.now(timezone.utc)).total_seconds())
        if remaining <= 0:
            break
        time.sleep(min(a.interval, remaining))
    if datetime.now(timezone.utc) >= deadline:
        status = 'DEADLINE_REACHED'
    report = dict(status=status, owner_pid=a.pid, executable=str(executable), binary_sha256=a.sha256,
                  observation_error=observation_error,
                  summary=summarize(rows) if rows else None, rows=rows,
                  boundary='Passive ps samples of one explicit owned PID. No input, HTTP, service call, profile access, approval, signal or restart. Sampled CPU is ps average; sampled maxima are not absolute peaks. This is not business stability or leak-free proof.')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'owner_pid', 'summary']}))
    return 0 if status == 'OBSERVED_NOT_FUNCTIONAL_SOAK' and rows else 1


if __name__ == '__main__':
    raise SystemExit(main())

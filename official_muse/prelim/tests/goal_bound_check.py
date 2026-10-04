"""Pure preflight for the frozen Goal summary entry; no PaidGuard or private data read."""
import hashlib
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'official_muse/prelim/tests'))
from ai_paid_guard import PaidPause, request_bounds

def goal_input_bound_check(candidate, host_source, contract, entry):
    """Check public artifacts and return Host-admitted prompt bounds before Goal UI click.

    Caller retains the existing PaidGuard profile whitelist, shared cost history,
    running Host binding, and exclusive synthetic Goal summary dispatch.
    """
    try:
        if (entry != 'goal-suggestion'
                or contract['kind'] != 'REVIEWED_GOAL_SUMMARY_NON_MESSAGES_INPUT_BOUND_CONTRACT'
                or contract['review_status'] != 'REVIEWED_ADMITTED_INPUT_BOUNDS_WITH_DECLARED_PRECONDITIONS'
                or contract['existing_chat_input_bound_check_compatible'] is not False):
            raise ValueError()
        candidate = Path(candidate).resolve()
        if candidate != (ROOT/contract['candidate_relative_path']).resolve():
            raise ValueError()
        sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        source_path = candidate/'bundle/main.splash'
        if sha(source_path) != contract['artifact_source_sha256']:
            raise ValueError()
        source = source_path.read_text()
        for name, digest in contract['app_function_sha256'].items():
            start = source.index('fn '+name+'(')
            end = re.search(r'^fn ', source[start+3:], re.M)
            block = source[start:start+3+end.start()] if end else source[start:]
            if hashlib.sha256(block.encode()).hexdigest() != digest:
                raise ValueError()
        for name, digest in contract['host_file_sha256'].items():
            if sha(Path(host_source)/name) != digest:
                raise ValueError()
        if sha(ROOT/contract['host_binary_relative_path']) != contract['observed_host_binary_sha256']:
            raise ValueError()
        if sha(candidate/'candidate.json') != contract['controller_candidate_metadata_sha256']:
            raise ValueError()
        if sha(ROOT/'official_muse/prelim/tests/ai_paid_guard.py') != contract['paid_guard_sha256_reviewed']:
            raise ValueError()
        length = contract['sdk_length_semantics_source']
        if sha(ROOT/length['relative_path']) != length['sha256']:
            raise ValueError()
        if any((candidate/'private/apps/.host'/n).exists() for n in ['mail','calendar']):
            raise ValueError()
        bounds = contract['reviewed_bounds']
        if (bounds['original_rounded_prompt_text_upper'] != 46080
                or bounds['repair_prompt_text_upper'] != 178176
                or bounds['fixed_goal_schema']['properties']['summary'] != {'type':'string','maxLength':45}):
            raise ValueError()
        result = request_bounds(46080)
        if result['repair_input_byte_upper_bound'] != 178176:
            raise ValueError()
        return {**result, 'checked_before_send':True,
                'entry':'goal-suggestion', 'request_branch':'input; messages absent; app system=None',
                'bound_kind':'HOST_ADMITTED_PROMPT_TEXT_BYTES_NOT_CHAT_PROJECTION',
                'attempts_max_if_existing_single_provider_whitelist_preserved':2,
                'profile_or_ledger_verified_here':False,
                'billing_output_token_cap_proved':False,
                'basis':'Host Request::check caps task/input/schema before provider access; fixed summary schema bounds repair error paths.'}
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        raise PaidPause('Frozen Goal nonmessages source/scope contract differs; stop before payment') from None

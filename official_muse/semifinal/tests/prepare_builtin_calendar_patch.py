"""Minimal reviewable RC2 Calendar patch; writes only the isolated test copy."""
import difflib
import hashlib
import json
from pathlib import Path

BASE_LIB = 'e046649209692d79364e2d2443eae4aad39400a1cbe6c7cd07c6e7f6814f0f3c'


def prepare(sdk, out):
    root = out/'calendar'
    original = root/'src/lib.rs'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == BASE_LIB, 'Review against the exact RC2 baseline first'
    files = {path: path.read_text() for path in (original, root/'src/ui.rs')}
    source = files[original]
    old = '''    let mut events: Vec<Event> = std::fs::read(store_path(host_dir))
        .ok()
        .and_then(|b| serde_json::from_slice(&b).ok())
        .unwrap_or_default();
    events.sort_by_cached_key(|e| (e.local_stamp(false), e.id.clone()));
    events
}'''
    new = '''    // Compatibility for existing callers; all tool and UI operations use
    // the fallible reader below and never treat an unreadable store as empty.
    load_checked(host_dir).unwrap_or_default()
}

fn load_checked(host_dir: &Path) -> Result<Vec<Event>, String> {
    let bytes = match std::fs::read(store_path(host_dir)) {
        Ok(bytes) => bytes,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
        Err(error) => return Err(format!("Calendar cannot read its events: {error}")),
    };
    let mut events: Vec<Event> = serde_json::from_slice(&bytes)
        .map_err(|_| "Calendar events are unreadable. Keep the original file and repair it before editing.".to_string())?;
    events.sort_by_cached_key(|e| (e.local_stamp(false), e.id.clone()));
    Ok(events)
}'''
    assert source.count(old) == 1
    source = source.replace(old,new)
    # All service call sites return Result; unit-test compatibility calls stay.
    boundary = source.index('#[cfg(test)]')
    source = source[:boundary].replace('load(host_dir)', 'load_checked(host_dir)?') + source[boundary:]
    readback = '''        "get_event" => {
            let id = bounded(text(args, "id"), 64, "An event id")?;
            let request_id = bounded(text(args, "request_id"), 160, "A request id")?;
            if (id.is_empty() && request_id.is_empty()) || (!id.is_empty() && !request_id.is_empty()) {
                return Err("Supply exactly one event id or request_id for precise readback.".into());
            }
            let matches: Vec<Event> = load_checked(host_dir)?.into_iter()
                .filter(|event| if id.is_empty() { event.request_id == request_id } else { event.id == id }).collect();
            if matches.len() > 1 { return Err("Calendar event identity is ambiguous. Keep the records and reconcile them.".into()); }
            Ok(json!({"found": !matches.is_empty(), "event": matches.first()}))
        },
'''
    source = source.replace('        "events" => {', readback+'        "events" => {',1)
    source += '\n#[cfg(test)]\nmod reconciliation_tests {\n' + Path(__file__).with_name('builtin_calendar_patch_tests.rs').read_text() + '\n}\n'
    original.write_text(source)
    ui = root/'src/ui.rs'
    boundary = files[ui].index('#[cfg(test)]')
    ui.write_text(files[ui][:boundary].replace('load(host_dir)', 'load_checked(host_dir)?')+files[ui][boundary:])
    tools_path = sdk/'apps/calendar/bundle/tools.json'
    before = tools_path.read_text(); tools = json.loads(before)
    items = tools['tools']
    for tool in items:
        if tool['name'] in ('calendar.update_event','calendar.remove_event'):
            # Official supervision requires destructive/outward risk to ask.
            # Editing existing data is explicitly person-confirmed in Muse;
            # confirm:'host' alone does not make an act tool supervised.
            tool.update(shareable=True, risk='destructive', confirm='host', auto_approvable=False)
        if tool['name']=='calendar.remove_event':
            tool['input_schema']['properties']['expected']={'type':'object'}
            tool['input_schema']['required'].append('expected')
    items.insert(1, {'name':'calendar.get_event',
        'description':'Exact durable readback by one event id or stable request_id, including authoritative absence. Refuses unreadable or ambiguous records. This is the same built-in Calendar store.',
        'input_schema':{'type':'object','properties':{'id':{'type':'string','minLength':1,'maxLength':64},
            'request_id':{'type':'string','minLength':1,'maxLength':160}},'additionalProperties':False},
        'output_schema':{'type':'object','properties':{'found':{'type':'boolean'},'event':{'type':['object','null']}},'required':['found','event']},
        'risk':'read','background':True,'implemented_by':'host-service','shareable':True})
    patched_tools = json.dumps(tools,ensure_ascii=False,indent=2)+'\n'
    (out/'bundle/tools.json').write_text(patched_tools)
    patch = ''
    for path, text in files.items():
        name = 'apps/calendar/host-service/'+str(path.relative_to(root))
        patch += ''.join(difflib.unified_diff(text.splitlines(True),path.read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    patch += ''.join(difflib.unified_diff(before.splitlines(True),patched_tools.splitlines(True),fromfile='a/apps/calendar/bundle/tools.json',tofile='b/apps/calendar/bundle/tools.json'))
    (out/'calendar-review.patch').write_text(patch)
    return hashlib.sha256(patch.encode()).hexdigest()

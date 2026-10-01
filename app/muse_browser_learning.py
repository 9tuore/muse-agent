"""Map live, public browser search controls into the generic RecipeStore adapter."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

from muse_browser import EDGE_BUNDLE_ID, IsolatedEdgeSession
from muse_capabilities import _public_url


SEARCH_PAGE = "https://www.python.org/search/"


class BrowserSearchLearningAdapter:
    """One isolated Edge tab; the observed DOM supplies the recipe controls."""

    def __init__(self, session: IsolatedEdgeSession):
        self.session = session
        self.last_query: str | None = None

    def _controls(self) -> list[dict]:
        expression = """JSON.stringify(Array.from(document.querySelectorAll('input,button')).slice(0,50)
          .map((e,index)=>{let r=e.getBoundingClientRect();let visible=r.width>0&&r.height>0;
            let label=(e.getAttribute('aria-label')||e.getAttribute('placeholder')||e.getAttribute('title')||'').trim();
            let role='',name='';
            if(e.tagName==='INPUT'&&e.type==='search'){role='AXSearchField';name=label;}
            if(e.tagName==='BUTTON'&&e.type==='submit'&&/search/i.test(label)){role='AXButton';name='Search';}
            return {index,role,name,value:e.value||'',enabled:visible&&!e.disabled,
                    x:r.x+r.width/2,y:r.y+r.height/2,width:r.width,height:r.height};
          }).filter(x=>x.role&&x.name&&x.enabled))"""
        value = self.session._evaluate(expression)
        controls = json.loads(value) if isinstance(value, str) else []
        if not isinstance(controls, list) or len(controls) > 50:
            raise ValueError("browser_controls_invalid")
        return controls

    def snapshot(self, bundle_id: str) -> dict:
        if bundle_id != EDGE_BUNDLE_ID:
            raise ValueError("browser_bundle_mismatch")
        url = self.session._evaluate("location.href")
        canonical, host, _ = _public_url(url, ["python.org"])
        if host != "www.python.org" or urlsplit(canonical).path != "/search/":
            raise ValueError("browser_search_page_changed")
        title = self.session._evaluate("document.title")
        if not isinstance(title, str) or not 1 <= len(title) <= 240:
            raise ValueError("browser_title_invalid")
        controls = self._controls()
        elements = [{"role": item["role"], "name": item["name"], "enabled": item["enabled"],
                     "actions": ["set_value"] if item["role"] == "AXSearchField" else ["press"],
                     "value": item["value"] if item["role"] == "AXSearchField" else "",
                     "window_title": title} for item in controls]
        return {"bundle_id": bundle_id, "observed_at": datetime.now(timezone.utc).isoformat(), "elements": elements,
                "source": "isolated_edge_dom"}

    def act(self, bundle_id: str, selector: dict, action: str, value: str | None) -> dict:
        if bundle_id != EDGE_BUNDLE_ID or not isinstance(selector, dict):
            return {"status": "BLOCKED", "error": "browser_bundle_mismatch"}
        try:
            snapshot = self.snapshot(bundle_id)
            if not snapshot["elements"] or selector.get("window_title") != snapshot["elements"][0]["window_title"]:
                return {"status": "BLOCKED", "error": "browser_window_changed"}
            matches = [item for item in self._controls() if item["role"] == selector.get("role") and
                       item["name"] == selector.get("name")]
            if len(matches) != 1:
                return {"status": "BLOCKED", "error": "browser_control_ambiguous"}
            control = matches[0]
            if action == "set_value" and control["role"] == "AXSearchField":
                if (not isinstance(value, str) or not 2 <= len(value.strip()) <= 160 or
                        re.search(r"[\r\n\x00@\\]", value)):
                    return {"status": "BLOCKED", "error": "browser_query_invalid"}
                expression = ("(()=>{let e=Array.from(document.querySelectorAll('input,button'))["
                              + str(control["index"]) + "];if(!e||e.tagName!=='INPUT'||e.type!=='search')return false;"
                              "e.value=" + json.dumps(value) + ";e.dispatchEvent(new Event('input',{bubbles:true}));"
                              "e.dispatchEvent(new Event('change',{bubbles:true}));return e.value==="
                              + json.dumps(value) + ";})()")
                if self.session._evaluate(expression) is not True:
                    return {"status": "BLOCKED", "error": "browser_query_not_set"}
                self.last_query = value
                return {"status": "COMPLETED", "transport": "cdp_dom_value", "query": value}
            if action == "press" and control["role"] == "AXButton" and control["name"] == "Search":
                if self.last_query is None or not 0 <= control["x"] <= 5000 or not 0 <= control["y"] <= 5000:
                    return {"status": "BLOCKED", "error": "browser_press_precondition_failed"}
                if self.session.cdp is None:
                    return {"status": "BLOCKED", "error": "browser_not_started"}
                for event_type in ("mousePressed", "mouseReleased"):
                    self.session.cdp.call("Input.dispatchMouseEvent", {"type": event_type,
                                                                         "x": control["x"], "y": control["y"],
                                                                         "button": "left", "clickCount": 1})
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline:
                    location = self.session._evaluate("location.href")
                    parsed = urlsplit(location)
                    if (parsed.hostname == "www.python.org" and parsed.path == "/search/" and
                            parse_qs(parsed.query).get("q") == [self.last_query]):
                        self.session._loaded()
                        return {"status": "COMPLETED", "transport": "cdp_mouse",
                                "search_page": location, "query": self.last_query}
                    time.sleep(0.2)
                return {"status": "BLOCKED", "error": "browser_search_did_not_navigate"}
        except (ValueError, TypeError, KeyError) as exc:
            return {"status": "BLOCKED", "error": str(exc)[:160]}
        return {"status": "BLOCKED", "error": "browser_action_not_reviewed"}

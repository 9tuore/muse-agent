"""Read-only audit of a synthetic browser recipe Goal's persisted authority chain."""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def digest(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def only_row(path, query, params=()):
    with sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = [dict(row) for row in db.execute(query, params)]
    if len(rows) != 1:
        raise AssertionError("expected_one_row:" + query)
    return rows[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--negative-evidence", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    raw = args.evidence.read_bytes()
    observed = json.loads(raw)
    workspace = Path(observed["workspace"]).resolve(strict=True)
    goal_id = observed["draft"]["goal_id"]
    goal = only_row(workspace / "memory.sqlite3",
                    "SELECT goal_id,revision,status,approval_id,approval_digest,run_count "
                    "FROM muse_goals WHERE goal_id=?", (goal_id,))
    plan = only_row(workspace / "memory.sqlite3",
                    "SELECT goal_id,revision,spec_json,digest FROM muse_goal_revisions "
                    "WHERE goal_id=? AND revision=?", (goal_id, goal["revision"]))
    approval = only_row(workspace / "memory.sqlite3",
                        "SELECT goal_id,revision,approval_id,digest,scope_json FROM muse_goal_approvals "
                        "WHERE goal_id=? AND revision=?", (goal_id, goal["revision"]))
    run = only_row(workspace / "memory.sqlite3",
                   "SELECT goal_id,revision,approval_id,status,result_json FROM muse_goal_runs "
                   "WHERE goal_id=? AND revision=?", (goal_id, goal["revision"]))
    spec = json.loads(plan["spec_json"])
    planned = spec["steps"][0]["args"]
    recipe = only_row(workspace / ".muse-app-recipes.sqlite3",
                      "SELECT id,revision,digest,body,enabled,approval_id FROM recipes "
                      "WHERE id=? AND revision=?",
                      (planned["recipe_id"], planned["recipe_revision"]))
    binding = only_row(workspace / ".muse-browser-recipe-bindings.sqlite3",
                       "SELECT goal_id,goal_revision,plan_digest,approval_id,recipe_id,"
                       "recipe_revision,recipe_digest,query,window_title FROM bindings "
                       "WHERE goal_id=? AND goal_revision=?", (goal_id, goal["revision"]))
    plan_digest = digest(spec)
    recipe_digest = digest(json.loads(recipe["body"]))
    result = json.loads(run["result_json"])
    browser_receipt = result["receipts"][0]
    sources = browser_receipt.get("sources", browser_receipt["output"].get("sources", []))
    artifact = Path(observed["artifact_path"]).resolve(strict=True)
    artifact.relative_to(workspace)
    artifact_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    checks = {
        "synthetic_approval_labeled": observed["approval_type"] == "synthetic_host_decision_fixture",
        "wrong_digest_rejected": observed["wrong_digest_decision"]["status"] == "REJECTED",
        "plan_digest_matches": observed["draft"]["plan_digest"] == plan["digest"] ==
                               approval["digest"] == goal["approval_digest"] == plan_digest,
        "approval_scope_matches": json.loads(approval["scope_json"]) ==
                                  {key: spec[key] for key in ("permissions", "budget", "deadline", "verification")},
        "recipe_digest_matches": observed["prepare"]["browser_recipe"]["recipe_digest"] ==
                                 planned["recipe_digest"] == recipe["digest"] == recipe_digest,
        "binding_matches": all((binding["goal_id"] == goal["goal_id"] == run["goal_id"],
                                binding["goal_revision"] == goal["revision"] == run["revision"],
                                binding["plan_digest"] == plan_digest,
                                binding["approval_id"] == goal["approval_id"] ==
                                approval["approval_id"] == run["approval_id"],
                                binding["recipe_id"] == recipe["id"] == planned["recipe_id"],
                                binding["recipe_revision"] == recipe["revision"] == planned["recipe_revision"],
                                binding["recipe_digest"] == recipe_digest,
                                binding["query"] == planned["query"],
                                binding["window_title"] == planned["window_title"])),
        "observed_approval_matches": observed["approved"]["approval_id"] ==
                                     goal["approval_id"] == approval["approval_id"] and
                                     observed["approved"]["recipe_binding"]["status"] == "ENABLED",
        "recipe_enabled": recipe["enabled"] == 1,
        "run_completed": goal["status"] == run["status"] == "completed" and
                         goal["run_count"] == 1 and result["status"] == "COMPLETED",
        "learned_browser_used": browser_receipt["verification"].get("learned_search_recipe") is True,
        "three_sources": len(sources) == 3 and len({item["source_url"] for item in sources}) == 3
                         and all(item["source_url"].startswith("https://www.python.org/")
                                 and item["click_transport"] == "cdp_mouse"
                                 and len(item["content_sha256"]) == 64 for item in sources),
        "artifact_readback_matches": artifact_digest == result["receipts"][-1]["verification"]["sha256"] ==
                                     observed["artifact_sha256"],
    }
    if args.negative_evidence:
        negative = json.loads(args.negative_evidence.read_text(encoding="utf-8"))
        checks["recipe_revoked_after_run"] = (
            recipe["enabled"] == 0 and
            negative["workspace"] == observed["workspace"] and
            negative["old_recipe_revision"] == recipe["revision"] and
            negative["old_recipe_digest"] == recipe_digest and
            negative["revoked"]["status"] == "DISABLED")
        del checks["recipe_enabled"]
    if args.report:
        report_bytes = args.report.read_bytes()
        checks["report_copy_matches"] = hashlib.sha256(report_bytes).hexdigest() == artifact_digest
        checks["report_sources_match_receipts"] = all(
            all(str(item[key]).encode("utf-8") in report_bytes
                for key in ("source_url", "retrieved_at", "content_sha256"))
            for item in sources)
    report = {"status": "PASS" if all(checks.values()) else "FAIL",
              "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
              "workspace": str(workspace), "checks": checks,
              "plan_digest": plan_digest, "recipe_digest": recipe_digest,
              "artifact_sha256": artifact_digest}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

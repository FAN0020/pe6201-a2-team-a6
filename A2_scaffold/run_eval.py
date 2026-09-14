#!/usr/bin/env python3
"""Run the D4/D5 evaluation harness and write an auditable result artifact.

The committed default remains the full offline scripted evaluation. Live runs
require both ``--backend live`` and an explicit ``--model`` so an accidental
command cannot spend credit on the scaffold's placeholder model.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import config
from backends import SCRIPTS
from harness import (load_cases, load_key, report, run_set,
                     summarise_cases)


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent


def _parser():
    parser = argparse.ArgumentParser(
        description="Run the reproducible PE6201 A2 evaluation harness.")
    parser.add_argument("case_id", nargs="?", help="run one case verbosely")
    parser.add_argument("--all", action="store_true",
                        help="compatibility flag; the full set is already the default")
    parser.add_argument("--prompt", action="store_true",
                        help="print the exact v2 system prompt and stop")
    parser.add_argument("--backend", choices=("scripted", "live"),
                        default="scripted")
    parser.add_argument("--model",
                        help="OpenRouter model id; required for a live run")
    parser.add_argument("--prompt-version", choices=("v2",), default="v2")
    parser.add_argument("--tool-version", default="main-tool-contract")
    parser.add_argument("--freeze-sha",
                        help="frozen source commit shared by all battery runners")
    parser.add_argument("--output",
                        help="result JSON path; relative paths use repository root")
    parser.add_argument("--no-write", action="store_true",
                        help="run and report without writing a result artifact")
    parser.add_argument("--verbose", action="store_true",
                        help="print every tool-calling turn for a full set")
    return parser


def _git(*args):
    try:
        completed = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def _git_metadata(freeze_sha=None):
    head = _git("rev-parse", "HEAD")
    branch = _git("branch", "--show-current")
    status = _git("status", "--porcelain", "--untracked-files=normal")
    if freeze_sha:
        resolved = _git("rev-parse", "--verify", freeze_sha + "^{commit}")
        if resolved is None:
            raise SystemExit("--freeze-sha does not resolve to a local commit")
        freeze_sha = resolved
    return {
        "freeze_commit_sha": freeze_sha or head,
        "source_commit_sha": head,
        "source_branch": branch,
        "working_tree_clean_before_run": status == "" if status is not None else None,
    }


def _safe_name(value):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "model"


def _output_path(args):
    if args.output:
        path = Path(args.output)
        return path if path.is_absolute() else REPO_ROOT / path
    if args.backend == "scripted":
        return REPO_ROOT / "artifacts" / "results_scripted.json"
    return (REPO_ROOT / "artifacts" / "live_results" /
            ("%s_%s.json" % (_safe_name(args.model), args.prompt_version)))


def _artifact(results, judgement_queue, summary, args, git_metadata):
    case_ids = load_cases()
    key = load_key()
    negative_ids = [case_id for case_id in case_ids
                    if key[case_id].get("expected_decision") != "book"]
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run": {
            "problem": config.PROBLEM,
            "backend": args.backend,
            "model_id": args.model if args.backend == "live" else None,
            "prompt_version": args.prompt_version,
            "tool_version": args.tool_version,
            "freeze_commit_sha": git_metadata["freeze_commit_sha"],
            "source_commit_sha": git_metadata["source_commit_sha"],
            "source_branch": git_metadata["source_branch"],
            "working_tree_clean_before_run":
                git_metadata["working_tree_clean_before_run"],
            "token_measurement": (
                "api_reported" if args.backend == "live"
                else "scripted_estimate_not_a_live_measurement"),
            "trial_policy": {
                "ordinary": 1,
                "negative": 3,
                "negative_definition": "expected decision is not book",
            },
        },
        "evaluation_set": {
            "case_count": len(case_ids),
            "negative_case_count": len(negative_ids),
            "case_ids": case_ids,
            "negative_case_ids": negative_ids,
        },
        "summary": summary,
        "case_results": summarise_cases(results),
        "trial_results": results,
        "judgement_queue": judgement_queue,
    }


def _run_one(case_id):
    results, queue = run_set(
        [case_id], trials_for=lambda _case_id: 1, verbose=True)
    if not results:
        return 1
    result = results[0]
    print("\n  DECISION RECORD")
    print(json.dumps(result["record"], indent=2, ensure_ascii=False))
    print("\n  CODE CHECK   %s" % ("PASS" if result["passed"] else "FAIL"))
    for failure in result["fails"]:
        print("      %s" % failure)
    if queue:
        print("\n  JUDGEMENT CHECK - pending")
        for item in queue[0]["must_record"]:
            print("      [ ] %s" % item)
    return 0 if result["passed"] else 1


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if args.backend == "live" and not args.model:
        parser.error("--model is required when --backend live")
    if args.backend == "scripted" and args.model:
        parser.error("--model is only valid when --backend live")

    config.BACKEND = args.backend
    if args.model:
        config.MODEL = args.model
    if args.backend == "live" and not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit(
            "OPENROUTER_API_KEY is required for live runs. "
            "The scripted default needs no key.")

    print("\n" + config.summary())
    print("data: %s" % config.data_root())

    if args.prompt:
        import prompt
        print()
        prompt.audit()
        return 0

    if args.case_id:
        return _run_one(args.case_id)

    case_ids = load_cases()
    if args.backend == "scripted":
        missing_scripts = [case_id for case_id in case_ids
                           if case_id not in SCRIPTS]
        if missing_scripts:
            print("\n  ERROR: %d submitted case(s) have no scripted replay:"
                  % len(missing_scripts))
            for case_id in missing_scripts:
                print("    %s" % case_id)
            print("  D5(a) requires the committed default to cover the whole set.")
            return 2

    git_metadata = _git_metadata(args.freeze_sha)
    print("\n  Running all %d submitted cases (%s backend)."
          % (len(case_ids), args.backend))
    results, judgement_queue = run_set(case_ids, verbose=args.verbose)
    summary = report(results)

    if args.no_write:
        return 0 if summary["passed"] == summary["trials"] else 1

    output = _output_path(args)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = _artifact(results, judgement_queue, summary, args, git_metadata)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
        handle.write("\n")
    print("  Wrote %s" % output.relative_to(REPO_ROOT))
    print("  Code pass rates and judgement status are reported separately.")
    return 0 if summary["passed"] == summary["trials"] else 1


if __name__ == "__main__":
    sys.exit(main())

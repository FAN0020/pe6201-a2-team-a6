"""Validate and summarize the saved D2(c) sequential/grouped comparison."""

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GROUPED = REPO_ROOT / "artifacts" / "grouped_REF-5602.json"
DEFAULT_SEQUENTIAL = REPO_ROOT / "artifacts" / "sequential_REF-5602.json"


def load_record(path):
    """Load one JSON record and fail with a useful file-specific message."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Result file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def require(condition, message):
    """Stop the comparison when an experimental control is violated."""
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def call_details(record):
    """Return fields that must remain identical across execution modes.

    Turn numbers and elapsed seconds are deliberately excluded: turns are the
    independent variable, and local timings naturally vary between runs.
    """
    return [
        {
            "tool": entry.get("tool"),
            "args": entry.get("args"),
            "observation": entry.get("observation"),
            "error": entry.get("error"),
        }
        for entry in record.get("tool_trace", [])
    ]


def percentage_reduction(sequential_value, grouped_value):
    """Calculate reduction relative to the sequential baseline."""
    require(sequential_value > 0, "sequential baseline must be greater than zero")
    return (sequential_value - grouped_value) / sequential_value * 100


def validate(grouped, sequential):
    """Check that grouping changes turn allocation without changing the work."""
    require(grouped.get("execution_mode") == "grouped",
            "grouped file has the wrong execution_mode")
    require(sequential.get("execution_mode") == "sequential",
            "sequential file has the wrong execution_mode")
    require(grouped.get("case_id") == sequential.get("case_id"),
            "the files describe different cases")
    require(grouped.get("backend") == sequential.get("backend") == "scripted",
            "this comparison expects two scripted runs")
    require(grouped.get("measurement_type") == "scripted_estimate" and
            sequential.get("measurement_type") == "scripted_estimate",
            "token and cost values must be labelled scripted_estimate")

    grouped_calls = call_details(grouped)
    sequential_calls = call_details(sequential)
    require(grouped_calls == sequential_calls,
            "tool names, arguments, observations, or errors differ")
    require(len(grouped_calls) > 0, "tool_trace is empty")
    require(all(entry["error"] is None for entry in grouped_calls),
            "at least one tool call contains an error")

    require(grouped.get("decision") == sequential.get("decision"),
            "final decisions differ")
    require(grouped.get("booked") == sequential.get("booked"),
            "final booking details differ")
    require(grouped.get("stopped_by") is None and
            sequential.get("stopped_by") is None,
            "at least one run stopped early")
    require(grouped.get("turns", 0) < sequential.get("turns", 0),
            "grouped mode did not reduce the turn count")


def print_summary(grouped, sequential):
    """Print the checked results and clearly label simulated estimates."""
    grouped_total = grouped["tokens_in"] + grouped["tokens_out"]
    sequential_total = sequential["tokens_in"] + sequential["tokens_out"]

    print("PASS: D2(c) saved-record comparison")
    print(f"Case:                  {grouped['case_id']}")
    print(f"Tool calls:            {len(grouped['tool_trace'])} in both modes")
    print(f"Sequential turns:      {sequential['turns']}")
    print(f"Grouped turns:         {grouped['turns']}")
    print(
        "Turn reduction:         "
        f"{percentage_reduction(sequential['turns'], grouped['turns']):.1f}%"
    )
    print(f"Decision:              {grouped['decision']} in both modes")
    print(f"Booking:               {grouped.get('booked')} in both modes")
    print(f"Sequential tokens:     {sequential_total:,} (scripted estimate)")
    print(f"Grouped tokens:        {grouped_total:,} (scripted estimate)")
    print(
        "Token reduction:        "
        f"{percentage_reduction(sequential_total, grouped_total):.1f}% "
        "(scripted estimate)"
    )
    print(f"Sequential cost:       ${sequential['cost_usd']:.6f} (scripted estimate)")
    print(f"Grouped cost:          ${grouped['cost_usd']:.6f} (scripted estimate)")


def parse_args():
    """Allow the same checker to compare refreshed or renamed result files."""
    parser = argparse.ArgumentParser(
        description="Validate two saved D2(c) scripted execution records."
    )
    parser.add_argument("--grouped", type=Path, default=DEFAULT_GROUPED)
    parser.add_argument("--sequential", type=Path, default=DEFAULT_SEQUENTIAL)
    return parser.parse_args()


def main():
    """Load, validate, and summarize the selected result pair."""
    args = parse_args()
    grouped = load_record(args.grouped)
    sequential = load_record(args.sequential)
    validate(grouped, sequential)
    print_summary(grouped, sequential)


if __name__ == "__main__":
    main()

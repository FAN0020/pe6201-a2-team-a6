# Fan Yupei D4/D5 Handoff

Repository: `https://github.com/FAN0020/pe6201-a2-team-a6`

Branch: `feature/evaluation`

Frozen experiment commit:
`e36bb1b2fcad625ed944e7df863165d95c0ef53f`

Upstream `main` used as the base:
`9a73ba90fedf5a848b46face38607b8e16eb0c3a`

## What is complete

- Eight Fan Yupei cases: `REF-6401` through `REF-6408`.
- Integrated Problem B set: 30 cases, including 14 negative cases.
- Trial policy: one ordinary trial and three negative trials, producing 58
  trials per model/descriptor arm.
- Full deterministic scripted coverage, exact outcome grading, gated-booking
  trace checks, judgement rubric and source-hashed judge sidecar.
- Freeze manifest containing case IDs, file hashes, prompt/descriptor hashes
  and reproducible commands.
- OpenAI GPT-5.4 live descriptor-v1 run and same-freeze v2 control.
- JSON, CSV and Markdown aggregation, defect analysis, report-ready findings,
  cost handoff and demo runbook.

## Result summary

| Run | Code pass | Negative pass | Judgement | API tokens in/out | Provider cost | Errors |
|---|---:|---:|---:|---:|---:|---:|
| Scripted v2 | 58/58 (100.0%) | 42/42 (100.0%) | 3/3 | estimates only | estimate only | 0 |
| GPT-5.4 descriptor v1 | 20/58 (34.5%) | 20/42 (47.6%) | 0/3 | 234,496 / 9,653 | US$0.731035 | 28 |
| GPT-5.4 descriptor v2 | 25/58 (43.1%) | 21/42 (50.0%) | 0/3 | 287,085 / 10,898 | US$0.881183 | 22 |

V2 improved code pass rate by 8.6 percentage points but used 53,834 more
tokens and cost US$0.150148 more. The dominant live failure was strict response
formatting: plain prose or concatenated/invalid JSON. All failures and raw model
responses are retained; there were no selective retries.

## Files in this package

- `results.json`: final live GPT-5.4 prompt-v2/descriptor-v2 result. This is the
  exact generic filename requested for handoff.
- `results_descriptor_v1.json`: Fan Yupei's required descriptor-v1 result.
- `judgement_results.json`: independent different-family judgement evidence.
- `live_battery_summary.csv`: report-ready metrics for both compatible runs.
- `live_cost_handoff.csv`: measured D6 inputs and price provenance.
- `freeze_manifest.json`: exact freeze and reproduction metadata.
- `SHA256SUMS`: integrity hashes for every packaged evidence file.

The canonical originals remain under `artifacts/`; these package copies must
not be edited independently.

## Verification

From the repository root:

```bash
python3 A2_reference_data/check_my_data.py
python3 -m unittest discover -s tests -v
python3 A2_scaffold/run_eval.py --no-write
python3 analysis/aggregate_live_results.py
cd handoff/fan_yupei && shasum -a 256 -c SHA256SUMS
```

Expected outcomes: fixture validation passes, 52 tests pass, scripted code
checks pass 58/58, and both live result rows are reported compatible.

## Remaining team actions

1. Add the four other members' final prompt-v2 result JSON files under
   `artifacts/live_results/`, all from the same frozen commit and exact case
   list.
2. Re-run `analysis/aggregate_live_results.py` and use only rows marked
   compatible.
3. Give `live_cost_handoff.csv` plus the other models' measured rows and agreed
   fallback/fixed-cost assumptions to the D6 owner.
4. Merge `feature/evaluation` only after review. Do not replace the raw result
   files, change labels after seeing results, or merge directly into `main`
   without the team's normal PR process.
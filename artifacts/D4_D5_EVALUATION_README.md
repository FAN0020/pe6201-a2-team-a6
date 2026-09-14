# D4 and D5 Evaluation Handoff

Owner: Fan Yupei
Branch: `feature/evaluation`

## Completed on this branch

- Added eight labelled Problem B cases, `REF-6401` to `REF-6408`, through the
  fixture generator rather than by editing generated data.
- Preserved every shipped row. The integrated set contains 30 referrals and 30
  labels: 15 shipped, Fan Yupei's eight, Liu Xuanlin's six, and one explicitly
  labelled D4-owner integration case.
- Added deterministic scripted replays for every current Problem B fixture.
  Replay construction reads fixture records and the Appendix A routing order;
  it never reads `expected_outcomes_B.json`.
- Extended the code check to validate the decision, escalation trigger, named
  missing item, exact booked slot, gated-action count and gate result.
- Limited judgement checks to selected prose-evidence cases and kept their
  pending verdicts separate from the code pass rate.
- Added an auditable result schema with commit SHA, prompt and descriptor hashes,
  branch, backend, model id, prompt/tool/descriptor versions, trial policy,
  API-reported token source, price provenance, errors, negative-only performance
  and per-case results.
- Made the committed default run the entire submitted set and fail loudly if a
  case has no scripted replay.

## Current reproducible run

From the repository root:

```bash
python3 A2_reference_data/check_my_data.py
python3 -m unittest discover -s tests -v
python3 A2_scaffold/run_eval.py
```

Integrated freeze-set shape:

| Measure | Value |
|---|---:|
| Cases | 30 |
| Negative cases | 14 |
| Ordinary trials | 16 |
| Negative trials | 42 |
| Total trials | 58 |
| Selected judgement cases | 3 |

Scripted token counts are estimates used only to test instrumentation. They are
explicitly labelled and must not be reported as live measurements.

## Result schema

`artifacts/results_scripted.json` contains:

- `run`: freeze/source commit, branch, backend, model, prompt/tool versions,
  token source and the trial policy;
- `evaluation_set`: all case ids and the negative subset;
- `summary`: overall and negative-only code pass rates, trial counts, turns,
  tokens, cost, cap hits and errors;
- `case_results`: one compact row per case, including check type;
- `trial_results`: full decision records and traces;
- `judgement_queue`: only cases selected for human or independent-model review.

The code pass rate is not relabelled as a combined pass rate while any judgement
verdict remains pending.

## Freeze and live-battery procedure

1. Check out the frozen `feature/evaluation` SHA from
   `artifacts/freeze_manifest.json` in a clean clone.
2. Run the checker and tests. Confirm the set has 30-50 cases, every label is
   present, and every new case has a scripted replay.
3. Freeze a side-branch commit. Every runner checks out that exact SHA; only the
   model id or the controlled descriptor version may differ.
4. Four members of this five-person team run the final v2 prompt on four model
   families spanning at least two price tiers. The fifth job is the controlled
   v1 descriptor pass on the same model used by one v2 runner.
5. Each runner uses an explicit model id and output filename:

   ```bash
   export OPENROUTER_API_KEY="..."
   python3 A2_scaffold/run_eval.py \
     --backend live \
     --model PROVIDER/MODEL \
     --descriptor-version v1 \
     --approve-fixture-bookings \
     --price-input-per-million PRICE \
     --price-output-per-million PRICE \
     --price-source SOURCE \
     --price-date YYYY-MM-DD \
     --freeze-sha COMMIT_SHA \
     --output artifacts/live_results/MEMBER_MODEL_v1.json
   ```

6. Commit each result JSON without changing source files, then aggregate the
   per-model and negative-only tables from those artifacts.

## Controlled descriptor experiment

Wang Chenyu's experiment design was adapted to the shared six-tool contract. The
only v1/v2 variable is the text of the `get_clinic_slots` descriptor; the callable
and every other frozen control remain identical. See
`artifacts/D2B_CONTROLLED_EXPERIMENT.md`.

The current timeline assigns member 4 the descriptor-v1 job, but a valid paired
comparison still requires a v2 result from the same `openai/gpt-5.4` model and
freeze SHA. The integrated team set also contains 14 negatives because Liu's
four negative cases were preserved; this exceeds the brief's recommended 6-10
range and should be reported rather than hidden.

# D4 and D5 Evaluation Handoff

Owner: Fan Yupei
Branch: `feature/evaluation`

## Completed on this branch

- Added eight labelled Problem B cases, `REF-6401` to `REF-6408`, through the
  fixture generator rather than by editing generated data.
- Preserved every shipped row. `check_my_data.py` passes with 23 referrals, 10
  negative cases and 23 labels.
- Added deterministic scripted replays for every current Problem B fixture.
  Replay construction reads fixture records and the Appendix A routing order;
  it never reads `expected_outcomes_B.json`.
- Extended the code check to validate the decision, escalation trigger, named
  missing item, exact booked slot, gated-action count and gate result.
- Limited judgement checks to selected prose-evidence cases and kept their
  pending verdicts separate from the code pass rate.
- Added an auditable result schema with commit SHA, branch, backend, model id,
  prompt and tool versions, trial policy, token source, errors, negative-only
  performance and per-case results.
- Made the committed default run the entire submitted set and fail loudly if a
  case has no scripted replay.

## Current reproducible run

From the repository root:

```bash
python3 A2_reference_data/check_my_data.py
python3 -m unittest discover -s tests -v
python3 A2_scaffold/run_eval.py
```

Current branch-local shape before other members' case branches are merged:

| Measure | Value |
|---|---:|
| Cases | 23 |
| Negative cases | 10 |
| Ordinary trials | 13 |
| Negative trials | 30 |
| Total trials | 43 |
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

1. Merge the final tools/ACI branch and every member's fixture/label branch.
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
     --freeze-sha COMMIT_SHA \
     --output artifacts/live_results/MEMBER_MODEL_v2.json
   ```

6. Commit each result JSON without changing source files, then aggregate the
   per-model and negative-only tables from those artifacts.

## Remaining dependencies before a genuine live result

- The tool/ACI v2 package in `_D2_tools_aci_v3_readme_aligned` has not been
  merged into the team repository. Its five-tool contract is not compatible
  with the current `main` replay arguments and must be integrated deliberately.
- The current timeline assigns member 4 the descriptor-v1 job, but the team
  declaration lists a unique GPT-5.4 model for that member. A valid v1/v2
  comparison requires the v1 job to use the same model as a v2 runner.
- No `OPENROUTER_API_KEY` was available in this workspace, so no live requests
  or measured token/cost claims were made here.
- Other members' evaluation cases are still needed before the team freezes the
  required 30-50 case set.

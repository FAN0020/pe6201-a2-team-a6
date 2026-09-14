# PE6201 A2 Team A-6 Problem B

This repository implements the outpatient referral coordination agent and its
reproducible evidence. The committed default is offline and deterministic.

## Reproduce the scripted evaluation

```bash
python3 A2_reference_data/check_my_data.py
python3 -m unittest discover -s tests -v
python3 A2_scaffold/run_eval.py
```

The final command evaluates every submitted Problem B fixture. Ordinary cases
run once and negative cases run three times. It writes
`artifacts/results_scripted.json`, including the source commit, case and trial
counts, code-check pass rates, negative-only results, turns, tokens, costs,
errors, per-case rows, and the separate judgement queue.

To inspect one case and every tool call:

```bash
python3 A2_scaffold/run_eval.py REF-6401
```

To inspect the exact prompt without spending credit:

```bash
python3 A2_scaffold/run_eval.py --prompt
```

Live evaluation is opt-in and requires an explicit OpenRouter model id:

```bash
export OPENROUTER_API_KEY="..."
python3 A2_scaffold/run_eval.py \
  --backend live \
  --model PROVIDER/MODEL \
  --freeze-sha COMMIT_SHA \
  --output artifacts/live_results/MEMBER_MODEL_v2.json
```

Do not run a live battery until the prompt, tool contract, evaluation set and
freeze commit are agreed. See `artifacts/D4_D5_EVALUATION_README.md` for the
handoff and result schema.

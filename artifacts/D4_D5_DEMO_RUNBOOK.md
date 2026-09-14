# D4/D5 Demo Runbook

## 1. Prove fixture integrity and coverage

```bash
python3 A2_reference_data/check_my_data.py
python3 -m unittest discover -s tests -v
```

Show the 30 referrals, the unchanged shipped-row fingerprints and the test that
every case has a label and scripted replay.

## 2. Show one ordinary case and one negative case

```bash
python3 A2_scaffold/run_eval.py REF-6401
python3 A2_scaffold/run_eval.py REF-5703
```

For the booking, point out the matching `book_slot`, `gate_passed` event and
exact slot check. For the hostile-text case, point out that no slot query or
booking occurs.

## 3. Reproduce the complete scripted run

```bash
python3 A2_scaffold/run_eval.py --freeze-sha COMMIT_SHA
```

Show 30 cases, 58 trials, the negative-only line, turns, errors and the separate
judgement queue. State explicitly that scripted tokens are estimates.

## 4. Demonstrate the controlled descriptor variable

```bash
python3 A2_scaffold/run_eval.py --prompt --descriptor-version v1
python3 A2_scaffold/run_eval.py --prompt --descriptor-version v2
```

Diff the prompts and show that only `get_clinic_slots` changes. Then open the
freeze manifest and live result; identify the matching SHA, model, descriptor,
API-reported tokens, price provenance and error count.

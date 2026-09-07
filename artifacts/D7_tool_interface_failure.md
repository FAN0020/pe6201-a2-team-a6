# D7 second failure: missing urgency-band constraint

This is a separate failure from the existing loop-control example in
`A2_scaffold/demo_loop_failure.py`. It is built as “the working agent, minus
one tool-interface constraint”: `get_clinic_slots` no longer requires the
`band` argument, and the weakened interface silently defaults the query to
`urgent`.

The scripted case is `REF-5602`. `check_referral_criteria` reports
`band=routine`. The working interface therefore filters for routine slots and
books `OPH-C2 / 2026-10-14 11:20`. With the constraint removed, the scripted
agent omits `band`; the permissive tool returns the first urgent slot and the
agent books `OPH-C1 / 2026-09-15 09:40`.

## Reproduction

From `A2_scaffold/`, run:

```text
python3 demo_loop_failure.py
```

No API key or network call is needed; `config.BACKEND` remains `scripted`.

| run | turns | tool calls | tokens | cost | decision | stopped_by |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before: required `band` | 4 | 6 | 21,600 | US$0.00234 | `book` | `None` |
| after: band constraint removed | 4 | 5 | 21,600 | US$0.00234 | `book` | `None` |

The error is semantic, not a crash: the after-run completes normally and
returns `book`, but books an urgent slot for a routine referral.

## Diagnosis

The correct fix belongs in the tool-interface layer: keep `band` required and
validate it against `urgent|soon|routine` (and, ideally, validate that the
chosen slot's band matches the requested band). This makes omission fail
loudly instead of silently changing the business meaning of the query.

Neither loop control nor action de-duplication is the right fix. The bad run
uses 4 turns, below the cap of 8, and makes no duplicate call. A step cap could
only truncate the run, while de-duplication could only detect repeats; neither
would prevent an otherwise unique urgent slot from being booked for a routine
referral.

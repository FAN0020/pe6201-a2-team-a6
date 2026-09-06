# D2(c) Tool Call Dependency Rule

## Rule

Two tool calls may be placed in the same agent turn only when neither call
needs the other call's output. Calls that consume data produced by an earlier
call must remain in a later turn. The final gated action must run only after
all facts needed to justify it have been established.

## REF-5602 dependency analysis

| Tool call | Required information | Grouping decision |
|---|---|---|
| `get_referral` | The original `case_id` | Runs alone because later calls need the returned patient ID and specialty. |
| `check_referral_criteria` | Specialty and referral ID returned or confirmed by `get_referral` | May share a turn with `lookup_patient`; neither call needs the other's output. |
| `lookup_patient` | Patient ID returned by `get_referral` | May share a turn with `check_referral_criteria`; neither call needs the other's output. |
| First `get_clinic_slots` | Specialty, urgency band, and first half of the booking window | May share a turn with the second slot query after the band and window are known. |
| Second `get_clinic_slots` | Specialty, urgency band, and second half of the booking window | May share a turn with the first slot query because the date ranges are known and independent. |
| `book_slot` | Passed referral checks, no duplicate appointment, and a selected available slot | Runs last and passes through the autonomy gate because it is the irreversible action. |

## Resulting turn plans

Sequential execution uses one tool call per turn:

1. `get_referral`
2. `check_referral_criteria`
3. `lookup_patient`
4. first `get_clinic_slots`
5. second `get_clinic_slots`
6. `book_slot`

Grouped execution preserves the dependencies while combining independent
calls:

1. `get_referral`
2. `check_referral_criteria` and `lookup_patient`
3. first and second `get_clinic_slots`
4. `book_slot`

The concluding response is bookkeeping and is not counted as a tool-calling
turn. Grouped execution currently means that several calls are requested in
one agent turn and all observations are appended before the next backend move.
The Python tool functions still execute one after another inside that turn; the
experiment measures agent turns rather than multi-threaded wall-clock speed.

## Scope

This rule documents the current `REF-5602` scripted comparison. It must be
reviewed when the tool contract changes or new evaluation cases introduce new
dependencies. A grouped plan must never be created merely to reduce the turn
count; correctness and the dependency rule take priority.

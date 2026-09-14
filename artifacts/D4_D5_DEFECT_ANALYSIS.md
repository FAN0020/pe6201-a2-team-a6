# D4/D5 Defect Analysis

| Defect found during integration | Risk to marks or validity | Resolution and evidence |
|---|---|---|
| Scripted backend covered only one Problem B example | Marker could not reproduce the submitted set | Fixture-derived scripts now cover every case without reading the answer key; coverage is tested |
| Grader checked decision/trigger/slot but not the exact missing item | Vague requests could pass | Normalised exact missing-item comparison and a negative unit test were added |
| A final `book` could be asserted without a matching gated tool result | False success and gate bypass | Merged booking-safety hardening; final booking must match the executed, approved `book_slot` trace |
| Live confirm mode previously auto-approved | A live model could bypass the intended human gate | Auto-approval is restricted to scripted mode; live evaluation requires the explicit `--approve-fixture-bookings` simulation flag |
| Result output omitted descriptor identity, price provenance and prompt hashes | v1/v2 and cost claims were not auditable | Result schema now records prompt and descriptor hashes, version, model prices/source/date, freeze SHA, token source and approval policy |
| Individual branches produced 29 combined cases | Below D4's 30-case minimum | Added one separately attributed D4 integration case, producing 30 labelled cases and 58 trials |
| Liu's branch adds four negatives to the ten shipped negatives | Integrated set has 14 negatives, above the recommended 6-10 | Preserved teammate work and report the deviation transparently; do not silently drop labelled cases |
| Timeline assigns Fan Yupei descriptor v1 while the declaration assigns a unique GPT-5.4 model | A same-model v1/v2 causal comparison cannot be completed by the v1 run alone | Freeze a descriptor-only change and request/produce a same-SHA GPT-5.4 v2 companion result before claiming a paired effect |
| REF-5590 source materials disagree on whether a slot query belongs in the red-flag trace | Could create an unresolvable trace assertion | Follow the routing rule's early-exit requirement: red flag stops before slot search; retain Wang Chenyu's data issue log as disclosure |
| Initial GPT-5.4 smoke response emitted three JSON moves in one response | The strict parser correctly rejected it, but a full run would fail before any tool execution | Strengthened the fixed system prompt to require exactly one move and an observation before the next; retained strict parsing and added the raw response trace for auditable failures |
| Second GPT-5.4 smoke run used the matched phrase as `trigger` instead of the answer-key code | Correct clinical escalation still failed the exact deterministic check | Enumerated all five canonical Problem B trigger codes in the fixed rules and told the model to keep factual phrases in `reason` |

Scripted token and cost values are instrumentation estimates, not model
measurements. Live results use only API-reported token counts and explicitly
provided price inputs.

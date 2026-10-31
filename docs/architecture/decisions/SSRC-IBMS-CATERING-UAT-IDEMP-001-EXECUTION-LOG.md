# SSRC-IBMS Catering UAT — CATERING-UAT-IDEMP-001 Execution Log

**Document status:** Active — Catering business workflow UAT passed; live Inventory receipt idempotency verification paused; Event #6 delivery-control investigation open.

**Scenario ID:** `CATERING-UAT-IDEMP-001`
**Acceptance checklist:** `SSRC-IBMS-CATERING-UAT-IDEMP-001-ACCEPTANCE-CHECKLIST.md`
**Environment:** SQL Server `KASONGO`, database `CDCS_EMP_UAT`
**Primary verification target:** Inventory receipt idempotency, alongside the wider Catering business workflow UAT.

---

## 1. Execution summary

### Overall execution disposition

| Workstream | Result |
|---|---|
| Catering Customer workflow | PASS |
| Catering Request and Event workflow | PASS |
| Catering Quotation workflow | PASS |
| Quotation acceptance | PASS |
| Event Requirements and readiness | PASS |
| Production and Delivery workflow | PASS |
| Expense creation and approval | PASS |
| Expense Cost Association and consumption | PASS |
| Catering Revenue eligibility | PASS |
| Catering Revenue recognition | PASS |
| Event profitability calculation | PASS |
| Live Inventory receipt idempotency | PAUSED — deferred verification |
| Event #6 delivery-control observation | OPEN FOLLOW-UP |

**Catering business workflow result: PASS.**

The Catering business workflow was successfully exercised from Customer through Revenue. Event #7 also demonstrated the complete financial path from an accepted quotation through revenue recognition and consumed expense cost to calculated event profitability.

The live Inventory receipt idempotency scenario remains paused after the initial receipt was successfully posted. The outstanding sequential retry, conflicting-payload retry, concurrent duplicate submission, and final reconciliation cases have not been confirmed as completed against the live database.

The Event #6 delivery-control observation remains an open technical follow-up. The visible delivery action and apparent material shortfall warrant investigation, but server-side enforcement has not yet been established.

These two outstanding items do not invalidate the completed Catering business workflow results.

## 2. Catering business workflow execution

**Result: PASS**

The following business workflow areas were exercised and verified during browser UAT:

1. Customer creation and management.
2. Catering Request creation and processing.
3. Catering Event creation and progression.
4. Quotation preparation and acceptance.
5. Event Requirement management and readiness.
6. Production and Delivery workflow.
7. Expense creation, submission and approval.
8. Expense Cost Association and cost consumption.
9. Catering Revenue creation and eligibility establishment.
10. Catering Revenue recognition.
11. Event profitability calculation.

The individual event and financial evidence below provides additional confirmation of the completed workflow.

### 2.1 Event #5 — Ministry of ICT workshop

**Scenario:** Five-day Ministry of ICT workshop
**Event dates:** 26–30 October 2026
**Participants:** 50
**Participant-days:** 250
**Event status:** COMPLETED

Event #5 was used for the Ministry of ICT workshop demonstration scenario.

The event progressed through the Catering planning, readiness, production, delivery and completion workflow.

Five approved workshop Expenses were associated with Event #5 and their cost contributions were consumed.

The Event #5 workflow is retained as part of the completed Catering UAT evidence. Its existing expense and cost records must remain separate from the later Event #7 financial scenario.

### 2.2 Event #6 — Delivery-control observation

**Scenario:** `CATERING-UAT-IDEMP-001`
**Customer:** CDCS — Training of Trainers (TOT)
**Scheduled dates:** 29–31 October 2026
**Event status at observation:** `IN_PRODUCTION`

**Observed state**

- Event Requirement #9: `READY`.
- Rice requirement: 30.000 kg.
- Approved Purchase Order: `PO-CATERING-UAT-IDEMP-001-001`.
- Purchase Order ID: `7`.
- Purchase Order receipt status: `PARTIALLY RECEIVED`.
- Recorded receipt quantity: 2.000 kg out of 30.000 kg.
- Receipt movement ID: `8`.
- Observed stock balance for `TOT-RICE-001` at `UAT-LOC-001`: 2.000 kg.
- Event page exposed the `Mark Delivered` action.
- No event-specific kitchen transfer or valid consumption record had been evidenced at the time of observation.
- Event profitability was unavailable because no expense costs were associated with this event.

**Assessment: OPEN FOLLOW-UP**

The availability of the `Mark Delivered` action despite the apparent material shortfall warrants investigation.

This observation does not establish that the server-side delivery transition accepts delivery without satisfying material requirements.

**Evidence status:** Observed in the browser and Inventory balance view. Production consumption, event-specific transfers and server-side delivery validation remain unverified.

**Required follow-up**

1. Inspect the existing delivery transition and associated tests.
2. Determine whether material availability is checked before delivery.
3. Determine whether event-specific stock transfers are required.
4. Determine whether valid production consumption is enforced before delivery.
5. Verify server-side behavior, not merely the visibility of the browser action.
6. Record findings before proposing any focused remediation.

**Safety decision:** Do not execute `Mark Delivered`, create compensating Inventory movements, or alter Event #6 records as part of this documentation update.

The observation remains open until the delivery-control behavior has been investigated and evidenced.

### 2.3 Event #7 — CDCS TOT end-of-training party

**Customer:** CDCS — Training of Trainers (TOT)
**Source Request:** Catering Request #7
**Event date:** 31 October 2026
**Participants:** 30
**Event status:** `DELIVERED`

Event #7 was used to verify the Catering revenue and profitability workflow.

**Accepted quotation**

| Field | Verified value |
|---|---|
| Quotation | #7 |
| Customer | CDCS — Training of Trainers (TOT) |
| Quotation status | ACCEPTED |
| Subtotal | USD 480.00 |
| Adjustment | USD 0.00 |
| Total | USD 480.00 |

The quotation covered:

- Prepared lunch for 30 participants.
- Bottled drinking water for 30 participants.
- Seasonal fruit and light refreshments for 30 participants.

Delivery of all three components was confirmed for 31 October 2026.

**Catering Revenue**

| Field | Verified value |
|---|---|
| Revenue Reference | `CAT-REV-EVENT-7-QUOTE-7` |
| Source Type | `CATERING_QUOTATION` |
| Source Reference | `7` |
| Customer | CDCS — Training of Trainers (TOT) |
| Catering Event | Event #7 |
| Amount | USD 480.00 |
| Revenue Date | 2026-10-31 |
| Revenue Classification | Catering Service Revenue |
| Eligibility Status | ELIGIBLE |
| Final Revenue Status | RECOGNIZED |
| Recognized At | 2026-10-31 03:20:45.973000 |

Revenue eligibility was established using the confirmed delivery evidence and accepted quotation. Revenue recognition was then completed as a separate action.

**Expense Cost Association**

| Field | Verified value |
|---|---|
| Expense ID | 13 |
| Classification | Transport & Delivery |
| Amount | USD 45.00 |
| Currency | USD |
| Expense Status | APPROVED |
| Event Association | EVENT-7 |
| Cost Contribution Status | CONSUMED |
| Contribution Reference | `expense:13:catering:event:7:consume_approved_expense` |

Expense #13 was approved, associated with Event #7 and successfully consumed as a Catering cost contribution.

**Event Profitability**

| Component | Verified amount |
|---|---:|
| Recognized revenue | USD 480.00 |
| Consumed costs | USD 45.00 |
| **Resulting profit** | **USD 435.00** |

Calculation:

USD 480.00 − USD 45.00 = **USD 435.00**

The browser profitability view displayed:

- Event reference: `EVENT-7`.
- Revenue reference: `CAT-REV-EVENT-7-QUOTE-7`.
- Recognized revenue: USD 480.00.
- Consumed costs: USD 45.00.
- Expense ID: `13`.
- Consumed contribution reference: `expense:13:catering:event:7:consume_approved_expense`.
- Resulting profit: USD 435.00.

**Assessment: PASS**

Event #7 successfully demonstrated:

1. Accepted quotation as the revenue source.
2. Catering Revenue creation.
3. Delivery evidence and eligibility establishment.
4. Separate revenue recognition.
5. Approved expense association.
6. Cost contribution consumption.
7. Event profitability calculation.

**Scope limitation:** USD 435.00 represents recognized revenue less the consumed costs currently recorded for Event #7. It is not evidence that every possible event cost has been recorded.

## 3. Inventory receipt idempotency execution

**Scenario:** `CATERING-UAT-IDEMP-001`
**Result:** PAUSED — initial receipt posting confirmed; remaining live verification deferred.

### 3.1 Confirmed live execution evidence

**Evidence classification:** COMMAND-CONFIRMED, supplemented by read-only SQL inspection supplied during the session.

| Item | Confirmed result |
|---|---|
| Scenario | `CATERING-UAT-IDEMP-001` |
| SQL Server / database | `KASONGO` / `CDCS_EMP_UAT` |
| Product | `TOT-RICE-001`, product ID `5` |
| Stock item | ID `5` |
| Location | `UAT-LOC-001`, location ID `1` |
| Purchase Order | `PO-CATERING-UAT-IDEMP-001-001`, PO ID `7` |
| Purchase Order line | ID `7` |
| Receipt movement | ID `8`, status `POSTED` |
| Receipt quantity | `2.000 kg` |
| Valuation snapshot | USD `2.50` per kg |
| Valuation basis | `PO_LINE_UNIT_PRICE` |
| Idempotency record | ID `8`, linked to movement ID `8` |
| Receipt reference | `CATERING-UAT-IDEMP-001-20261028T181114-GRN-A` |
| Idempotency key | `CATERING-UAT-IDEMP-001-20261028T181114-SEQUENTIAL` |
| Observed stock balance after posting | `2.000 kg` |

The recorded movement and idempotency entry agree on the posted receipt and valuation snapshot.

The first receipt is a persistent business record. It must be preserved and included in any future continuation of the live test.

### 3.2 Harness correction

The first controlled receipt was posted successfully. The run subsequently stopped with:

`ValueError: valuation_price_basis must be PO_LINE_UNIT_PRICE.`

The cause was the sequential conflicting-payload retry supplying `RETRY_CONFLICT` as its valuation basis. The public `PurchaseOrderReceiptRequest` contract rejects that value before the service-level idempotency lookup can be exercised.

The harness-only retry payload was subsequently corrected to retain the valid `PO_LINE_UNIT_PRICE` basis while using a conflicting unit price of `999.99` and currency `SSP`.

This corrected payload is intended to test whether the existing idempotency key returns the original movement without overwriting its persisted valuation.

Focused offline tests were run after the harness correction:

- `tests/modules/procurement/integration/test_inventory_receipt_idempotency.py`: **6 passed**.
- `tests/modules/procurement/integration/test_contracts.py`: **57 passed**.

These offline test results do not establish that the corrected retry or concurrent case passed against the live database.

### 3.3 Live verification status

| Test | Status |
|---|---|
| Initial receipt posting and persisted valuation | PASS — first receipt confirmed |
| Same-key identical retry | PAUSED — live result not confirmed |
| Same-key conflicting valuation retry | PAUSED — live result not confirmed |
| Fresh-session verification of retry result | Pending |
| Concurrent duplicate submission | PAUSED — live result not confirmed |
| Final stock-balance reconciliation | Pending |
| Purchase Order receiving-total reconciliation | Pending |
| Overall live idempotency acceptance | PAUSED |

### 3.4 Continuation and data-integrity controls

1. Preserve movement ID `8`, idempotency record ID `8`, and their associated historical evidence.
2. Do not delete, reverse, or manually compensate for the posted receipt.
3. Do not rerun the live harness without a separately reviewed continuation plan and explicit authorization.
4. Before further live execution, inspect the current stock balance, Purchase Order line received quantity, receipt counts and existing idempotency records using read-only queries.
5. Any continuation must account for the already-posted 2 kg receipt and must not assume the original zero-balance baseline still applies.
6. Preserve the harness and unrelated working-tree changes.
7. Keep the Event #6 delivery-control investigation separate from the Inventory idempotency continuation.

**Protected harness status:** `scripts/run_live_inventory_receipt_idempotency.py` has not been inspected or executed during this checkpoint preparation. Its inspection and execution remain pending future investigation and require a separately reviewed continuation plan and explicit authorization.

## 4. Consolidated outstanding actions

| Follow-up | Current disposition | Required next action |
|---|---|---|
| Live Inventory receipt idempotency | PAUSED | Review continuation plan and complete remaining live verification |
| Event #6 delivery-control observation | OPEN | Inspect delivery transition, material controls and associated tests |

The completed Catering business workflow results do not depend on closing these two outstanding technical follow-ups.

## 5. Acceptance and closure criteria

### Catering business workflow

**Result: PASS**

The Customer-to-Revenue workflow and the Event #7 financial path have been exercised and verified through browser UAT.

### Live Inventory receipt idempotency

**Result: PAUSED**

Do not mark the live idempotency scenario as passed until the sequential and concurrent duplicate behaviors, persisted valuation, stock balance and Purchase Order receiving totals have been verified against the live database.

### Event #6 delivery-control investigation

**Result: OPEN FOLLOW-UP**

Do not close this observation until the server-side delivery transition and its material-readiness and consumption controls have been investigated and evidenced.

### Overall document disposition

**Current disposition:** Catering business workflow UAT passed. Live Inventory receipt idempotency verification paused for later execution. Event #6 delivery-control observation retained as an open follow-up.

**Document status:** Active — completed Catering business workflow evidence recorded; two technical follow-ups remain open.

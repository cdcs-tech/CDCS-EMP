# SSRC-IBMS Pilot Demonstration — Ministry of ICT UAT Execution Log

**Document status:** Active UAT execution log; partial browser verification recorded; end-to-end UAT remains in progress
**Authoritative scenario:** Ministry of ICT five-day workshop
**Scenario dates:** 26–30 October 2026 (intentionally simulated)
**UAT database:** `CDCS_EMP_UAT`
**Current implementation stage:** Stage 8 — Catering Revenue Eligibility and Recognition; browser verification of revenue, expense-cost delivery, and Event #5 profitability recorded
**Stage 8 migration:** `e7a4c91d2f60`
**Companion scenario:** `SSRC-IBMS-MINISTRY-OF-ICT-WORKSHOP-DEMONSTRATION-SCENARIO.md`

---

## 1. Purpose and evidence conventions

This log preserves the reported UAT state of the Ministry of ICT five-day workshop demonstration and records subsequent test execution.

The demonstration is an internal end-to-end business workflow test intended to establish how the current CDCS-EMP implementation supports SSRC-IBMS pilot readiness.

It is not evidence that a real Ministry of ICT workshop occurred.

### 1.1 Evidence labels

Use the following labels to distinguish the source and strength of each observation.

- **USER-SUPPLIED BASELINE:** Record details transcribed from UAT screens and supplied in the conversation. They have not been independently re-opened during this documentation step.
- **COMMAND-CONFIRMED:** Output returned by a command executed during the session.
- **BROWSER-VERIFIED:** Behavior directly observed during a browser UAT action and recorded with the action and result.
- **PENDING:** Not yet verified or not yet executed.
- **INFERENCE / RECONCILIATION:** A calculation or interpretation derived from supplied values; it is not a substitute for checking the application's underlying records.

Do not mark a test `PASS` solely because a status or record was reported in the initial baseline.

### 1.2 Test result values

| Result | Meaning |
|---|---|
| `PASS` | The expected behavior was directly verified. |
| `FAIL` | The observed behavior differed from the defined expectation. |
| `BLOCKED` | The test could not proceed because of an identified dependency or problem. |
| `NOT RUN` | The test has not yet been executed. |

---

## 2. Scenario and environment baseline

| Item | Baseline |
|---|---|
| Authoritative scenario | Ministry of ICT five-day workshop |
| Workshop subject | South Sudan ICT Infrastructure |
| Simulated service dates | 26–30 October 2026 |
| Customer | Ministry of ICT |
| Attendance | 50 |
| Requested service | Catering and Hall Hire |
| Catering Request | Request #5 |
| Catering Event | Event #5 |
| Catering Quotation | Quotation #5 |
| Event Requirement | Requirement #8 |
| Purchase Request | `PR-MICT-2026-001` |
| Purchase Order | `PO-MICT-2026-001` |
| Database | `CDCS_EMP_UAT` |
| Stage 8 migration | `e7a4c91d2f60` |

### 2.1 Simulated future dates

**USER-SUPPLIED BASELINE — CONFIRMED SCENARIO RULE**

The dates 26–30 October 2026 are intentionally used as simulated future dates in UAT. Event #5 being marked `COMPLETED` is intentional test state.

This combination is not a defect merely because the dates are in the future. Test the system's actual business rules and transitions, rather than treating the scenario as a live calendar.

### 2.2 Environment safety

- Preserve the existing `CDCS_EMP_UAT` database and its records.
- Do not reset or reseed the database without explicit authorization.
- Do not direct migration or test commands to the normal `CDCS_EMP` database.
- Do not alter application code during the initial browser UAT pre-check.
- Keep the ICRC five-day workshop scenario paused and separate.
- Do not commit this log until the saved documentation and Git state have been reviewed.

---

## 3. Current implementation checkpoint

### 3.1 Stage 8 migration

**COMMAND-CONFIRMED**

The following migration operation was run with a temporary process-level `DB_NAME=CDCS_EMP_UAT` override:

```powershell
flask --app app db upgrade e7a4c91d2f60
```

The output reported:

```text
Running upgrade 4c91e7a2d6f3 -> e7a4c91d2f60, Add evidence fields for Catering revenue eligibility.
```

A subsequent current-revision check reported:

```text
e7a4c91d2f60 (head)
```

The original `DB_NAME` environment setting was restored by the command's `finally` block.

**Scope of this evidence:** It confirms that the migration command succeeded and the subsequent revision check returned the new revision while the temporary UAT database-name override was active. It does not independently verify every new column or the behavior of the browser workflow.

### 3.2 Implementation checkpoint and browser verification

The Stage 8 implementation was committed at checkpoint `8753c3a` (`feat(catering): implement revenue eligibility evidence`), according to the project checkpoint record.

**BROWSER-VERIFIED — PARTIAL UAT**

Browser verification has subsequently confirmed the following for the simulated Ministry of ICT Event #5:

- Catering revenue is recognized under reference `REV-MICT-WS-2026-001` for USD 1,250.00.
- Approved Expense #1, amount USD 420.00, was associated with Event #5 through the existing Expense Cost Association.
- The association initially showed `ELIGIBLE` with no consumption timestamp.
- The existing association's **Retry Delivery** action was executed once. The resulting browser state showed the association as `CONSUMED` and populated `Consumed At`.
- Event #5 profitability then displayed recognized revenue of USD 1,250.00, consumed costs of USD 420.00, and profit of USD 830.00.
- Before successful delivery, the profitability screen explained that profitability was unavailable because recognized revenue and valid consumed-cost records were required.

These results verify the observed revenue/cost/profitability state for the linked records. They do not establish that all revenue eligibility and recognition controls, all expense associations, all procurement workflows, or the full demonstration scenario have passed UAT.

**Current UAT status:** Partial browser verification completed; remaining business-workflow checks and execution-log reconciliation are still in progress.

---

## 4. Baseline: Catering Request #5

**Evidence classification:** USER-SUPPLIED BASELINE

| Field | Supplied value |
|---|---|
| Customer | Ministry of ICT |
| Request date | 16 October 2026 |
| Requested service | Catering and Hall Hire |
| Service date | 26 October 2026 |
| Attendance | 50 |
| Requirements | Breakfast, lunch, refreshments |
| Notes | Five days’ workshop on South Sudan ICT Infrastructure — 26–30 October 2026 |
| Status | `Submitted` |

**Initial assessment:** The supplied record identifies the intended customer, service, attendance, and simulated workshop period.

**Browser verification:** PENDING

Items to verify:

- The request is accessible and its values persist.
- Event #5 references Request #5.
- The request and operational Event remain distinct records.
- The simulated date handling does not incorrectly block the intended UAT workflow.

---

## 5. Baseline: Catering Event #5

**Evidence classification:** USER-SUPPLIED BASELINE

| Field | Supplied value |
|---|---|
| Customer | Ministry of ICT |
| Source Request | Request #5 |
| Event date | 26 October 2026 |
| Service details | Catering and Hall Hire |
| Attendance | 50 |
| Operational notes | Five days’ workshop on South Sudan ICT Infrastructure — 26–30 October 2026 |
| Status | `COMPLETED` |

**Scenario interpretation:** `COMPLETED` is intentional simulated state, not a calendar inconsistency to fix.

**Browser verification:** PENDING

Items to verify:

- The Event and source-request relationship.
- The displayed customer, attendance, service, and operational notes.
- The Event status and available actions.
- The behavior of revenue eligibility when the Event is `COMPLETED`.
- That Event completion does not itself recognize revenue.

---

## 6. Baseline: Catering Quotation #5

**Evidence classification:** USER-SUPPLIED BASELINE

| Field | Supplied value |
|---|---|
| Customer | Ministry of ICT |
| Catering Event | Event #5 |
| Quotation date | 16 October 2026 |
| Valid until | 25 October 2026 |
| Customer notes | Five-day workshop on South Sudan ICT Infrastructure |
| Status | `ACCEPTED` |

### 6.1 Quotation line reconciliation

| Description | Item reference | Quantity | Unit | Unit price (USD) | Line total (USD) |
|---|---|---:|---|---:|---:|
| Breakfast per participant | `BREAKFAST-001` | 50 | person | 5.00 | 250.00 |
| Lunch per participant | `LUNCH-002` | 50 | person | 15.00 | 750.00 |
| Three bottles of water per participant | `WATER-003` | 150 | bottle | 1.00 | 150.00 |
| One bottle of soda per participant | `SODA-004` | 50 | bottle | 2.00 | 100.00 |
| **Total** | | | | | **1,250.00** |

Pricing summary supplied:

- Subtotal: USD 1,250.00
- Adjustment: USD 0.00
- Total: USD 1,250.00

**Arithmetic reconciliation:** USD 250.00 + USD 750.00 + USD 150.00 + USD 100.00 = USD 1,250.00.

**Browser verification:** PENDING

Items to verify:

- The quotation belongs to Event #5 and the Ministry of ICT.
- Its status is `ACCEPTED`.
- The line values and total persist.
- The accepted quotation can be selected as revenue eligibility evidence.
- The application does not confuse quotation acceptance with revenue recognition.

---

## 7. Baseline: Event Requirement #8 and purchase requirements

### 7.1 Event Requirement #8

**Evidence classification:** USER-SUPPLIED BASELINE

| Field | Supplied value |
|---|---|
| Catering Event | Event #5 |
| Description | Posho (Maize flour) for Ministry of ICT workshop |
| Item reference | `POSHO-003` |
| Quantity | 150.000 kg |
| Fulfilment type | `PROCUREMENT` |
| Required by | 25 October 2026 |
| Status | `READY` |

### 7.2 Catering Purchase Requirement

| Field | Supplied value |
|---|---|
| Description | Posho (Maize flour) for Ministry of ICT workshop |
| Quantity | 150.000 kg |
| Status | `DRAFT` |
| Procurement reference | `CATERING-PR-fe23a058-344e-4291-9d0e-e5e3eb04143b` |

### 7.3 Procurement Purchase Requirement

| Field | Supplied value |
|---|---|
| Reference | `CATERING-PR-fe23a058-344e-4291-9d0e-e5e3eb04143b` |
| Source module | `CATERING` |
| Source type | `CATERING_PURCHASE_REQUIREMENT` |
| Source reference | `fe23a058-344e-4291-9d0e-e5e3eb04143b` |
| Required by | 25 October 2026 |
| Status | `DRAFT` |

**Outstanding lifecycle question:** Event Requirement #8 is `READY`, while the Catering Purchase Requirement and linked Procurement Purchase Requirement are displayed as `DRAFT`. The meaning and expected transition must be checked against the implementation and approved workflow contract. Do not label this a defect until the intended lifecycle is established.

**Browser verification:** PENDING

---

## 8. Baseline: Purchase Request

**Evidence classification:** USER-SUPPLIED BASELINE

| Field | Supplied value |
|---|---|
| Reference | `PR-MICT-2026-001` |
| Purchase Requirement | `CATERING-PR-fe23a058-344e-4291-9d0e-e5e3eb04143b` |
| Request date | 19 October 2026 |
| Required by | 25 October 2026 |
| Status | `APPROVED` |
| Justification | Posho (Maize flour) required for the Ministry of ICT five-day workshop on South Sudan ICT Infrastructure, 26–30 October 2026. |

Purchase Request line:

| Field | Supplied value |
|---|---|
| Description | Posho (Maize flour) for Ministry of ICT workshop |
| Item reference | `POSHO-003` |
| Quantity | 150.000 kg |
| Estimated unit cost | Not displayed |
| Estimated total | Not displayed |
| Required by | 25 October 2026 |
| Notes | Event #5; Event Requirement #8; item reference POSHO-003; quantity 150.000 kg; workshop period |

**Browser verification:** PENDING

Verify the link to the originating requirement, approval status, item identity, quantity, and expected lifecycle behavior.

---

## 9. Baseline: Purchase Order

**Evidence classification:** USER-SUPPLIED BASELINE

| Field | Supplied value |
|---|---|
| Reference | `PO-MICT-2026-001` |
| Supplier | UAT Test Supplier – Procurement A |
| Order date | 19 October 2026 |
| Expected delivery | 25 October 2026 |
| Status | `APPROVED` |
| Purchase Request | `PR-MICT-2026-001` |

Purchase Order line:

| Field | Supplied value |
|---|---|
| Description | Posho (Maize flour) for Ministry of ICT workshop |
| Item reference | `POSHO-003` |
| Ordered quantity | 150.000 kg |
| Receiving status | `FULLY RECEIVED` |
| Received quantity | 150.000 / 150.000 kg |
| Receipts recorded | 2 |
| Unit price | USD 2.00 |
| Total amount | USD 300.00 |

**Arithmetic reconciliation:** 150 kg × USD 2.00/kg = USD 300.00.

**Browser verification:** PENDING

Verify the Purchase Order and Purchase Request relationship, approval status, line amount, and receiving history.

---

## 10. Baseline: Inventory movements and stock balance

**Evidence classification:** USER-SUPPLIED BASELINE

### 10.1 Receipt movements

| Stock item | Location | Movement type | Quantity | Status | Occurred at | Reference |
|---|---|---|---:|---|---|---|
| Posho (Maize flour) | UAT Integration Test Location (`UAT-LOC-001`) | `RECEIPT` | 50.000 kg | Posted | 19 October 2026, 21:26 | `MICT-UAT-POSHO003-PARTIAL-20261019-001` |
| Posho (Maize flour) | UAT Integration Test Location (`UAT-LOC-001`) | `RECEIPT` | 100.000 kg | Posted | 19 October 2026, 23:13 | `MICT-UAT-POSHO003-FINAL-20261019-001` |

### 10.2 Stock balance

| Stock item | Product code | Location | Quantity |
|---|---|---|---:|
| Posho (Maize flour) | `POSHO-003` | UAT Integration Test Location (`UAT-LOC-001`) | 150.000 kg |

**Arithmetic reconciliation:** 50 kg + 100 kg = 150 kg, equal to the supplied Purchase Order quantity and reported stock balance.

This arithmetic does not independently prove the current stock balance or exclude other stock movements.

**Browser verification:** PENDING

Verify both posted movements, their references, the Purchase Order receiving status, and the current stock balance. Confirm that receipt is not incorrectly treated as consumption or Catering cost recognition.

---

## 11. Baseline: expense records

**Evidence classification:** USER-SUPPLIED BASELINE

The following 12 entries were supplied from the Expenses view.

| # | Expense date | Description | Classification | Amount (USD) |
|---:|---|---|---|---:|
| 1 | 26 October 2026 | Workshop catering ingredients: rice, beans, vegetables and cooking oil; excludes Posho already recorded in inventory receipts. | Food Supplies | 420.00 |
| 2 | 26 October 2026 | Drinking water for workshop participants and catering team. | Beverages | 75.00 |
| 3 | 26 October 2026 | Tea, sugar, milk and bread for workshop tea breaks. | Tea Break Supplies | 110.00 |
| 4 | 26 October 2026 | Cooking fuel for initial workshop meal preparation. | Cooking Fuel | 95.00 |
| 5 | 27 October 2026 | Fresh vegetables and beans replenishment for workshop meals. | Food Supplies | 260.00 |
| 6 | 27 October 2026 | Local market transport and delivery of catering supplies. | Transport & Delivery | 60.00 |
| 7 | 28 October 2026 | Meat and eggs for workshop meals. | Food Supplies | 375.00 |
| 8 | 28 October 2026 | Temporary catering assistants for food preparation and service. | Casual Catering Labour | 250.00 |
| 9 | 29 October 2026 | Fruit and snack replenishment for workshop tea breaks. | Tea Break Supplies | 190.00 |
| 10 | 29 October 2026 | Dishwashing liquid, soap, refuse bags and cleaning supplies. | Cleaning & Sanitation | 85.00 |
| 11 | 30 October 2026 | Drinking water replenishment for the final workshop day. | Beverages | 75.00 |
| 12 | 30 October 2026 | Final-day fresh food and produce replenishment. | Food Supplies | 280.00 |
| | | **Total** | | **2,275.00** |

### 11.1 Expense total reconciliation

The supplied amounts sum to USD 2,275.00.

This is the total of the listed expense entries, not a verified total of consumed Catering costs.

### 11.2 Expense #1 — association and consumption

**Evidence classification:** BROWSER-VERIFIED

Expense #1 was approved and associated with Catering Event #5.

| Field | Verified value |
|---|---|
| Description | Workshop catering ingredients: rice, beans, vegetables and cooking oil; excludes Posho already recorded in inventory receipts. |
| Amount | USD 420.00 |
| Expense date | 26 October 2026 |
| Association status before delivery retry | `ELIGIBLE` |
| Action taken | Used **Retry Delivery** on the existing association once |
| Association status after retry | `CONSUMED` |
| Consumed at | `2026-10-22 18:39:08.323631+00:00` |
| Contribution reference | `expense:1:catering:event:5:consume_approved_expense` |

After the retry, the browser displayed the association as `CONSUMED`, populated `Consumed At`, and showed no further association action. Event #5 profitability also reflected USD 420.00 in consumed costs.

**Result:** `PASS` for the observed delivery and consumption of the existing Expense #1 association.

**Scope limitation:** This result applies to Expense #1 only. The presence of 12 Expenses in the scenario does not establish that the other 11 are associated with Event #5 or consumed. Verify each relevant expense and association individually.

---

## 12. Stage 8 — revenue eligibility and recognition

**Current focus:** Verify the new Catering revenue eligibility and recognition behavior using the Ministry of ICT scenario.

### 12.1 Required business rules

The test must establish that:

1. The associated Event is `DELIVERED` or `COMPLETED`.
2. An authorized user explicitly confirms the service delivered.
3. An accepted quotation supports the proposed revenue amount.
4. Any difference from the quotation amount is explained by a documented adjustment reason.
5. The record identifies the revenue date, source business context, and eligibility evidence.
6. Eligibility is explicitly established and transitions the revenue record to `ELIGIBLE`.
7. Recognition is a separate explicit authorized action.
8. Recognition transitions an eligible record to `RECOGNIZED`.
9. Event completion and quotation acceptance do not automatically recognize revenue.

### 12.2 Current evidence status

**Evidence classification:** BROWSER-VERIFIED for the current recognized-revenue record and its displayed amount; other lifecycle controls remain to be verified.

| Verification item | Result |
|---|---|
| Does Catering Revenue exist for Event #5? | PASS — revenue reference `REV-MICT-WS-2026-001` was observed |
| Is the correct customer and Event associated? | PASS — Ministry of ICT, Event #5 |
| Is Quotation #5 available as eligibility evidence? | Not independently re-verified in this check |
| Is delivery evidence required and validated? | Not independently re-verified in this check |
| Are eligibility reason and revenue date captured? | Not independently re-verified in this check |
| Is a quotation amount adjustment validated when applicable? | NOT RUN |
| Can an authorized user explicitly establish eligibility? | NOT RUN in this verification |
| Does the record persist as `ELIGIBLE` with evidence? | Historical eligibility transition not independently verified here |
| Is recognition a separate authorized operation? | NOT RUN in this verification |
| Does recognition persist as `RECOGNIZED`? | PASS — current record was observed as recognized |
| Is duplicate or invalid recognition prevented? | NOT RUN |
| Does reporting include recognized revenue correctly? | PARTIALLY VERIFIED — Event #5 profitability displayed the recognized revenue amount |

### 12.3 Recognized revenue reference

The browser displayed the following simulated UAT revenue record:

| Field | Verified value |
|---|---|
| Revenue reference | `REV-MICT-WS-2026-001` |
| Source type | `CATERING_QUOTATION` |
| Source reference | `5` |
| Customer | Ministry of ICT |
| Catering Event | Event #5 |
| Amount | USD 1,250.00 |
| Classification | `CATERING_SERVICE_REVENUE` |
| Current state | Recognized |

This confirms the observed current record and amount. It does not, by itself, prove every preceding eligibility, authorization, validation, or duplicate-prevention control. Those controls must be tested separately before Stage 8 can be considered fully UAT-verified.

---

## 13. Profitability and reporting verification

**Evidence classification:** BROWSER-VERIFIED for Event #5's displayed revenue, consumed costs, and profitability after Expense #1 delivery.

The intended profitability basis is recognized Catering revenue and valid consumed Catering costs.

### 13.1 Before Expense #1 delivery

Before the existing Expense #1 association was successfully delivered, the Event #5 profitability area showed no profitability action and displayed this helper text:

> Profitability is currently unavailable. Ensure recognized Catering revenue and valid consumed cost records are available.

This was consistent with the absence of a valid consumed-cost record for Expense #1 at that point.

### 13.2 After Expense #1 delivery

After the existing association's **Retry Delivery** action succeeded, the browser displayed:

| Measure | Verified value |
|---|---:|
| Recognized Catering revenue | USD 1,250.00 |
| Consumed Catering costs | USD 420.00 |
| Profit | USD 830.00 |

The displayed result reconciles arithmetically:

`USD 1,250.00 − USD 420.00 = USD 830.00`

The associated cost contribution referenced `expense:1:catering:event:5:consume_approved_expense`. Expense #1's association displayed `CONSUMED` with a populated `Consumed At` timestamp.

### 13.3 Scope and remaining verification

- Do not treat the total of all 12 listed expenses (USD 2,275.00) as the consumed-cost total; the other expense associations and consumption states have not been established by this check.
- Do not add the USD 300.00 Posho Purchase Order value as a separate cost without tracing its representation in the cost records and preventing double-counting.
- The displayed USD 830.00 result is verified for the revenue and consumed-cost values shown by the browser. It is not a final profitability conclusion for the entire workshop unless all relevant costs and revenue have been reconciled.
- Additional reporting, eligibility, authorization, and duplicate-prevention tests remain outstanding.

**Current result:** `PASS` for the observed Event #5 profitability display after Expense #1 was consumed; broader workshop profitability reconciliation remains pending.

### 13.4 Subsequent verification — five consumed expense contributions

**Evidence classification:** USER-SUPPLIED BROWSER-VERIFIED RESULT

Following the earlier Expense #1-only checkpoint, the user confirmed that the Expense Cost Association now appears correctly on Catering Event #5 after refreshing the page.

The refreshed Event #5 page displayed the following profitability values:

| Measure | Observed value |
|---|---:|
| Recognized Catering revenue | USD 1,250.00 |
| Consumed Catering costs | USD 960.00 |
| Resulting profit | USD 290.00 |

The five visible consumed-cost contributions were:

| Expense ID | Amount (USD) | Contribution reference |
|---:|---:|---|
| 1 | 420.00 | `expense:1:catering:event:5:consume_approved_expense` |
| 2 | 75.00 | `expense:2:catering:event:5:consume_approved_expense` |
| 3 | 110.00 | `expense:3:catering:event:5:consume_approved_expense` |
| 4 | 95.00 | `expense:4:catering:event:5:consume_approved_expense` |
| 5 | 260.00 | `expense:5:catering:event:5:consume_approved_expense` |
| **Total** | **960.00** | |

**Arithmetic reconciliation:**

`USD 420.00 + USD 75.00 + USD 110.00 + USD 95.00 + USD 260.00 = USD 960.00`

`USD 1,250.00 − USD 960.00 = USD 290.00`

The Expense Cost Association table displayed Expenses #1–#5 as `CONSUMED`, with populated consumption timestamps and no remaining actions for these five associations.

**Result:** `PASS` for the reported refreshed-page display, the five visible consumed contributions, and the arithmetic reconciliation of the displayed profitability values.

**Evidence limitation:** This entry records the browser result supplied by the user; the page was not independently reopened during this documentation update. It does not establish the status of Expenses #6–#12, reconcile all workshop costs, or resolve the inventory-to-event-cost traceability limitation documented in F-006. The USD 290.00 result is the current displayed profitability based on the recognized revenue and five consumed contributions, not yet a final profitability conclusion for the entire workshop.

---

## 14. Browser UAT test register

This register distinguishes earlier baseline observations from subsequent browser verification. A test is marked `PASS` only where the observed action and result support its stated objective. Current-state inspection does not, by itself, verify every lifecycle or authorization control.

| Test ID | Test objective | Expected result | Result |
|---|---|---|---|
| MICT-UAT-001 | Open Catering Request #5 | Correct Ministry request and values are displayed | NOT RUN |
| MICT-UAT-002 | Open Catering Event #5 | Correct source request, customer, service, attendance, and status are displayed | NOT RUN |
| MICT-UAT-003 | Open Quotation #5 | Accepted quotation and USD 1,250.00 total are displayed | NOT RUN |
| MICT-UAT-004 | Inspect Event Requirement #8 | Posho requirement and `READY` status are displayed | NOT RUN |
| MICT-UAT-005 | Inspect Catering and Procurement Purchase Requirements | References, source relationships, and lifecycle states are confirmed | NOT RUN |
| MICT-UAT-006 | Inspect `PR-MICT-2026-001` | Approved Purchase Request and correct requirement link are displayed | NOT RUN |
| MICT-UAT-007 | Inspect `PO-MICT-2026-001` | Approved Purchase Order, USD 300.00 line, and fully received state are displayed | NOT RUN |
| MICT-UAT-008 | Inspect receipt history | Both posted receipt references and quantities are displayed | NOT RUN |
| MICT-UAT-009 | Inspect stock balance | Posho balance and location are displayed and reconciled | NOT RUN |
| MICT-UAT-010 | Inspect all 12 expenses | Records and values reconcile to the supplied baseline | NOT RUN |
| MICT-UAT-011 | Verify Expense #1 association delivery and consumption | Retrying the existing eligible association delivers the contribution, persists `CONSUMED`, and populates `Consumed At` | PASS |
| MICT-UAT-012 | Inspect Catering Revenue for Event #5 | Current record, source, customer, amount, classification, and recognized state are established | PASS |
| MICT-UAT-013 | Establish revenue eligibility | Authorized action validates and persists required eligibility evidence | NOT RUN |
| MICT-UAT-014 | Test eligibility amount support | Accepted quotation is referenced and any adjustment is justified | NOT RUN |
| MICT-UAT-015 | Recognize eligible revenue | Separate authorized action transitions the record to `RECOGNIZED` | NOT RUN — current recognized state observed; transition not verified in this check |
| MICT-UAT-016 | Verify recognition controls | Invalid or duplicate recognition is handled correctly | NOT RUN |
| MICT-UAT-017 | Verify profitability before prerequisites | Profitability unavailability is explained when the required recognized-revenue and valid consumed-cost evidence is not available | PASS |
| MICT-UAT-018 | Verify profitability after prerequisites | Event #5 displays USD 1,250.00 recognized revenue, USD 420.00 consumed costs, and USD 830.00 profit after Expense #1 consumption | PASS |
| MICT-UAT-019 | Verify inventory-to-event-cost traceability for soda | A valid inventory-consumption record links the issued quantity and its supported cost valuation to Event #5 and contributes only the valid consumed cost to profitability | BLOCKED — required end-to-end capability is not available in the current workflow |
| MICT-UAT-020 | Verify refreshed Event #5 profitability with five consumed expense contributions | Event #5 displays USD 1,250.00 recognized revenue, USD 960.00 consumed costs, and USD 290.00 profit; Expenses #1–#5 are shown as `CONSUMED` | PASS — user-supplied browser verification; independent recheck pending |

### 14.1 Evidence notes

- **MICT-UAT-011:** The existing Expense #1 association was retried once. It changed from `ELIGIBLE` to `CONSUMED`; `Consumed At` was populated, and the contribution reference was `expense:1:catering:event:5:consume_approved_expense`.
- **MICT-UAT-012:** The current revenue record displayed reference `REV-MICT-WS-2026-001`, source type `CATERING_QUOTATION`, source reference `5`, customer Ministry of ICT, Event #5, USD 1,250.00, classification `CATERING_SERVICE_REVENUE`, and recognized state.
- **MICT-UAT-017:** Before successful Expense #1 delivery, the profitability area displayed the helper text explaining that recognized revenue and valid consumed-cost records were required.
- **MICT-UAT-018:** After delivery, the browser displayed USD 1,250.00 revenue, USD 420.00 consumed costs, and USD 830.00 profit.
- **MICT-UAT-019:** The browser verified receipt `GRN-MICT-WS-2026-002` for 50 bottles of `SODA-004` at `MAIN-STORE`, and the stock balance displayed 50 bottles. No event-attributed inventory consumption or cost contribution was verified. The test is `BLOCKED` by the current capability limitation; no soda stock issue or standalone expense was created.
- **MICT-UAT-020:** The user confirmed that after refreshing Catering Event #5, the Expense Cost Association table displayed Expenses #1–#5 as `CONSUMED`, with consumption timestamps and no remaining actions for those associations. The displayed contributions totalled USD 960.00. Event #5 profitability displayed USD 1,250.00 recognized revenue, USD 960.00 consumed costs, and USD 290.00 profit. This is a user-supplied browser result, not an independent recheck during this documentation update. Expenses #6–#12 and full-workshop cost reconciliation remain outstanding.

These passes are limited to the actions and results described above. They do not certify the remaining scenario workflow or untested eligibility, recognition, duplicate-prevention, and authorization controls.

For each subsequent test, record the browser action, resulting state, evidence reference where available, and any error message. Update results only when the evidence supports the expected behavior.

---

## 15. Findings and unresolved questions

### F-001 — Purchase requirement lifecycle

**Observation:** Event Requirement #8 is reported as `READY`; the Catering Purchase Requirement and linked Procurement Purchase Requirement were reported as `DRAFT` in the supplied baseline.

**Status:** Open — the lifecycle states have not been independently rechecked in the current verification sequence.

**Next action:** Inspect the records and compare the intended lifecycle transitions with the approved integration and workflow contracts before classifying this as a defect.

### F-002 — Expense consumption evidence

**Observation:** Expense #1's existing association initially displayed `ELIGIBLE` with no `Consumed At` timestamp. After the existing association's **Retry Delivery** action was executed once, the association displayed `CONSUMED` and `Consumed At` was populated.

**Status:** Resolved for the observed Expense #1 association delivery and consumption; other expense associations remain unverified.

**Next action:** Continue verifying the relevant remaining expense records individually. Do not infer that all 12 expenses are associated with Event #5 or consumed.

### F-003 — Catering revenue record and recognition

**Observation:** The browser displayed recognized Catering revenue reference `REV-MICT-WS-2026-001`, source type `CATERING_QUOTATION`, source reference `5`, customer Ministry of ICT, Event #5, USD 1,250.00, and classification `CATERING_SERVICE_REVENUE`.

**Status:** Current recognized-revenue record and amount verified; eligibility history, authorization controls, recognition transition, and duplicate/invalid recognition behavior remain unverified.

**Next action:** Test the outstanding eligibility and recognition controls separately, without creating duplicate revenue records or repeating financial actions unless specifically authorized.

### F-004 — Profitability availability and reconciliation

**Observation:** Before successful Expense #1 delivery, the profitability screen explained that recognized revenue and valid consumed-cost records were required. After delivery, it displayed USD 1,250.00 recognized revenue, USD 420.00 consumed costs, and USD 830.00 profit.

**Status:** Resolved for the observed Event #5 display based on the linked revenue and Expense #1 contribution; full-workshop financial reconciliation remains open.

**Next action:** Verify the remaining relevant expenses and cost records, trace the Posho procurement/receipt/cost relationship, and guard against double-counting before treating the USD 830.00 result as final workshop profitability.

### F-005 — Scenario timing

**Observation:** The workshop service dates are in the future relative to the execution date, while Event #5 is `COMPLETED`.

**Status:** Resolved as an intentional scenario rule.

**Decision:** Do not treat the future dates and completed status as a defect solely on that basis.

### F-006 — Inventory consumption is not linked to Catering event costs

**Observation:** The soda Purchase Order `PO-MICT-2026-002` was approved, and receipt `GRN-MICT-WS-2026-002` was successfully recorded for 50 bottles of MICT Soda (`SODA-004`) at `MAIN-STORE`. The browser subsequently displayed the 50-bottle stock balance.

The current workflow does not provide a verified, costed inventory-consumption record linked to Catering Event #5 and Event Requirement #7. A stock receipt establishes inventory received, but it does not establish consumption by the workshop. A stock issue or quantity allocation alone does not establish the required event-cost contribution and monetary valuation.

**Status:** Open — receipt and stock balance verified; inventory-to-event-cost traceability remains an implementation limitation. No soda consumption or soda cost contribution has been verified.

**Financial treatment:** Event #5's currently displayed profitability remains USD 1,250.00 recognized revenue, USD 420.00 consumed Catering costs, and USD 830.00 profit. The soda purchase value is excluded because no valid event-attributed consumed-cost record has been established. This display must not be treated as final workshop profitability.

**Decision:** Do not create a standalone soda expense or record a stock issue solely to make profitability include the soda purchase. Avoid double-counting procurement expenditure and inventory consumption.

**Next action:** Complete the current UAT without changing existing scenario data. Plan a separate, test-first enhancement that establishes traceable inventory consumption, event attribution, cost valuation, and an idempotent contribution to Catering event profitability. Reconcile the relevant workflow and architecture before implementation.

---

## 16. Execution log entry template

Append an entry for each browser UAT action using this structure:

### MICT-UAT-XXX — [Test title]

- **Execution date/time:**
- **Environment:** `CDCS_EMP_UAT`
- **User/role used:**
- **Starting record state:**
- **Preconditions:**
- **Action performed:**
- **Expected result:**
- **Actual result:**
- **Evidence reference:**
- **Outcome:** `PASS` / `FAIL` / `BLOCKED` / `NOT RUN`
- **Defect or follow-up reference:**
- **Notes:**

Avoid recording credentials, passwords, tokens, or other secrets in this log.

---

## 17. Next authorized work sequence

1. Preserve the existing `CDCS_EMP_UAT` database and all scenario records; do not reset or reseed.
2. Continue the remaining browser UAT checks for the Ministry of ICT scenario, starting with the purchase-requirement lifecycle and the related procurement/receipt/stock evidence.
3. Inspect the remaining Expenses individually and determine which, if any, have valid Event #5 associations and consumed-cost records.
4. Test any outstanding Catering Revenue eligibility, authorization, recognition-transition, and duplicate/invalid recognition controls as separate actions, without repeating completed financial actions or creating duplicate records.
5. Reconcile Event #5 profitability against all relevant recognized revenue and valid consumed-cost records, including the Posho cost path, before concluding full-workshop profitability.
6. Record each new browser action and result in §14 and append an execution entry using §16's template.
7. Reconcile the findings in §15 as evidence is gathered. Keep unverified items open or `NOT RUN`.
8. After the remaining end-to-end business workflow UAT is complete, review the execution log and companion scenario document together.
9. Review Git status and diffs before any documentation commit. Keep both Ministry of ICT UAT documents uncommitted until the broader end-to-end business workflow UAT is complete.

**Safety constraints:** Do not reset or reseed the database, alter application code, repeat completed financial actions, or commit the two UAT documents as part of this documentation update. Any new action that changes UAT business data requires the appropriate authorization.

---

## 18. Scenario authority and separation

This log belongs exclusively to the Ministry of ICT five-day workshop scenario.

The ICRC five-day workshop at SSRC Juba is a separate, paused scenario. Its records and execution history must not be treated as the current Ministry UAT baseline.

The authoritative demonstration workflow is the Ministry of ICT five-day workshop described in the companion scenario document. This log records evidence and progress for that workflow in preparation for the SSRC-IBMS pilot.

---

## 19. Subsequent browser verification — Expense Cost Association and profitability

### MICT-UAT-020 — Verify refreshed Event #5 profitability with five consumed expense contributions

- **Execution date/time:** Not recorded in the supplied result.
- **Environment:** `CDCS_EMP_UAT`
- **User/role used:** Not recorded.
- **Starting record state:** Event #5 was `COMPLETED`. An earlier checkpoint displayed USD 1,250.00 recognized revenue, USD 420.00 consumed costs, and USD 830.00 profit after Expense #1 consumption.
- **Preconditions:** Catering Event #5 and its recognized revenue record existed; expense-cost associations and consumed-cost contributions were available.
- **Action performed:** Refreshed the Catering Event #5 page and inspected Event Profitability and the Expense Cost Association table.
- **Expected result:** Persisted associations remain visible after refresh; consumed contributions and displayed profitability reconcile.
- **Actual result:** Expenses #1–#5 appeared as `CONSUMED`, each with a consumption timestamp and no remaining association actions. Recognized revenue displayed as USD 1,250.00, consumed costs as USD 960.00, and resulting profit as USD 290.00.
- **Evidence reference:** User-supplied browser result in this conversation; contribution references are listed in Section 13.4.
- **Outcome:** `PASS` — reported browser state and arithmetic reconcile.
- **Defect or follow-up reference:** Continue remaining expense verification and full-workshop cost reconciliation; F-006 remains open.
- **Notes:** This entry supersedes the earlier figures only as the latest reported Event #5 display. It does not change the historical record of MICT-UAT-018, establish the status of Expenses #6–#12, or resolve inventory-to-event-cost traceability. Independent browser re-verification has not been performed during this documentation update.

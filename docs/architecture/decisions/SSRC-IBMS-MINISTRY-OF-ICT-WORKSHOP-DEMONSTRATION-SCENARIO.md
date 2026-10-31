# SSRC-IBMS Pilot Demonstration Scenario — Ministry of ICT Five-Day Workshop

**Document status:** Working baseline for internal end-to-end UAT
**Scenario authority:** Authoritative SSRC-IBMS pilot demonstration workflow
**Business scenario:** Ministry of ICT five-day workshop on South Sudan ICT Infrastructure
**Simulated service dates:** 26–30 October 2026
**UAT environment:** `CDCS_EMP_UAT`
**Current implementation checkpoint:** Stage 8 — Catering Revenue Eligibility and Recognition
**Current Stage 8 migration:** `e7a4c91d2f60`
**Purpose:** Internal CDCS-EMP business workflow testing and SSRC-IBMS pilot readiness preparation

---

## 1. Purpose and scope

This document defines the authoritative Ministry of ICT five-day workshop scenario used to exercise the current CDCS-EMP implementation in preparation for the SSRC-IBMS pilot.

The scenario tests how the platform supports a realistic end-to-end business workflow across Catering, Procurement, Inventory, Expenses, Catering revenue eligibility and recognition, and financial reporting.

This is an **internal simulated UAT scenario**. It is not evidence that a real Ministry of ICT workshop took place.

The dates 26–30 October 2026 are intentionally used as simulated service dates. Catering Event #5 being marked `COMPLETED` before those dates is intentional test state and must not, by itself, be treated as a defect.

### 1.1 Objectives

The demonstration is intended to establish whether the current CDCS-EMP implementation can:

1. Register and manage a customer request for catering and hall hire.
2. Convert the request into an operational Catering Event.
3. Prepare and accept a commercial quotation.
4. Define and manage event requirements.
5. create Catering Purchase Requirements and hand them off to Procurement.
6. Process Purchase Requests and Purchase Orders.
7. Record partial and final receipts and reflect the resulting stock balance.
8. Manage event-related expenses and evidence of cost consumption.
9. Establish Catering revenue eligibility using appropriate business evidence.
10. Recognize eligible revenue as a separate, explicit operation.
11. Present meaningful financial summaries and event profitability when the required evidence exists.
12. Identify lifecycle, authorization, integration, and reporting gaps that require remediation before pilot readiness.

### 1.2 Scope boundaries

The scenario exercises the current implementation; it does not assume that every business capability is complete.

- Catering owns customer, request, event, quotation, event requirement, catering purchase requirement, production/delivery, and Catering revenue business context.
- Procurement owns Purchase Requests, Purchase Orders, procurement approvals, and purchasing transactions.
- Inventory owns stock, receipts, movements, and stock balances.
- Expense records support the recording and association of event-related costs.
- Financial reporting must respect the current revenue and cost recognition rules.
- The scenario must not be used to imply that a full ERP Finance capability has been implemented.

A visible status is evidence of the status displayed, not proof that every preceding business action or integration has behaved correctly. Acceptance requires verification of the relevant action and its resulting record.

---

## 2. Scenario identity and business context

| Attribute | Scenario value |
|---|---|
| Customer | Ministry of ICT |
| Workshop | Five-day workshop on South Sudan ICT Infrastructure |
| Simulated service period | 26–30 October 2026 |
| Attendance | 50 participants |
| Requested service | Catering and Hall Hire |
| Meals/services in the request | Breakfast, lunch, refreshments |
| Catering Request | Request #5 |
| Catering Event | Event #5 |
| Catering Quotation | Quotation #5 |
| Event Requirement | Requirement #8 |
| Item under procurement | Posho (maize flour), `POSHO-003` |
| Purchase Request | `PR-MICT-2026-001` |
| Purchase Order | `PO-MICT-2026-001` |
| Dedicated UAT database | `CDCS_EMP_UAT` |

### 2.1 Scenario timing rule

The service dates are simulated. The UAT scenario may deliberately place records in states that would normally follow the passage of real time.

Accordingly:

- Do not change the scenario dates merely because they are in the future.
- Do not downgrade Event #5 from `COMPLETED` solely because the service dates are in the future.
- Evaluate lifecycle behavior against the approved workflow and the recorded test actions, not the real-world calendar.
- If a function depends on event status, test its status prerequisite directly.
- Record the simulated nature of the scenario in demonstrations, evidence, and defect reports.

---

## 3. Authoritative end-to-end workflow

The intended business sequence is:

1. Register or identify the Ministry of ICT customer.
2. Submit the Catering Request.
3. Create the Catering Event from the request.
4. Prepare and accept the Catering Quotation.
5. Define event requirements and identify the fulfilment method for each requirement.
6. Create a Catering Purchase Requirement for items requiring procurement.
7. Hand off the purchase requirement to Procurement.
8. Create, approve, and process the Purchase Request.
9. Create, approve, and process the Purchase Order.
10. Record partial and final goods receipts.
11. Verify Inventory movements and balances.
12. Verify the Catering requirement's resulting lifecycle state.
13. Record event-related expenses.
14. Establish valid expense association and cost-consumption evidence where required.
15. Establish Catering revenue eligibility using event, quotation, delivery, amount, date, and supporting evidence.
16. Explicitly recognize eligible Catering revenue.
17. Verify reporting and profitability using recognized revenue and valid consumed costs.
18. Record the outcome of each test and identify unresolved gaps.

The sequence describes the target workflow. The execution log must distinguish completed steps from steps that remain unverified.

---

## 4. Customer request and event

### 4.1 Catering Request #5

The supplied UAT baseline shows:

| Field | Value |
|---|---|
| Customer | Ministry of ICT |
| Request date | 16 October 2026 |
| Requested service | Catering and Hall Hire |
| Service date | 26 October 2026 |
| Attendance | 50 |
| Requirements | Breakfast, lunch, refreshments |
| Notes | Five days’ workshop on South Sudan ICT Infrastructure — 26–30 October 2026 |
| Status | `Submitted` |

Acceptance criteria:

- The request identifies the correct customer and intended service.
- Attendance and service details are retained.
- The workshop period is clear in the request notes.
- Creating an Event from the request preserves the source relationship.
- The request remains distinguishable from the resulting Event.

A Catering Request is the initial demand. It is not itself the operational Event.

### 4.2 Catering Event #5

The supplied baseline shows:

| Field | Value |
|---|---|
| Customer | Ministry of ICT |
| Source request | Request #5 |
| Event date | 26 October 2026 |
| Service details | Catering and Hall Hire |
| Attendance | 50 |
| Operational notes | Five-day workshop on South Sudan ICT Infrastructure — 26–30 October 2026 |
| Status | `COMPLETED` |

Acceptance criteria:

- The Event links to Request #5 and the Ministry of ICT.
- Attendance and service details are correct.
- The Event lifecycle supports the actions required by the current workflow.
- The test recognizes `COMPLETED` as intentional simulated state.
- The Event status alone does not automatically recognize Catering revenue.

---

## 5. Catering quotation

### 5.1 Catering Quotation #5

The supplied baseline shows:

| Field | Value |
|---|---|
| Customer | Ministry of ICT |
| Catering Event | Event #5 |
| Quotation date | 16 October 2026 |
| Valid until | 25 October 2026 |
| Customer notes | Five-day workshop on South Sudan ICT Infrastructure |
| Status | `ACCEPTED` |

### 5.2 Quotation lines

| Description | Item reference | Quantity | Unit | Unit price (USD) | Line total (USD) |
|---|---|---:|---|---:|---:|
| Ministry of ICT workshop — breakfast | `BREAKFAST-001` | 50 | person | 5.00 | 250.00 |
| Ministry of ICT workshop — lunch | `LUNCH-002` | 50 | person | 15.00 | 750.00 |
| Ministry of ICT workshop — water | `WATER-003` | 150 | bottle | 1.00 | 150.00 |
| Ministry of ICT workshop — soda | `SODA-004` | 50 | bottle | 2.00 | 100.00 |
| **Total** | | | | | **1,250.00** |

Pricing summary:

- Subtotal: USD 1,250.00
- Adjustment: USD 0.00
- Total: USD 1,250.00

Acceptance criteria:

- The quotation is associated with the correct Event and customer.
- The line totals and quotation total reconcile.
- The accepted quotation is available as supporting commercial evidence.
- Acceptance of a quotation does not automatically establish or recognize revenue.
- If more than one accepted quotation exists for the Event, the behavior must be tested and any ambiguity recorded.

---

## 6. Event requirements and procurement

### 6.1 Event Requirement #8

The supplied baseline shows:

| Field | Value |
|---|---|
| Catering Event | Event #5 |
| Description | Posho (Maize flour) for Ministry of ICT workshop |
| Item reference | `POSHO-003` |
| Quantity | 150.000 kg |
| Fulfilment type | `PROCUREMENT` |
| Required by | 25 October 2026 |
| Status | `READY` |

### 6.2 Catering Purchase Requirement

The supplied baseline shows:

| Field | Value |
|---|---|
| Description | Posho (Maize flour) for Ministry of ICT workshop |
| Quantity | 150.000 kg |
| Status | `DRAFT` |
| Procurement reference | `CATERING-PR-fe23a058-344e-4291-9d0e-e5e3eb04143b` |

The linked Procurement Purchase Requirement shows:

| Field | Value |
|---|---|
| Reference | `CATERING-PR-fe23a058-344e-4291-9d0e-e5e3eb04143b` |
| Source module | `CATERING` |
| Source type | `CATERING_PURCHASE_REQUIREMENT` |
| Source reference | `fe23a058-344e-4291-9d0e-e5e3eb04143b` |
| Required by | 25 October 2026 |
| Status | `DRAFT` |

Acceptance criteria:

- Event Requirement #8 identifies the correct stock item, quantity, fulfilment method, and required-by date.
- The Catering Purchase Requirement retains its source identity and can be traced to Event Requirement #8.
- The procurement handoff creates or identifies the corresponding Procurement Purchase Requirement.
- The integration is idempotent according to the approved handoff contract.
- Catering and Procurement records remain distinct business records.
- The `READY` Event Requirement and `DRAFT` purchase requirement statuses must be investigated and documented; do not assume they are consistent or inconsistent without checking the implemented lifecycle rules.

---

## 7. Procurement and purchase order

### 7.1 Purchase Request

The supplied baseline shows:

| Field | Value |
|---|---|
| Reference | `PR-MICT-2026-001` |
| Purchase Requirement | `CATERING-PR-fe23a058-344e-4291-9d0e-e5e3eb04143b` |
| Request date | 19 October 2026 |
| Required by | 25 October 2026 |
| Status | `APPROVED` |
| Justification | Posho required for the Ministry of ICT five-day workshop on South Sudan ICT Infrastructure, 26–30 October 2026 |

The Purchase Request line specifies:

- Description: Posho (Maize flour) for Ministry of ICT workshop
- Item reference: `POSHO-003`
- Quantity: 150.000 kg
- Required by: 25 October 2026
- Notes reference Event #5, Event Requirement #8, and the workshop period.

Acceptance criteria:

- The Purchase Request is traceable to the correct Purchase Requirement.
- The approved status reflects the implemented approval workflow.
- The line quantity and item reference agree with the originating requirement.

### 7.2 Purchase Order

The supplied baseline shows:

| Field | Value |
|---|---|
| Reference | `PO-MICT-2026-001` |
| Supplier | UAT Test Supplier – Procurement A |
| Order date | 19 October 2026 |
| Expected delivery | 25 October 2026 |
| Status | `APPROVED` |
| Purchase Request | `PR-MICT-2026-001` |

Purchase Order line:

- Item: Posho (Maize flour), `POSHO-003`
- Ordered quantity: 150.000 kg
- Unit price: USD 2.00
- Total line amount: USD 300.00
- Receiving status: `FULLY RECEIVED`

Acceptance criteria:

- The Purchase Order is linked to the correct Purchase Request and supplier.
- Approval and receiving status are independently represented.
- The ordered quantity, unit price, and total amount reconcile.
- The system accurately reflects partial and final receiving activity.

---

## 8. Inventory receipt and stock verification

The supplied baseline reports two posted receipt movements at `UAT-LOC-001`, UAT Integration Test Location:

| Receipt reference | Quantity | Status | Recorded time |
|---|---:|---|---|
| `MICT-UAT-POSHO003-PARTIAL-20261019-001` | 50.000 kg | Posted | 19 October 2026, 21:26 |
| `MICT-UAT-POSHO003-FINAL-20261019-001` | 100.000 kg | Posted | 19 October 2026, 23:13 |
| **Total** | **150.000 kg** | | |

The supplied stock balance is:

| Stock item | Product code | Location | Quantity |
|---|---|---|---:|
| Posho (Maize flour) | `POSHO-003` | UAT Integration Test Location (`UAT-LOC-001`) | 150.000 kg |

Acceptance criteria:

- Both receipts are recorded and posted.
- The two receipt quantities sum to the ordered quantity.
- The resulting stock balance is consistent with the receipts and any other movements.
- The Purchase Order receiving state is consistent with the receipt history.
- Inventory stock is not treated as consumed catering cost merely because it has been received.
- The Catering requirement lifecycle and any fulfilment association are checked separately from stock receiving.

---

## 9. Expense records and cost evidence

The supplied UAT baseline includes 12 expense entries.

| # | Date | Description | Classification | Amount (USD) |
|---:|---|---|---|---:|
| 1 | 26 Oct 2026 | Workshop catering ingredients: rice, beans, vegetables and cooking oil; excludes Posho already recorded in inventory receipts. | Food Supplies | 420.00 |
| 2 | 26 Oct 2026 | Drinking water for workshop participants and catering team. | Beverages | 75.00 |
| 3 | 26 Oct 2026 | Tea, sugar, milk and bread for workshop tea breaks. | Tea Break Supplies | 110.00 |
| 4 | 26 Oct 2026 | Cooking fuel for initial workshop meal preparation. | Cooking Fuel | 95.00 |
| 5 | 27 Oct 2026 | Fresh vegetables and beans replenishment for workshop meals. | Food Supplies | 260.00 |
| 6 | 27 Oct 2026 | Local market transport and delivery of catering supplies. | Transport & Delivery | 60.00 |
| 7 | 28 Oct 2026 | Meat and eggs for workshop meals. | Food Supplies | 375.00 |
| 8 | 28 Oct 2026 | Temporary catering assistants for food preparation and service. | Casual Catering Labour | 250.00 |
| 9 | 29 Oct 2026 | Fruit and snack replenishment for workshop tea breaks. | Tea Break Supplies | 190.00 |
| 10 | 29 Oct 2026 | Dishwashing liquid, soap, refuse bags and cleaning supplies. | Cleaning & Sanitation | 85.00 |
| 11 | 30 Oct 2026 | Drinking water replenishment for the final workshop day. | Beverages | 75.00 |
| 12 | 30 Oct 2026 | Final-day fresh food and produce replenishment. | Food Supplies | 280.00 |
| | | **Total of supplied expense entries** | | **2,275.00** |

### 9.1 Known status of Expense #1

The supplied Expense Cost Association view reports:

| Field | Value |
|---|---|
| Description | Workshop catering ingredients: rice, beans, vegetables and cooking oil; excludes Posho already recorded in inventory receipts. |
| Amount | USD 420.00 |
| Expense date | 26 October 2026 |
| Association status | `ELIGIBLE` |
| Consumed at | Not recorded (`—`) |

Acceptance criteria:

- Expense records are identifiable and retain their classification, date, amount, and description.
- The expense-to-event association is explicitly established where required.
- Eligibility and consumption are distinct states or concepts.
- An expense in `ELIGIBLE` status with no consumption timestamp must not automatically be treated as a valid consumed cost.
- Received Posho and the USD 420 ingredient expense must not be double-counted.
- Other listed expenses must not be presumed associated, eligible, or consumed merely because they appear in the expense list.
- Any cost included in profitability must satisfy the applicable current cost-recognition rules.

---

## 10. Stage 8 — Catering revenue eligibility and recognition

Stage 8 adds explicit evidence and a controlled transition for Catering revenue.

The migration `e7a4c91d2f60` adds revenue eligibility evidence fields, including:

- `eligibility_quotation_id`
- `delivery_evidence`
- `eligibility_reason`
- `amount_adjustment_reason`
- `eligible_at`

The intended rules are:

1. The associated Catering Event must be `DELIVERED` or `COMPLETED`.
2. An authorized user explicitly confirms what catering service was actually delivered.
3. The proposed revenue amount must be supported by an accepted quotation.
4. If the delivered service differs from the accepted quotation amount, the adjustment must be documented.
5. The revenue record must identify the applicable revenue date, source business context, and eligibility evidence/reason.
6. Establishing eligibility transitions a valid revenue record from `DRAFT` to `ELIGIBLE`.
7. Recognition is a separate explicit action by an authorized user, transitioning revenue from `ELIGIBLE` to `RECOGNIZED`.
8. Neither acceptance of a quotation nor completion of an Event automatically recognizes revenue.

### 10.1 Revenue test for Event #5

The accepted quotation total is USD 1,250.00. It is the commercial reference amount for the scenario, not proof that revenue already exists or has been recognized.

The browser UAT must establish:

- Whether a Catering Revenue record exists for Event #5.
- Whether the record references the correct customer, Event, and accepted quotation.
- Whether service-delivery evidence and eligibility reason are required and validated.
- Whether the revenue date is recorded appropriately.
- Whether any amount difference requires a documented adjustment reason.
- Whether eligibility is explicitly established and stored.
- Whether recognition is a separate authorized action.
- Whether duplicate recognition is prevented.
- Whether reporting includes only recognized revenue according to the implemented rules.

No revenue record, eligibility status, or recognition outcome should be assumed before it is observed in UAT.

---

## 11. Profitability and reporting

The current intended profitability basis is recognized Catering revenue and valid consumed Catering costs.

The quotation amount of USD 1,250.00 and the sum of supplied expense entries of USD 2,275.00 are reconciliation inputs only. They are not, by themselves, a recognized-revenue total or a valid consumed-cost total.

The USD 300.00 Posho purchase value must be handled according to the actual costing model and must not be counted twice.

Acceptance criteria:

- Before valid recognized revenue and valid consumed cost records exist, profitability may correctly be unavailable.
- The interface should explain the reason for unavailable profitability rather than presenting an unsupported result.
- After valid evidence is established, reporting must use the system's applicable recognized revenue and consumed cost sources.
- Revenue, costs, and profitability must reconcile to their underlying records.
- The report must not infer consumption from inventory receipt or revenue recognition from Event completion.
- Any missing or inconsistent association must be recorded as a finding.

---

## 12. UAT execution and evidence rules

The companion document `SSRC-IBMS-MINISTRY-OF-ICT-WORKSHOP-UAT-EXECUTION-LOG.md` records actual test execution.

For each test, record:

- Test ID and date.
- Preconditions and starting record state.
- Action performed.
- Expected result.
- Actual observed result.
- Evidence or reference.
- Result: `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN`.
- Follow-up or defect reference.

A test is not `PASS` merely because a record exists. The relevant user action and resulting state must be observed.

Do not convert assumptions into facts. Clearly distinguish:

- Information supplied from the prior UAT session.
- Output directly observed in the current browser session.
- Migration status confirmed through the migration command.
- Unverified behavior that remains to be tested.

---

## 13. Environment safety and change control

The dedicated UAT database is `CDCS_EMP_UAT`. The normal `CDCS_EMP` database must not be used for this demonstration's database changes.

Until explicitly authorized:

- Do not reset, truncate, reseed, or recreate the UAT database.
- Do not delete or rewrite existing UAT records to make the scenario appear cleaner.
- Do not apply additional migrations without a focused target and explicit authorization.
- Do not modify application code while the current browser UAT is being established.
- Do not commit documentation until its contents and repository state have been verified.
- Keep the paused ICRC workshop scenario and its execution log unchanged.

The Stage 8 migration `e7a4c91d2f60` has been applied to `CDCS_EMP_UAT`; the reported post-upgrade revision was `e7a4c91d2f60 (head)`.

---

## 14. Completion criteria for the end-to-end demonstration

The demonstration can be considered complete only when:

1. Customer request and Event relationships are verified.
2. Quotation and commercial values reconcile.
3. Event requirements and procurement handoff behave according to the approved contract.
4. Purchase Request and Purchase Order lifecycle behavior is verified.
5. Receipt history and stock balances reconcile.
6. Requirement fulfilment behavior is understood and verified.
7. Expense records and event associations are verified.
8. Eligible costs are supported by valid consumption evidence.
9. Revenue eligibility evidence is complete and persisted.
10. Revenue recognition is explicit, authorized, and correctly reflected in reporting.
11. Profitability is correct when the required recognized revenue and consumed cost evidence exists.
12. All material findings are recorded.
13. Outstanding limitations are documented for pilot readiness decisions.

A completed demonstration does not imply that every wider CDCS-EMP or SSRC-IBMS capability is implemented. The outcome is an evidence-based assessment of the workflow covered by this scenario.

---

## 15. Relationship to the paused ICRC scenario

The ICRC five-day workshop at SSRC Juba is a separate scenario that is currently paused.

Its documents are not the source of truth for the Ministry of ICT workflow. Do not copy ICRC-specific assumptions, data, status values, or execution outcomes into this scenario unless a deliberate, separately documented decision is made.

**The Ministry of ICT scenario defined here is the authoritative internal end-to-end workflow for this SSRC-IBMS pilot demonstration.**

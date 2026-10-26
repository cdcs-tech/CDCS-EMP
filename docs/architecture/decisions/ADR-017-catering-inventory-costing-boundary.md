# ADR-017 — Catering Inventory Costing Boundary

* **Status:** Approved — Implementation in Progress
* **Decision Date:** 24 October 2026
* **Documentation Date:** 24 October 2026
* **Decision Type:** Architectural
* **Phase:** SSRC-IBMS Pilot Readiness
* **Module:** Catering
* **Scope:** Inventory valuation, event consumption cost attribution, direct event expenses, and Catering profitability reporting
* **Related ADRs:** ADR-008, ADR-011, ADR-012, ADR-014, ADR-015, PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md, PHASE-4-CATERING-REVENUE-CAPABILITY.md

---

## 1. Context

CDCS-EMP provides a Catering inventory foundation for stock items, locations, balances, movements, and transfers. Procurement maintains Purchase Orders and Purchase Order lines, including ordered quantities, units, unit prices, and line totals.

The Procurement-to-Inventory receipt path now validates persisted approved Purchase Orders and Purchase Order lines as the source of commercial valuation evidence. The receipt contract and Inventory persistence have been extended to support a receipt-level valuation snapshot, including Purchase Order and line provenance, actual received quantity, unit, unit price, currency, and price basis. A separate valuation status distinguishes physical receipt recording from successful valuation.

This establishes the purchase-currency and receipt-valuation foundation. It does not establish a complete inventory valuation algorithm, valued stock consumption, or finalized event profitability costing.

Catering also supports Expense Cost Associations and an Event Profitability service. Directly attributing the full value of a purchase to an event is not valid when that purchase supplies inventory used by multiple events or when some of the purchased stock remains unused.

For example, a bulk purchase of 300 kg of rice may supply several workshops. Charging the full purchase amount to the first workshop would overstate that event's cost and leave subsequent consumption without a defensible cost attribution.

The architecture must distinguish between:

* purchase commitments and purchase-price facts;
* physical inventory receipts and stock quantities;
* inventory valuation and remaining stock value;
* stock quantities consumed by individual events;
* direct event expenses that are not already represented by inventory costs; and
* reporting calculations derived from recognized revenue and valid attributable costs.

This decision establishes the approved costing boundary and guides implementation. The authoritative purchase-currency and receipt-valuation-snapshot foundation has been implemented, migrated, and schema-verified in the dedicated SSRC-IBMS pilot UAT database. Browser verification of the costing workflow remains outstanding, and this checkpoint does not claim that a complete inventory valuation algorithm or event-linked stock consumption costing has been implemented.

---

## 2. Decision

Catering costing shall follow a clear separation of responsibilities across Procurement, Inventory, Catering, and Reporting.

Procurement remains authoritative for Purchase Order and Purchase Order line commercial facts. Inventory remains authoritative for operational stock quantities and shall own inventory valuation and the cost basis used for valued stock movements. Catering shall identify the event requirements and event-linked consumption to which costs are attributable. Reporting shall derive event profitability from valid source records without duplicating their financial effects.

Weighted-average costing is the initial inventory valuation option to evaluate. It is not yet a finalized accounting policy or an implemented valuation algorithm.

The costing boundary shall preserve the following principles:

1. A bulk purchase may supply multiple Catering Events.
2. Unconsumed quantities remain in inventory with their corresponding inventory value.
3. Inventory cost attributed to an event is based on the valued quantity consumed for that event, not the full purchase amount.
4. Eligible direct event expenses remain supported where they represent genuinely direct costs.
5. The same economic cost must not be counted both as an inventory consumption cost and as a direct event expense.
6. Event profitability shall use valid, posted, valued consumption records and eligible direct expenses.
7. Missing or invalid cost data shall be reported as unavailable or incomplete rather than silently treated as zero.
8. Corrections and reversals shall preserve an auditable history.

---

## 3. Capability Responsibilities

### 3.1 Procurement

Procurement owns the commercial purchase facts, including:

* Purchase Orders and Purchase Order lines;
* ordered quantities and units;
* approved unit prices and line totals;
* Purchase Order approval state; and
* Purchase Order and line references communicated across integration boundaries.

Procurement shall not determine how much of a bulk purchase is consumed by a particular Catering Event.

The inventory receipt integration must establish a documented and validated way for Inventory to obtain the authoritative valuation basis for a receipt. A Purchase Order reference alone is not a valuation record.

### 3.2 Inventory

Inventory owns:

* physical stock quantities and stock movement history;
* receipt provenance, including Purchase Order and line references where applicable;
* inventory valuation and remaining stock value;
* the valuation basis of posted receipts and issues;
* the cost of valued quantities issued or consumed; and
* inventory valuation reconciliation.

Inventory shall not create a duplicate product master or take ownership of Procurement's Purchase Order workflow.

A receipt must not be considered fully valued merely because its physical quantity has been posted. Where valuation is missing or invalid, the system must preserve that distinction and prevent the affected cost from being represented as a valid zero-cost consumption.

### 3.3 Catering

Catering owns event requirements and the business attribution of consumption to Catering Events.

Event-linked stock consumption shall use structured, persisted references to the relevant Catering Event and, where applicable, its Event Requirement.

A free-text movement reference alone is not sufficient evidence of event cost attribution.

Catering shall distinguish between:

* stock allocated or reserved for fulfilment;
* stock physically issued or consumed;
* a posted and valued inventory cost attributable to an event; and
* a direct event expense that is not already represented by inventory consumption.

Allocation or fulfilment readiness alone shall not be treated as proof of consumption or as a cost recognized for event profitability.

### 3.4 Reporting

Reporting shall derive event profitability from authoritative revenue and cost records.

The reporting layer shall:

* include only valid recognized Catering revenue;
* include valid posted and valued inventory consumption attributable to the event;
* include eligible direct event expenses;
* prevent duplicate attribution of the same economic cost;
* preserve traceability from a reported cost to its source records; and
* distinguish a genuine zero result from missing, incomplete, or invalid cost data.

Reporting shall not independently create inventory valuation, consume stock, or persist a second copy of an underlying cost.

---

## 4. Bulk Purchase and Multiple-Event Example

Assume an illustrative receipt of 300 kg of rice with an approved uniform valuation of USD 2 per kg.

The initial inventory quantity is 300 kg and the initial inventory value is USD 600.

The following consumption is then recorded:

| Transaction | Quantity | Illustrative value |
|---|---:|---:|
| Initial inventory receipt | 300 kg | USD 600 |
| Workshop A consumption | 120 kg | USD 240 |
| Workshop B consumption | 80 kg | USD 160 |
| Remaining inventory | 100 kg | USD 200 |

The reconciliation is:

* Workshop A cost: USD 240.
* Workshop B cost: USD 160.
* Remaining inventory value: USD 200.
* Total reconciled value: USD 600.

The purchase value is not charged in full to either workshop. Each workshop receives the cost of its attributable consumption, and unused stock retains its value in inventory.

This example illustrates the costing boundary only. It assumes a uniform USD 2 per kg valuation for clarity and does not prescribe the final weighted-average calculation, rounding policy, or accounting treatment.

---

## 5. Direct Expense and Double-Counting Controls

An approved Expense may be associated with a Catering Event when it represents a valid direct cost of that event and satisfies the relevant approval and attribution rules.

An expense that represents a bulk inventory purchase must not also be counted in full as a direct event cost when its value is represented through inventory receipts and subsequent consumption.

The implementation shall define how the system identifies and prevents duplicate cost attribution across:

* approved direct Expense records;
* inventory receipt valuation;
* posted inventory issues and consumption; and
* Catering Event profitability calculations.

The system must preserve source identity and auditability so that the same underlying economic cost cannot be silently included twice.

This decision does not impose a universal one-Expense-to-one-Event constraint. A single purchase may legitimately supply stock consumed by multiple events.

---

## 6. Posting, Valuation, and Auditability

A cost may contribute to event profitability only when its source, attribution, posting state, and valuation are valid.

The intended event inventory costing flow is:

1. Receive stock and preserve receipt provenance.
2. Establish a valid inventory valuation basis.
3. Record a structured stock issue or consumption linked to the relevant event and requirement where applicable.
4. Post the physical stock effect through the established Inventory transaction boundary.
5. Determine and persist or otherwise reproducibly derive the valued cost of the posted consumption.
6. Make the attributable cost available to Catering profitability reporting.

**Valuation control:** A posted physical receipt with missing or unvalidated price or currency provenance must not be treated as valued. Its physical stock effect and valuation availability must remain distinguishable.

The final implementation must preserve transaction atomicity and idempotency across relevant posting operations.

Retries must not duplicate stock effects or cost attribution. Corrections, returns, and reversals must preserve an auditable relationship to the original transaction and must not silently rewrite historical results.

The precise transaction model and persistence design remain subject to detailed design and testing.

---

## 7. Initial Valuation Option

Weighted-average costing is the initial option to evaluate for inventory valuation.

The evaluation shall consider:

* how receipt value and quantity update the applicable average cost;
* how issues use the applicable valuation basis;
* how multiple receipts at different prices affect the average;
* how unit conversions and measurement precision are handled;
* how rounding differences are reconciled;
* how returns, wastage, damage, and adjustments affect quantity and value;
* how historical issues retain a defensible cost basis when later receipts change the average; and
* how valuation results are reconciled to receipt, movement, and balance records.

Weighted-average costing is not declared the final accounting policy by this ADR. The implementation must not proceed on the assumption that these mechanics have already been resolved.

---

## 8. Cost Availability and Reporting Semantics

The system shall distinguish at least the following conditions:

* **Available:** the relevant revenue and attributable costs are valid and sufficiently complete to calculate profitability.
* **Zero cost:** valid source records establish that the attributable cost is genuinely zero.
* **Unavailable:** the required cost or valuation data is absent or cannot be established.
* **Incomplete:** some relevant records exist, but required consumption, valuation, or reconciliation steps remain outstanding.
* **Invalid or conflicting:** the source records fail validation or disagree in a way that prevents a reliable result.

An unavailable or incomplete cost must not be silently substituted with zero. Reporting shall explain the condition sufficiently for a user to understand why profitability cannot yet be relied upon.

The detailed status model and user-facing presentation are implementation decisions to be defined consistently with the existing reporting and domain conventions.

---

## 9. Scope and Non-Goals

This ADR establishes a costing boundary; it does not implement the following:

* a full ERP Finance or General Ledger;
* a complete inventory valuation engine;
* a finalized weighted-average accounting policy;
* a universal constraint that each Expense belongs to only one event;
* automatic recognition of all procurement expenditure as an event cost;
* replacement of existing Procurement, Inventory, or Catering ownership boundaries; or
* retroactive changes to existing UAT records.

Implementation shall reuse the established domain, repository, service, authorization, integration, and transaction boundaries wherever suitable.

---

## 10. Outstanding Design Questions

The following decisions must be resolved during detailed design before the corresponding implementation is approved.

### 10.1 Valuation mechanics

Define the precise weighted-average calculation, valuation scope, treatment of multiple receipts, unit conversions, precision, rounding, and historical cost reproducibility. Confirm how negative balances and unvalued receipts are prevented or handled.

### 10.2 Decision: Authoritative Purchase Valuation and Receipt Valuation Snapshot

**Decision status:** Approved for implementation.

#### 10.2.1 Ownership and source of truth

Procurement owns the authoritative commercial valuation of an approved Purchase Order. Inventory owns the immutable valuation snapshot recorded against a physical stock receipt.

The approved Purchase Order and its persisted line items are the authoritative source for the purchase item, unit of measure, unit price, and currency. The receiving process must not accept caller-supplied commercial values as substitutes for those persisted records.

A physical receipt and its valuation evidence are related but distinct. Inventory may record a physically verified receipt when valid valuation evidence is unavailable, but that receipt must remain `UNVALUED` until the valuation requirements are satisfied through an explicitly defined and auditable process.

#### 10.2.2 Purchase Order currency

1. The `PurchaseOrder` model must contain a required currency field.
2. The initial supported currencies are `USD` and `SSP`.
3. Currency is established at Purchase Order level. Each `PurchaseOrderLine` inherits the currency of its parent Purchase Order; a separate line-level currency field must not be introduced.
4. Purchase Order creation must require an explicit supported currency. The system must not silently assume a currency when creating a new Purchase Order.
5. Currency and commercial terms must follow the existing Purchase Order lifecycle controls. Once a Purchase Order is approved, its currency and approved commercial terms must not be changed through ordinary update operations.
6. Existing Purchase Orders whose currency is unknown must not be silently backfilled as `USD`. Any legacy-data backfill must use an explicitly reviewed and justified mapping. Where currency cannot be established reliably, the record must remain unvalued for receipt-valuation purposes until the missing evidence is resolved.

#### 10.2.3 Finance commitment currency

The Finance commitment integration must use the currency persisted on the Purchase Order being committed.

A configurable default such as `USD` must not override the Purchase Order's currency or serve as a substitute for authoritative purchase valuation. The commitment payload must preserve the currency associated with the approved Purchase Order and must not imply currency conversion.

Currency conversion, exchange-rate sourcing, and exchange-rate accounting are outside the scope of this decision.

#### 10.2.4 Receiving validation

Before creating a receipt request with valuation evidence, the receiving handler must resolve and validate the persisted Purchase Order and Purchase Order line.

The receiving process must enforce all of the following:

1. The referenced Purchase Order exists and has status `APPROVED`.
2. The referenced Purchase Order line exists and belongs to that exact Purchase Order.
3. The received stock item and unit of measure agree with the approved Purchase Order line and its valid item mapping.
4. Unit price and currency are derived from the persisted approved Purchase Order and line, not trusted from request payloads or browser-supplied values.
5. Currency is explicitly established and is one of the supported currencies.
6. The valuation snapshot uses the actual quantity received for the receipt, not the full quantity ordered. Partial receipts must therefore retain their own received quantities and corresponding valuation evidence.
7. Missing, inconsistent, or invalid commercial evidence must not be fabricated or inferred from a configurable default.

A receiving request that fails physical or identity validation must be rejected according to the receiving workflow's validation rules. If physical receipt is valid but valuation evidence is missing or invalid, the system may record the physical receipt only where the existing Inventory workflow permits it, and the resulting record must remain `UNVALUED`.

#### 10.2.5 Inventory receipt valuation snapshot

Where valid purchase valuation evidence is available, the Procurement-to-Inventory integration must transmit the valuation facts required to establish a receipt snapshot, including:

- Purchase Order identity/reference.
- Purchase Order line identity/reference.
- Stock item identity/reference.
- Actual quantity received.
- Unit of measure.
- Approved unit price.
- Explicit currency.
- The applicable quantity/price basis needed to interpret the unit price consistently.

Inventory must persist the accepted valuation snapshot as historical evidence associated with the receipt. Later changes to a Purchase Order, its lines, or current catalogue data must not silently rewrite the historical snapshot.

A receipt without complete and valid valuation evidence must remain `UNVALUED`; the system must not assign a fabricated unit price, assume `USD`, or report the receipt as valued merely because physical stock was recorded.

#### 10.2.6 Idempotency and corrections

Receipt creation must preserve the existing idempotency guarantees. Repeating a request with the same idempotency key must not create a second stock effect or silently replace the original receipt's valuation snapshot with different commercial facts.

If a retry using an existing idempotency key supplies materially different receipt or valuation facts, the system must not silently treat those facts as an update to the original receipt. The request must follow the established idempotency-conflict or validation behaviour.

Corrections to an accepted receipt or its valuation snapshot must use an explicitly authorized and auditable correction, reversal, or adjustment workflow. Ordinary retries and edits must not mutate the historical snapshot.

#### 10.2.7 Costing boundary and exclusions

This decision establishes the source of purchase valuation and the persistence of receipt-level valuation evidence. It does not select or implement an Inventory costing algorithm.

Methods such as FIFO, weighted-average costing, or other inventory valuation methods require a separate decision where applicable. This decision also does not introduce currency conversion, exchange-rate accounting, or a full Finance costing implementation.

#### 10.2.8 Implementation status and validation evidence

**Status:** Purchase Order currency and receipt-level valuation-snapshot foundation implemented, migrated, schema-verified, and partially browser-verified in the dedicated pilot UAT database. The USD and SSP Purchase Order and receipt workflows have been browser-verified for the scenarios recorded below. Browser verification of receipt retry/idempotency behavior remains outstanding.

The following implementation work is in place:

1. Purchase Orders support explicit currency, initially `USD` and `SSP`, and Purchase Order creation requires an explicit supported currency.
2. Finance commitment integration uses the currency persisted on the Purchase Order rather than substituting a configured default.
3. Receiving validation resolves the persisted approved Purchase Order and Purchase Order line, verifies their relationship, and checks the stock item and unit against persisted line data.
4. The receipt contract supports complete valuation evidence or an explicitly unvalued receipt; it does not permit partial valuation evidence to be treated as complete.
5. Inventory receipt persistence supports the Purchase Order and line references, received unit, unit price, currency, price basis, and valuation status.
6. Receipt idempotency and focused regression coverage protect against duplicate stock effects and unsupported changes to existing receipt facts.
7. Purchase Order Details displays the parent Purchase Order currency in the Unit Price and Total Amount headings. The Add/Edit Purchase Order Line form also identifies the parent currency beside the unit-price field and in the calculated-total guidance. Currency remains a Purchase Order-level attribute, not an independently selected line attribute.

The following migrations have been applied to `CDCS_EMP_UAT`:

| Revision | Migration | Purpose |
|---|---|---|
| `f2a8c6d94170` | `add_stock_movement_valuation_status.py` | Adds explicit stock movement valuation status. |
| `a7c4d19e62b8` | `add_purchase_order_currency.py` | Adds nullable Purchase Order currency without a legacy currency backfill. |
| `c3d9e71a4b62` | `add_stock_movement_receipt_valuation_snapshot.py` | Adds receipt-level valuation snapshot fields. |

**Migration verification evidence:**

- Database: `CDCS_EMP_UAT`.
- SQL Server: `KASONGO`.
- Database revision and repository migration head: `c3d9e71a4b62`.
- The `purchase_orders.currency` column exists and is nullable.
- At the time of schema verification, all four existing Purchase Orders had `NULL` currency. No currency was silently assigned to legacy records.
- The `stock_movements.valuation_status` column exists and is non-nullable.
- At the time of schema verification, all four existing Stock Movements had status `NOT_APPLICABLE`, with no null valuation statuses.
- All seven expected receipt-valuation columns were present on `stock_movements`.

**Browser verification evidence in `CDCS_EMP_UAT`:**

1. Purchase Order `ADR-017-VAL-001` was created with currency `USD`, approved, and used for two partial receipts. Both receipts were posted and recorded as `VALUED`, with the Purchase Order and line references, received unit, unit price `2.50`, currency `USD`, and price basis `PO_LINE_UNIT_PRICE` persisted in their receipt snapshots. The combined received quantity was 10 kg against 100 kg ordered.
2. Purchase Order `ADR-017-VAL-002` was created with currency `SSP`, approved, and used for a full receipt of 2 kg at a unit price of `5000.00`. The posted receipt was recorded as `VALUED`, with the Purchase Order and line references, unit `kgs`, currency `SSP`, unit price `5000.00`, and price basis `PO_LINE_UNIT_PRICE` persisted in the snapshot.
3. The Purchase Order Details pages for the USD and SSP scenarios were browser-verified to display the corresponding currency in both the Unit Price and Total Amount headings.
4. The Add/Edit Purchase Order Line form was browser-verified on a DRAFT Purchase Order. It displayed the Purchase Order currency in the context line, beside the unit-price field, and in the calculated-total guidance.
5. These checks establish the observable behavior for the tested scenarios. They do not establish that receipt retries have been browser-verified or that a complete inventory costing algorithm, valued consumption, or event-linked stock consumption costing has been implemented.

**Regression evidence:**

- The previously recorded project regression suite passed with 3,510 tests.
- The latest focused Purchase Order Details and Purchase Order line-route regression passed with **31 tests** after the currency-display change.
- The latest focused Procurement contract and Inventory receipt integration regression passed with **116 tests** across `test_contracts.py`, `test_inventory_receipt_idempotency.py`, `test_inventory_receipt_provider.py`, `test_receiving_execution.py`, and `test_partial_receipt_handling.py`.
- Passing automated tests provide regression evidence; they do not replace browser verification of workflows not actually exercised in the browser.

**Remaining validation and implementation:**

1. Verify receipt retry behavior against `CDCS_EMP_UAT` and confirm that retries do not duplicate stock effects or silently replace an existing receipt's valuation snapshot.
2. Verify missing or incomplete valuation evidence through the observable workflow, where a suitable scenario can be exercised without compromising existing UAT records.
3. Continue detailed design and implementation of inventory valuation mechanics, valued consumption, and event-linked cost attribution as separate capabilities.
4. Continue to record UI limitations and failed checks rather than treating unverified behavior as complete.

**Acceptance criterion:** A receipt may be represented as valued only when its valuation is traceable to valid, persisted, approved Purchase Order commercial evidence and the applicable receipt snapshot is persisted consistently. Otherwise, where physical receipt is permitted, its valuation status must remain `UNVALUED`. The USD and SSP receipt scenarios and currency-display behavior documented above are browser-verified for the tested cases; receipt retry/idempotency behavior remains unverified in the browser.

### 10.3 Cost timing and finalization

Define when a stock issue becomes a cost attributable to an event, how provisional or incomplete consumption is represented, and when event profitability is sufficiently complete for final review.

Define how changes after event completion affect previously reported results.

### 10.4 Consumption, returns, and wastage

Define the structured issue/consumption record, its event and requirement references, authorization, posting, idempotency, reversal, and audit behavior.

Define treatment for returned stock, spoilage, wastage, damage, shortages, adjustments, and stock consumed without a valid event attribution.

### 10.5 Direct expense eligibility

Define which direct expenses may contribute to event profitability and how expenses representing inventory purchases are distinguished from genuinely direct event costs.

Define safeguards against duplicate attribution across expenses and inventory valuation.

### 10.6 Reconciliation and reporting

Define the reconciliation controls between receipt valuation, stock movements, physical balances, inventory value, event consumption, direct expenses, and reported event costs.

Define the status model for unavailable, incomplete, invalid, and zero-cost results.

### 10.7 Migration and existing records

Determine how existing stock balances, receipts, movements, Expense Cost Associations, and historical event costs will be treated where valuation data or structured event linkage is missing.

No historical value shall be invented merely to make an event profitability result available.

---

The implementation sequence is:

1. Establish authoritative Purchase Order currency and the receipt-valuation contract. **Foundation implemented and migrated; browser verification pending.**
2. Complete browser verification of Purchase Order currency, receipt provenance, valuation status, receipt snapshot persistence, and idempotent retries.
3. Define the inventory valuation algorithm, including the selected method, unit conversions, precision, rounding, reconciliation, and treatment of unvalued receipts.
4. Define structured event-linked stock issue and consumption, including posting, authorization, idempotency, reversal, and audit behavior.
5. Implement and verify inventory valuation and the cost basis of posted issues or consumption.
6. Attribute valid valued consumption to Catering Events.
7. Refine direct Expense eligibility and duplicate-cost prevention.
8. Update Event Profitability calculations and presentation.
9. Verify multi-event bulk consumption, remaining stock value, retries, reversals, missing valuation, and genuine zero-cost cases.

Each increment shall receive focused tests before broader regression testing. Existing uncommitted work and UAT records must remain protected throughout implementation.

---

## 12. Consequences

### Positive consequences

* Establishes clear ownership across Procurement, Inventory, Catering, and Reporting.
* Supports bulk purchases shared across multiple events.
* Prevents treating an entire purchase as the cost of one event when stock remains or is consumed elsewhere.
* Creates a path to auditable event cost attribution.
* Explicitly addresses duplicate-cost risks and missing valuation data.
* Keeps detailed valuation mechanics separate from the approved high-level boundary.

### Trade-offs and constraints

* Reliable event profitability depends on inventory valuation and structured consumption capabilities that are not established by the inspected receipt path.
* Additional contracts, persistence, transaction controls, and tests will be required.
* Historical records may remain incomplete until a deliberate migration or reconciliation approach is approved.
* Weighted-average costing still requires detailed design and must not be represented as a finalized accounting policy.

---

## 13. Approval

The Catering Costing Boundary is approved as the proposed CDCS-EMP architecture baseline on 24 October 2026.

Weighted-average costing is approved as the initial valuation option to evaluate, not as a finalized accounting policy or completed implementation.

This ADR governs subsequent detailed design unless superseded by a reviewed and approved architecture decision.

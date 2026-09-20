# Phase 2.2 — Procurement ↔ Inventory Integration Contract

**Document Type:** Architecture Decision / Integration Contract
**Status:** APPROVED / ACTIVE / LOCKED
**Phase:** Phase 2.2 — Purchasing & Expense Management
**Component:** Procurement ↔ Inventory Integration
**Decision Authority:** Project Architecture Review
**Decision Date:** 19 September 2026
**Authoritative Location:** `docs/architecture/decisions/PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

---

## 1. Decision Summary

This document establishes the authoritative integration contract between the CDCS-EMP Procurement/Purchasing capability and the Catering Inventory capability.

The integration shall allow a completed physical supplier delivery associated with a Procurement Purchase Order to communicate a receiving/stock-effect request to Inventory.

The integration shall preserve strict domain ownership:

- Procurement owns supplier-facing procurement information and the Purchase Order lifecycle.
- Inventory owns physical stock state, stock movements, stock balances, and stock-effect posting.
- Procurement may initiate and communicate receiving information.
- Inventory remains the sole authority for determining and recording the resulting physical stock effect.

The approved conceptual flow is:

```text
Purchase Order
      ↓
Supplier Fulfillment
      ↓
Physical Receiving / Handover
      ↓
Procurement ↔ Inventory Integration Contract
      ↓
Inventory Receipt Posting
      ↓
StockMovement(RECEIPT)
      ↓
StockBalance Effect
```

An approved Purchase Order by itself shall **not** create a stock effect.

A stock effect shall occur only when an actual physical receipt is communicated through the approved integration boundary and successfully posted by Inventory.

---

# 2. Architectural Context

Phase 2 architecture establishes Procurement/Purchasing and Inventory as distinct bounded business capabilities.

Procurement is responsible for:

- Supplier management;
- Purchase Requirements;
- Purchase Requests;
- Purchase Request Lines;
- Purchase Orders;
- Purchase Order Lines;
- Procurement workflow;
- Supplier-facing procurement information; and
- Procurement lifecycle coordination.

Inventory is responsible for:

- Stock Items;
- Inventory Locations;
- Stock Balances;
- Stock Movements;
- physical stock quantities;
- inventory movement posting; and
- resulting physical stock state.

The integration therefore exists to communicate a business effect across the boundary rather than to merge the two domains.

The integration must not introduce a second Inventory subsystem inside Procurement.

---

# 3. Existing Enterprise Integration Infrastructure

The integration shall reuse the existing enterprise Integration Framework.

The following enterprise contracts are authoritative:

```text
app/core/integration/models.py
app/core/integration/service.py
app/core/integration/providers/base.py
app/core/integration/providers/registry.py
```

The integration execution path is:

```text
Domain Receiving Request
        ↓
IntegrationRequest
        ↓
IntegrationService.execute()
        ↓
IntegrationProviderRegistry
        ↓
Inventory Integration Provider
        ↓
Inventory-Owned Service
        ↓
IntegrationResponse
        ↓
IntegrationResult
```

The following existing enterprise contracts shall be reused without modification:

- `IntegrationRequest`
- `IntegrationResponse`
- `IntegrationResult`
- `IntegrationService`
- `BaseIntegrationProvider`
- `IntegrationProviderRegistry`

No Procurement-specific fields shall be added to `IntegrationRequest`.

The Procurement ↔ Inventory business contract shall be represented by a domain-specific payload carried by the generic `IntegrationRequest`.

---

# 4. Integration Provider Identity

The Procurement-to-Inventory receiving provider shall use a stable enterprise provider identity.

The approved provider identity is:

```text
inventory
```

The receiving operation shall use the explicit operation identity:

```text
receive_purchase_order
```

Therefore the generic integration envelope shall conceptually contain:

```text
provider  = "inventory"
operation = "receive_purchase_order"
payload   = PurchaseOrderReceiptRequest
```

The provider shall implement the existing:

```text
BaseIntegrationProvider.execute(
    IntegrationRequest
) -> IntegrationResponse
```

contract.

The provider shall be registered through:

```text
IntegrationProviderRegistry
```

No separate Procurement-to-Inventory dispatcher or provider registry shall be introduced.

---

# 5. Domain Receiving Contract

The Procurement ↔ Inventory receiving payload shall represent a physical receipt against one Purchase Order Line.

The authoritative conceptual contract is:

```text
PurchaseOrderReceiptRequest
```

The payload shall contain the following business information.

## 5.1 Purchase Order Reference

```text
purchase_order_reference
```

Required.

This identifies the originating Procurement Purchase Order.

The reference is an external business-document reference from the perspective of Inventory.

It shall not create a foreign-key dependency from Inventory to Procurement.

---

## 5.2 Purchase Order Line Reference

```text
purchase_order_line_reference
```

Required.

This identifies the Purchase Order Line against which the physical receipt is being recorded.

The reference shall allow Inventory to retain Procurement context without importing Procurement domain persistence relationships.

A Purchase Order Line remains a Procurement concept.

---

## 5.3 Stock Item Reference

```text
stock_item_reference
```

Required.

This identifies the Inventory Stock Item that is physically being received.

The Stock Item is an Inventory-owned concept.

Procurement and Inventory shall not assume that a Purchase Order Line and a Stock Item are inherently the same entity.

The mapping between the procurement line and the inventory item shall therefore be explicit.

---

## 5.4 Inventory Location Reference

```text
inventory_location_reference
```

Required.

This identifies the Inventory Location into which the physical stock is being received.

Inventory Location remains entirely Inventory-owned.

Procurement shall not maintain or duplicate the Inventory Location master.

---

## 5.5 Quantity Received

```text
quantity_received
```

Required.

The value represents the physical quantity received for the specified Purchase Order Line and Stock Item.

The quantity shall be greater than zero.

The integration shall not support zero or negative receipt quantities.

A receipt represents a positive Inventory `RECEIPT` movement.

---

## 5.6 Unit

```text
unit
```

Required.

The unit communicates the business unit associated with the received quantity.

This contract shall not introduce a general Unit-of-Measure conversion engine.

The receiving implementation shall not silently convert between incompatible units.

Any future UOM conversion capability shall require a separate approved architectural decision.

---

## 5.7 Occurrence Timestamp

```text
received_at
```

Required.

This represents the time at which the physical receipt occurred.

It provides business context for the Inventory movement occurrence.

Inventory shall remain responsible for the authoritative posting timestamp.

---

## 5.8 Receiving Reference

```text
receiving_reference
```

Required.

This is the business reference identifying the particular physical receiving event.

It shall provide a stable reference that can be used for traceability and duplicate detection.

One Purchase Order may have multiple receiving references.

---

## 5.9 Idempotency Key

```text
idempotency_key
```

Required.

The idempotency key uniquely identifies the intended receiving operation.

The same physical receiving operation submitted more than once with the same idempotency identity shall not result in multiple stock postings.

The exact persistence mechanism for idempotency shall be implemented within the approved integration/Inventory boundary without changing the domain ownership decision established here.

---

## 5.10 Notes

```text
notes
```

Optional.

This provides supplementary receiving context.

Notes shall not be used to embed Procurement, Finance, supplier-invoice, payment, accounting, or Inventory-specific transaction structures.

---

# 6. Contract Ownership

The receiving contract has deliberately split ownership.

## Procurement supplies

- Purchase Order reference;
- Purchase Order Line reference;
- receiving business reference;
- physical quantity communicated by the receiving process;
- receiving timestamp;
- supplier/procurement context where required; and
- integration identity/idempotency information.

## Inventory determines and owns

- Stock Item validity;
- Inventory Location validity;
- whether the requested physical stock effect is valid;
- Stock Movement creation;
- Stock Movement type;
- Stock Movement posting;
- Stock Balance mutation;
- resulting stock quantity;
- Inventory transaction atomicity; and
- final physical stock state.

Procurement shall never directly update:

```text
StockMovement
StockBalance
```

through repository or model mutation.

---

# 7. Cross-Module Identity Strategy

The integration shall use explicit business references rather than direct database relationships.

The approved identity model is:

```text
Procurement Purchase Order
        │
        │ purchase_order_reference
        ↓
Receiving Contract
        │
        ├── purchase_order_line_reference
        ├── stock_item_reference
        └── inventory_location_reference
```

No direct foreign key shall be introduced between Procurement models and Inventory models solely to support this integration.

In particular:

- Purchase Order shall not receive an Inventory Stock Item foreign key.
- Purchase Order Line shall not receive an Inventory Stock Item foreign key as part of this integration contract.
- Inventory Stock Movement shall not receive a Procurement Purchase Order foreign key.
- Inventory Stock Balance shall not receive a Procurement Purchase Order foreign key.
- Inventory Location shall remain independent of Procurement.

The existing Inventory `StockMovement.reference` field may carry the relevant external Procurement/receiving business reference.

---

# 8. Purchase Order Line and Stock Item Mapping

A Purchase Order Line and an Inventory Stock Item represent different business concepts.

A Purchase Order Line represents:

> what Procurement ordered.

A Stock Item represents:

> what Inventory physically manages.

Therefore:

```text
PurchaseOrderLine ≠ StockItem
```

The receiving integration must explicitly communicate the Stock Item associated with the physical receipt.

The integration shall not assume that:

```text
PurchaseOrderLine.id == StockItem.id
```

or that an implicit database relationship exists.

Any future persistent item-mapping capability shall be considered separately if implementation requirements demonstrate that it is necessary.

---

# 9. Inventory Location Ownership

Inventory Location remains an Inventory-owned concept.

Procurement shall provide an Inventory Location reference when receiving requires location-specific stock posting.

Procurement shall not:

- create Inventory Locations;
- modify Inventory Locations;
- maintain duplicate Inventory Location records;
- maintain Inventory balances by location; or
- implement location-specific stock rules.

Inventory shall validate the supplied location and determine whether the receipt can be posted there.

---

# 10. Receiving Semantics

## 10.1 Purchase Order Approval Is Not Receipt

An approved Purchase Order represents a Procurement commitment.

It does not represent physical stock.

Therefore:

```text
Purchase Order APPROVED
        ≠
Inventory RECEIPT
```

No stock effect shall be generated merely because a Purchase Order reaches `APPROVED`.

---

## 10.2 Physical Receipt Creates the Candidate Stock Effect

A physical supplier delivery creates the business event that may result in an Inventory receipt.

The integration therefore begins from physical receiving information rather than Purchase Order workflow status alone.

---

## 10.3 Partial Receiving

Partial receiving is explicitly supported.

For example:

```text
Purchase Order Line ordered quantity = 100

Receipt 1 = 40
Receipt 2 = 35
Receipt 3 = 25
```

may result in three separate receiving operations.

Each receiving operation shall have its own receiving reference and idempotency identity.

The integration shall not require a Purchase Order Line to be fully received in one transaction.

---

## 10.4 Multiple Receipts

One Purchase Order may generate multiple physical receipts.

One Purchase Order Line may therefore be associated with multiple receiving operations.

The integration shall preserve the distinction between:

```text
Purchase Order
Purchase Order Line
Physical Receipt
Inventory Stock Movement
```

---

# 11. Over-Receipt and Business Validation

The initial integration contract shall not establish a new Procurement quantity-reconciliation subsystem.

Inventory shall validate the physical stock effect from an Inventory perspective.

Procurement-side business rules concerning ordered quantity, outstanding quantity, supplier fulfillment, or acceptance of over-receipt shall remain Procurement-owned.

Where such validation is required to prevent an invalid physical receipt, it shall be implemented through an explicit integration/business rule rather than by introducing Procurement foreign keys into Inventory.

Any future requirement for:

- tolerance percentages;
- over-receipt approval;
- under-receipt approval;
- back-order management;
- supplier fulfillment reconciliation; or
- receipt acceptance workflows

shall be treated as an extension requiring its own design decision.

---

# 12. Inventory Stock Effect

A successful receiving operation shall result in an Inventory `RECEIPT` movement.

The resulting conceptual operation is:

```text
Receipt Contract
      ↓
Inventory Validation
      ↓
StockMovement
    type = RECEIPT
      ↓
POST
      ↓
StockBalance update
```

The Inventory service remains responsible for the stock-effect operation.

Procurement shall not construct or persist the `StockMovement` itself.

---

# 13. Stock Movement Reference

The existing Inventory `StockMovement.reference` field shall be used to retain external receiving/procurement context.

The reference may contain the receiving reference or another approved stable external business identifier.

This preserves traceability without embedding Procurement-specific persistence structures into Inventory.

The Inventory movement shall therefore remain an Inventory movement while retaining sufficient external context to answer:

> Which Procurement receiving operation caused this physical stock effect?

---

# 14. Idempotency and Duplicate Receiving

Duplicate protection is mandatory.

A receiving operation may be retried because of:

- network interruption;
- provider timeout;
- client retry;
- application retry;
- integration response loss; or
- duplicate submission.

A retry must not create a second physical stock effect.

The approved invariant is:

```text
One physical receiving operation
        ↓
One successful Inventory stock effect
```

Repeated delivery of the same integration request using the same idempotency identity shall produce an equivalent already-processed outcome rather than another `RECEIPT` posting.

Idempotency must be evaluated before creating a new physical stock effect.

The implementation shall not rely solely on user interface behavior to prevent duplicates.

---

# 15. Idempotency Identity

The idempotency identity shall be based on the receiving operation rather than merely the Purchase Order.

This is necessary because:

```text
One Purchase Order
        ↓
Multiple legitimate receipts
```

must be supported.

Therefore the following are not sufficient by themselves:

```text
purchase_order_reference
purchase_order_line_reference
```

The receiving operation requires its own stable identity.

The `idempotency_key` supplied by the receiving contract shall provide that identity.

A repeated request with the same key must be treated as the same integration operation.

A new physical receipt must use a new idempotency key.

---

# 16. Integration Response Semantics

The provider shall return the existing enterprise `IntegrationResponse`.

A successful receiving operation shall communicate:

- success;
- receiving/integration reference;
- resulting Inventory movement reference where available;
- relevant Inventory result information; and
- metadata required for traceability.

A repeated idempotent request shall return an outcome indicating that the receiving operation has already been processed, without creating a second stock effect.

A failed operation shall communicate:

- failure;
- an appropriate integration error;
- a meaningful message;
- relevant metadata; and
- no claim of successful Inventory posting.

The existing `IntegrationResult` shall remain the outer execution result returned by `IntegrationService.execute()`.

No Procurement-specific replacement for `IntegrationResult` shall be introduced.

---

# 17. Failure Semantics

Failure must preserve Inventory consistency.

If Inventory cannot successfully post the receipt:

```text
No StockMovement POST
No StockBalance mutation
No partial Inventory stock effect
```

The receiving integration shall not report success unless the authoritative Inventory stock effect has successfully completed.

The integration shall not implement manual compensation logic inside Procurement to reverse an Inventory transaction.

Inventory's existing transaction boundary remains authoritative.

---

# 18. Transaction Boundary

The integration shall not introduce distributed transactions.

The approved transaction model is:

```text
Integration Provider
        ↓
Inventory Service
        ↓
Existing TransactionManager
        ↓
Inventory Stock Effect
```

Inventory shall coordinate the atomic operation covering:

- validation;
- balance retrieval/creation;
- resulting balance calculation;
- Stock Movement creation;
- Stock Movement posting;
- required metadata;
- commit.

If any required Inventory operation fails, the Inventory transaction shall roll back.

The Procurement integration layer shall not implement:

- a second transaction manager;
- manual rollback;
- distributed transaction coordination;
- database triggers;
- cross-database transaction orchestration; or
- repository-owned transaction management.

---

# 19. Existing Inventory Posting Boundary

The existing Inventory architecture establishes that Stock Movement posting is a service/application responsibility.

The receiving integration must therefore ultimately invoke the Inventory-owned service boundary.

The integration must not bypass that boundary by directly invoking:

```text
StockBalanceRepository
StockMovementRepository
```

to create the physical stock effect.

The approved dependency direction is:

```text
Procurement
    ↓
Enterprise Integration Contract
    ↓
Inventory Integration Provider
    ↓
Inventory Service
    ↓
Inventory Repository / TransactionManager
```

and not:

```text
Procurement
    ↓
Inventory Repository
```

---

# 20. Procurement Purchase Order Workflow Boundary

The Procurement Purchase Order workflow remains independent of Inventory receiving.

The Purchase Order workflow currently contains:

```text
DRAFT
SUBMITTED
APPROVED
REJECTED
CANCELLED
```

with its approved workflow operations.

Inventory receiving shall not be treated as another Purchase Order workflow transition.

In particular:

```text
Inventory Receipt
≠
Purchase Order Workflow Transition
```

The receipt integration may occur while a Purchase Order is in an appropriate Procurement state, subject to Procurement business rules, but Inventory receipt posting is an Inventory operation rather than a Procurement workflow operation.

Any future requirement to automatically update Purchase Order status based on receiving shall require a separate approved workflow/integration decision.

---

# 21. Receiving Is Not a New Procurement Workflow

This integration does not create:

```text
purchase_order.receive
```

as a Procurement workflow operation.

Receiving is a cross-domain business interaction whose physical effect belongs to Inventory.

The integration contract therefore remains separate from the existing Purchase Order workflow command matrix:

```text
purchase_order.submit
purchase_order.approve
purchase_order.reject
purchase_order.return
purchase_order.cancel
```

No receiving command shall be added to that matrix by this decision.

---

# 22. Generic Procurement Receipt Entity

A generic Procurement `Receipt` or `ProcurementReceipt` entity is deliberately not introduced by this decision.

The existing architecture is sufficient to represent the integration using:

- Purchase Order;
- Purchase Order Line;
- receiving reference;
- receiving contract payload; and
- Inventory Stock Movement.

A dedicated Procurement receipt entity may be considered later only if implementation demonstrates a genuine need for Procurement-owned receiving records beyond the integration contract.

Such a requirement would require a separate architectural decision.

---

# 23. Security and Authorization

The integration shall reuse the enterprise security and authorization architecture.

No parallel authorization mechanism shall be created.

The integration provider and receiving execution boundary shall operate under the existing enterprise authorization model.

Where integration execution is exposed through an enterprise execution context, authorization shall follow the established application-to-enterprise authorization boundary, including the approved application execution authorization adapter.

The integration shall not:

- bypass authorization;
- create a second permission engine;
- create a private Inventory authorization system;
- bypass governance;
- bypass audit; or
- bypass enterprise execution controls.

---

# 24. Audit and Traceability

The integration shall reuse the existing enterprise integration and audit infrastructure.

Relevant integration execution shall remain traceable through:

- integration request identity;
- provider;
- operation;
- receiving reference;
- idempotency key;
- Purchase Order reference;
- Purchase Order Line reference;
- Inventory Stock Movement reference; and
- integration result.

The existing enterprise integration events remain authoritative:

```text
integration.request
integration.result
integration.failure
```

No parallel Procurement ↔ Inventory event framework shall be introduced.

---

# 25. Event Boundary

Integration events describe integration activity.

They shall not replace the authoritative Inventory Stock Movement ledger.

The distinction is:

```text
Integration Event
    = communication/execution trace

StockMovement
    = authoritative physical inventory effect
```

A successful integration event therefore does not itself constitute the Inventory stock record.

The Stock Movement remains authoritative for the actual physical stock effect.

---

# 26. Governance

The integration remains subject to enterprise governance.

The following principles are mandatory:

1. Domain ownership must remain explicit.
2. Cross-module dependencies must remain controlled.
3. Business transactions must remain inside their owning module.
4. Integration infrastructure must remain centralized.
5. Auditability must be preserved.
6. Authorization must be enforced through enterprise security.
7. Physical inventory state must remain Inventory-owned.
8. Procurement must not become an Inventory subsystem.
9. Inventory must not become a Procurement subsystem.

---

# 27. Data Ownership Matrix

| Data / Concept | Procurement | Inventory | Integration Role |
|---|---|---|---|
| Supplier | Owns | References only where needed | Context |
| Purchase Order | Owns | References | Source document |
| Purchase Order Line | Owns | References | Source line |
| Receiving Reference | Provides/owns operational context | Retains reference | Correlation |
| Idempotency Key | Provides/request identity | Enforces duplicate protection | Duplicate control |
| Stock Item | References where known | Owns | Target |
| Inventory Location | References | Owns | Target |
| Quantity Received | Communicates | Validates physical stock effect | Input |
| Stock Movement | No ownership | Owns | Result |
| Stock Balance | No ownership | Owns | Result |
| Purchase Order Workflow | Owns | No ownership | Separate lifecycle |
| Inventory Posting | No ownership | Owns | Integration target |
| Financial Expense | No ownership | No ownership | Excluded |

---

# 28. Integration Contract Invariants

The following invariants are locked.

### Invariant 1 — No automatic receipt from approval

```text
Purchase Order APPROVED
≠
Inventory RECEIPT
```

### Invariant 2 — Inventory owns physical stock

```text
Only Inventory may authoritatively post stock effects.
```

### Invariant 3 — No direct cross-module foreign keys

```text
Procurement ↔ Inventory
= explicit integration references
```

### Invariant 4 — Positive receipt

```text
quantity_received > 0
```

### Invariant 5 — Partial receipt supported

```text
One PO / PO Line
→ multiple receiving operations
```

### Invariant 6 — Idempotent receipt

```text
One receiving operation
→ at most one Inventory stock effect
```

### Invariant 7 — Atomic Inventory posting

```text
Successful receipt
→ complete Inventory effect

Failed receipt
→ no partial Inventory effect
```

### Invariant 8 — Workflow separation

```text
Inventory receipt
≠
Purchase Order workflow transition
```

### Invariant 9 — Centralized integration infrastructure

```text
Existing Integration Framework
→ reused
```

### Invariant 10 — No repository-level cross-module posting

```text
Procurement
→ Integration Provider
→ Inventory Service
→ Inventory transaction boundary
```

---

# 29. Error Categories

The integration may use the existing enterprise integration exception hierarchy where applicable, including:

- `IntegrationRequestException`;
- `IntegrationResponseException`;
- `IntegrationDeliveryException`;
- `IntegrationGovernanceException`; and
- other existing integration exceptions appropriate to the failure.

Inventory business-rule failures shall remain Inventory-domain failures and shall be normalized into the enterprise integration response/result boundary.

The integration shall not create a new generic exception hierarchy.

---

# 30. Explicit Exclusions

The following are outside this decision.

## Procurement exclusions

- redesign of Purchase Order;
- redesign of Purchase Order workflow;
- supplier redesign;
- Purchase Request redesign;
- Procurement receiving subsystem;
- supplier invoice processing;
- supplier payment;
- Accounts Payable;
- financial settlement.

## Inventory exclusions

- redesign of Stock Item;
- redesign of Inventory Location;
- redesign of Stock Balance;
- redesign of Stock Movement;
- stock valuation;
- warehouse management;
- batch/lot management;
- serial-number management;
- expiry management;
- replenishment;
- advanced stock reservation;
- advanced warehouse allocation;
- general Inventory redesign.

## General exclusions

- Finance integration;
- Expense Management integration;
- General Ledger;
- chart of accounts;
- tax;
- payroll;
- invoicing;
- payment processing;
- supplier settlement;
- UOM conversion;
- distributed transactions;
- speculative custom locking;
- duplicate Inventory infrastructure;
- parallel event framework;
- parallel audit framework;
- parallel authorization framework;
- generic Procurement Receipt entity unless separately justified.

---

# 31. Approved Implementation Sequence

The implementation shall proceed in the following controlled sequence:

```text
1. Integration Contract Foundation
       ↓
2. Receiving Execution Boundary
       ↓
3. Inventory Receipt Adapter / Provider
       ↓
4. Partial Receipt Handling
       ↓
5. Idempotency / Duplicate Receipt Protection
       ↓
6. Integration Events & Audit
       ↓
7. Integration Security / Governance Verification
       ↓
8. End-to-End Integration Verification
```

Each implementation stage shall preserve the architectural invariants established by this document.

No implementation stage shall silently expand the scope into Finance, Expense Management, Inventory redesign, or Procurement redesign.

---

# 32. Implementation Contract Boundary

The eventual implementation shall preserve the following conceptual API boundary:

```text
IntegrationRequest
{
    provider: "inventory",
    operation: "receive_purchase_order",
    payload: PurchaseOrderReceiptRequest,
    metadata: ...
}
```

The domain payload shall conceptually contain:

```text
PurchaseOrderReceiptRequest
{
    purchase_order_reference,
    purchase_order_line_reference,
    stock_item_reference,
    inventory_location_reference,
    quantity_received,
    unit,
    received_at,
    receiving_reference,
    idempotency_key,
    notes
}
```

The exact Python representation, validation implementation, serialization approach, and provider registration details shall be determined during implementation using established CDCS-EMP conventions.

They shall not alter the architectural contract defined here.

---

# 33. Result Boundary

The expected successful flow is:

```text
IntegrationRequest
        ↓
IntegrationService.execute()
        ↓
Inventory Provider
        ↓
Inventory Service
        ↓
Inventory Transaction
        ↓
StockMovement(RECEIPT)
        ↓
StockBalance update
        ↓
IntegrationResponse(success)
        ↓
IntegrationResult(success)
```

The expected failure flow is:

```text
IntegrationRequest
        ↓
Inventory Provider
        ↓
Inventory Validation / Posting
        ↓
Failure
        ↓
Inventory Transaction Rollback
        ↓
IntegrationResponse(failure)
        ↓
IntegrationResult(failure)
```

No failed result may be interpreted as a successful physical receipt.

---

# 34. Architectural Rationale

This design provides a narrow and reusable integration boundary without weakening the bounded-module architecture.

It allows Procurement to communicate what was physically received while preventing Procurement from acquiring Inventory persistence responsibilities.

It also prevents Inventory from becoming dependent on Procurement's database structure.

The existing enterprise Integration Framework provides the necessary infrastructure for:

- request identity;
- provider resolution;
- operation execution;
- response normalization;
- result handling;
- integration events;
- audit;
- exceptions; and
- governance.

The existing Inventory service architecture provides the necessary authority for:

- validation;
- stock movement creation;
- balance mutation;
- transaction coordination;
- posting; and
- physical stock consistency.

Consequently, no parallel infrastructure is justified.

---

# 35. Architectural Decision

The following decisions are hereby locked:

1. **Procurement ↔ Inventory receiving shall use the existing enterprise Integration Framework.**
2. **`IntegrationRequest` shall remain a generic enterprise envelope.**
3. **A domain-specific receiving payload shall carry Procurement ↔ Inventory business data.**
4. **The Inventory provider identity shall be `inventory`.**
5. **The receiving operation shall be `receive_purchase_order`.**
6. **Inventory shall remain authoritative for physical stock effects.**
7. **Inventory `StockMovement(RECEIPT)` shall represent the authoritative physical receipt effect.**
8. **Inventory `StockBalance` shall be mutated only through Inventory-owned service logic.**
9. **Procurement shall not directly mutate Inventory models or repositories.**
10. **No direct Procurement ↔ Inventory foreign keys shall be introduced for this integration.**
11. **Purchase Order and Purchase Order Line references shall remain explicit integration references.**
12. **Stock Item and Inventory Location references shall remain Inventory-owned references.**
13. **Partial receiving shall be supported.**
14. **Multiple receiving operations may relate to the same Purchase Order or Purchase Order Line.**
15. **Every receiving operation shall have a stable receiving identity and idempotency key.**
16. **Duplicate integration delivery shall not create duplicate physical stock effects.**
17. **Inventory's existing transaction boundary shall remain authoritative.**
18. **No distributed transaction mechanism shall be introduced.**
19. **Failed Inventory posting shall leave no partial Inventory stock effect.**
20. **Purchase Order workflow and Inventory receiving shall remain separate lifecycles.**
21. **Receiving shall not be added as a Purchase Order workflow transition by this decision.**
22. **Existing enterprise security, authorization, governance, audit, and integration events shall be reused.**
23. **No parallel integration, authorization, audit, or event infrastructure shall be created.**
24. **No generic Procurement Receipt entity shall be introduced unless separately justified.**
25. **Finance and Expense Management remain outside this integration.**

---

# 36. Verification Criteria

The implementation derived from this contract shall eventually demonstrate, through targeted automated tests and appropriate integration verification, that:

- a valid Purchase Order receiving request reaches the Inventory provider;
- the provider accepts the approved integration envelope;
- the receiving payload is validated;
- the correct Stock Item is identified;
- the correct Inventory Location is identified;
- a positive `RECEIPT` movement is created;
- the Inventory balance is updated atomically;
- the resulting Stock Movement retains the external receiving reference;
- partial receipts are supported;
- multiple receipts against one Purchase Order are supported;
- duplicate delivery using the same idempotency key does not double-post stock;
- a failed posting produces no partial Inventory state;
- Procurement does not directly mutate Inventory persistence;
- no direct Procurement ↔ Inventory foreign keys are required;
- authorization is enforced through enterprise security;
- integration request/result/failure activity remains auditable;
- Purchase Order workflow remains separate from Inventory receipt posting; and
- the existing enterprise Integration Framework remains the infrastructure boundary.

---

# 37. Related Architecture Decisions

This decision shall be read together with:

- `ADR-001-phase-2-business-module-architecture.md`
- `ADR-006-catering-security-governance-integration.md`
- `ADR-008-catering-inventory-domain-boundary.md`
- `ADR-009-inventory-stock-item-architecture.md`
- `ADR-010-inventory-location-architecture.md`
- `ADR-011-inventory-stock-balance-architecture.md`
- `ADR-012-inventory-stock-movement-ledger-architecture.md`
- `ADR-014-inventory-repository-service-boundary.md`
- `ADR-015-inventory-transaction-posting-boundary.md`
- `ADR-016-application-execution-authorization-adapter.md`
- `PHASE-2-AUTHORITATIVE-ROADMAP.md`
- `PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

---

# 38. Relationship to Phase 2.2 Architecture

This document is subordinate to and consistent with:

`PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

The Phase 2.2 architecture establishes the ownership rule that Procurement/Purchasing and Inventory remain distinct capabilities and that Procurement may communicate receiving through an explicit integration boundary while Inventory remains responsible for physical stock effects.

This document makes that integration boundary concrete.

No provision of this document shall be interpreted as transferring Inventory ownership to Procurement or Procurement ownership to Inventory.

---

# 39. Status

**APPROVED / ACTIVE / LOCKED**

This document constitutes the approved architectural contract for the Procurement ↔ Inventory integration.

Implementation may proceed against this contract without reopening the architectural approval decision, provided that implementation remains within the boundaries and invariants established above.

Any material deviation from the following requires a new architectural decision:

- domain ownership;
- integration infrastructure;
- direct foreign-key strategy;
- receiving identity;
- idempotency semantics;
- Inventory stock-effect ownership;
- transaction boundary;
- Purchase Order workflow boundary;
- security/governance boundary; or
- excluded financial/Inventory/Procurement responsibilities.

---

## 40. Final Architectural Statement

The authoritative CDCS-EMP Procurement ↔ Inventory boundary is:

```text
                    PROCUREMENT
                         │
                         │
                  Purchase Order
                         │
                         ↓
               Supplier Fulfillment
                         │
                         ↓
              Physical Receiving
                         │
                         ↓
        ┌────────────────────────────────┐
        │ Enterprise Integration Layer  │
        │                                │
        │ IntegrationRequest             │
        │ provider = inventory            │
        │ operation = receive_purchase_order │
        │ payload = receiving contract    │
        └────────────────────────────────┘
                         │
                         ↓
              Inventory Provider
                         │
                         ↓
                Inventory Service
                         │
                         ↓
               Transaction Boundary
                         │
                         ↓
              StockMovement(RECEIPT)
                         │
                         ↓
                  StockBalance
```

**Procurement communicates the physical receiving context.
Inventory determines, records, and owns the physical stock effect.**

This separation is the authoritative architectural rule for Phase 2.2 Procurement ↔ Inventory integration.

## Implementation Status

Phase 2.2 Procurement ↔ Inventory Integration — Receiving Execution Boundary
- Status: Completed
- Procurement receiving is represented by ReceivePurchaseOrderCommand.
- Operation: procurement.purchase_order.receive.
- Permission: PROCUREMENT.PURCHASE_ORDER.RECEIVE.
- Receiving remains outside the Purchase Order workflow.
- The handler validates that the Purchase Order is APPROVED.
- The handler constructs PurchaseOrderReceiptRequest.
- Delivery occurs through enterprise IntegrationService.
- Procurement does not directly mutate Inventory state.
- Inventory remains authoritative for physical stock effects.
- Verification: 21 focused tests passed; 39 Procurement tests passed; 436 combined Core Execution/Core Integration/Procurement tests passed.
- No direct Procurement → Inventory repository access was introduced.

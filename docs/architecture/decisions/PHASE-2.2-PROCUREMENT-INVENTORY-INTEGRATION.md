# Phase 2.2 — Procurement ↔ Inventory Integration

**Document Type:** Architecture Decision
**Status:** APPROVED / ACTIVE / LOCKED
**Phase:** Phase 2.2 — Purchasing & Expense Management
**Component:** Procurement ↔ Inventory Integration
**Decision Authority:** Project Architecture Review
**Decision Date:** 19 September 2026
**Authoritative Location:** `docs/architecture/decisions/PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION.md`

---

## 1. Purpose

This document establishes the authoritative architectural boundary for integration between the CDCS-EMP Procurement/Purchasing capability and the Catering Inventory capability.

The purpose is to allow Procurement to communicate supplier fulfillment and physical receiving information to Inventory while preserving strict ownership of physical stock effects within Inventory.

This decision deliberately separates:

- Procurement purchasing lifecycle;
- supplier-facing procurement information;
- physical receiving communication;
- Inventory stock-effect posting;
- Inventory stock balances; and
- future financial treatment.

The integration shall provide a controlled cross-module boundary without creating direct database coupling or duplicating Inventory functionality inside Procurement.

---

# 2. Architectural Decision Summary

The approved architecture is:

```text
Purchase Order
      ↓
Supplier Fulfillment
      ↓
Physical Receiving / Handover
      ↓
Procurement ↔ Inventory Integration Boundary
      ↓
Inventory Receipt Posting
      ↓
StockMovement(RECEIPT)
      ↓
StockBalance Effect
```

The fundamental ownership rule is:

> **Procurement may initiate and communicate receiving information, but Inventory remains authoritative for physical stock effects, stock movements, stock balances, and physical stock state.**

Procurement shall therefore never become an Inventory subsystem.

Inventory shall likewise not assume ownership of Procurement purchasing lifecycle concepts.

---

# 3. Existing Domain Ownership

## 3.1 Procurement Ownership

Procurement owns:

- Suppliers;
- Purchase Requirements;
- Purchase Requests;
- Purchase Request Lines;
- Purchase Orders;
- Purchase Order Lines;
- procurement workflow;
- sourcing;
- supplier-facing purchasing information;
- procurement lifecycle; and
- Procurement-side receiving context.

Procurement does not own:

- Stock Balances;
- Stock Movements;
- Inventory Locations;
- physical stock quantities;
- Inventory posting;
- financial expenses;
- invoices;
- payments;
- accounting ledgers.

---

## 3.2 Inventory Ownership

Inventory owns:

- Stock Items;
- Inventory Locations;
- Stock Balances;
- Stock Movements;
- physical stock quantities;
- inventory movement posting;
- resulting physical stock state;
- inventory transaction boundaries; and
- inventory-specific validation.

Inventory does not own:

- Suppliers;
- Purchase Requests;
- Purchase Orders;
- Procurement workflow;
- supplier negotiations;
- supplier payments;
- financial expenses;
- accounting ledgers.

---

# 4. Why the Integration Exists

Procurement and Inventory represent different business concerns.

Procurement answers:

> What did the organization order, from whom, and under what procurement lifecycle?

Inventory answers:

> What physical stock was actually received, where was it received, and what is the resulting stock balance?

These questions are related but are not the same transaction.

Therefore:

```text
Purchase ≠ Receipt
Receipt ≠ Expense
Physical Receipt ≠ Financial Expense
Purchase Order ≠ Stock Movement
```

The integration exists to communicate the relationship between these concerns without merging their ownership.

---

# 5. Purchase Order Does Not Create Stock

An approved Purchase Order is a procurement commitment.

It is not proof that goods physically arrived.

Therefore:

```text
Purchase Order APPROVED
        ≠
Inventory RECEIPT
```

No Inventory stock effect shall be generated merely because a Purchase Order:

- is created;
- is submitted;
- is approved; or
- otherwise changes Procurement workflow state.

A physical receipt must be communicated through the receiving/integration boundary before Inventory may post the corresponding stock effect.

---

# 6. Receiving Responsibility

Receiving responsibility is deliberately divided.

### Procurement is responsible for communicating:

- which Purchase Order is being fulfilled;
- which Purchase Order Line is involved;
- receiving context;
- supplier fulfillment context where relevant;
- quantity physically received;
- receiving reference;
- receiving occurrence information; and
- other Procurement-owned context required by the integration contract.

### Inventory is responsible for:

- validating Stock Item;
- validating Inventory Location;
- validating physical stock-effect requirements;
- creating the Stock Movement;
- posting the Stock Movement;
- updating Stock Balance;
- maintaining inventory transaction integrity; and
- maintaining authoritative physical stock state.

This creates the following boundary:

```text
Procurement
   │
   │ Receiving Context
   ↓
Integration Boundary
   │
   │ Physical Stock Effect Request
   ↓
Inventory
```

---

# 7. Approved Cross-Module Flow

The complete conceptual flow is:

```text
1. Procurement Purchase Order
             ↓
2. Supplier Fulfillment
             ↓
3. Physical Delivery
             ↓
4. Receiving / Handover
             ↓
5. Procurement ↔ Inventory Integration Contract
             ↓
6. Inventory Validation
             ↓
7. Inventory Receipt Posting
             ↓
8. StockMovement(RECEIPT)
             ↓
9. StockBalance Update
```

The integration contract is therefore a boundary between business capabilities rather than a new business module.

---

# 8. Cross-Module Dependency Strategy

Procurement and Inventory shall not establish direct foreign-key dependencies merely to support this integration.

The approved strategy is:

```text
Procurement Business Entity
        ↓
Explicit External Reference
        ↓
Integration Contract
        ↓
Inventory Business Entity
```

The integration shall use explicit business references for:

- Purchase Order;
- Purchase Order Line;
- Stock Item;
- Inventory Location;
- receiving operation; and
- integration identity.

No direct Procurement-to-Inventory relational ownership shall be introduced by this integration.

---

# 9. Purchase Order and Purchase Order Line References

Inventory may retain references to Procurement documents for traceability.

However:

```text
PurchaseOrder
PurchaseOrderLine
```

remain Procurement-owned entities.

Inventory shall not import or own their database relationships.

The existing Inventory `StockMovement.reference` capability provides an appropriate mechanism for retaining external business-document context.

---

# 10. Purchase Order Line and Stock Item Distinction

A Purchase Order Line and a Stock Item are distinct concepts.

A Purchase Order Line represents:

> what Procurement ordered.

A Stock Item represents:

> what Inventory physically manages.

Therefore:

```text
PurchaseOrderLine ≠ StockItem
```

The integration must provide an explicit mapping/reference when a Purchase Order Line results in a physical Inventory receipt.

The architecture shall not assume that their identifiers are identical.

---

# 11. Inventory Location Boundary

Inventory Location remains entirely Inventory-owned.

Procurement may communicate a receiving location where required, but Procurement shall not:

- create Inventory Locations;
- modify Inventory Locations;
- maintain duplicate locations;
- maintain location balances; or
- implement Inventory location rules.

Inventory remains responsible for validating and using the location during stock posting.

---

# 12. Partial Receiving

Partial receiving is explicitly supported.

A Purchase Order or Purchase Order Line may be fulfilled through multiple physical receiving operations.

Example:

```text
Ordered: 100 units

Receipt 1: 40 units
Receipt 2: 35 units
Receipt 3: 25 units
```

Each receiving operation is an independent physical event.

The integration must therefore not assume:

```text
One Purchase Order
        =
One Receipt
```

or:

```text
One Purchase Order Line
        =
One Stock Movement
```

Multiple legitimate Inventory receipt movements may arise from one Procurement document.

---

# 13. Receiving Identity

Each physical receiving operation requires its own stable identity.

The receiving identity must be distinct from:

- Purchase Order identity;
- Purchase Order Line identity; and
- Inventory Stock Item identity.

This is necessary to support:

- partial receiving;
- retries;
- duplicate protection;
- audit;
- reconciliation; and
- integration tracing.

The detailed identity and idempotency contract is established in:

`PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

---

# 14. Idempotency

Duplicate receiving must be prevented.

Integration delivery may be retried because of:

- network interruption;
- timeout;
- lost response;
- application retry;
- provider retry; or
- duplicate submission.

The architecture therefore establishes the invariant:

```text
One physical receiving operation
        ↓
At most one Inventory stock effect
```

The detailed idempotency key and duplicate-handling rules are defined by the Integration Contract document.

No implementation shall rely solely on user-interface controls to prevent duplicate stock posting.

---

# 15. Inventory Stock Effect Ownership

Inventory remains the sole authority for physical stock effects.

The authoritative effect is:

```text
StockMovement
        ↓
StockBalance
```

Procurement shall not directly create or modify:

- Stock Movement records;
- Stock Balance records;
- Inventory balances; or
- Inventory posting metadata.

Procurement communicates the requested physical effect through the integration boundary.

Inventory determines whether and how that physical effect may be posted.

---

# 16. Existing Inventory Transaction Boundary

The existing Inventory transaction architecture remains authoritative.

Inventory stock posting is coordinated through the existing service/application boundary and enterprise transaction infrastructure.

The integration shall not create:

- a distributed transaction manager;
- a Procurement transaction manager for Inventory;
- repository-owned cross-module transactions;
- database triggers;
- manual rollback frameworks; or
- speculative custom locking.

The transaction boundary remains:

```text
Inventory Service
       ↓
Existing TransactionManager
       ↓
Inventory Stock Effect
```

---

# 17. Atomicity and Failure

Inventory receipt posting shall be atomic.

A successful operation must result in the complete Inventory effect.

A failed operation must result in no partial Inventory stock state.

Conceptually:

```text
Success:
Receipt
  ↓
StockMovement
  ↓
StockBalance
  ↓
COMMIT
```

Failure:

```text
Receipt
  ↓
Validation / Posting Failure
  ↓
ROLLBACK
  ↓
No partial stock effect
```

The Procurement integration layer shall not attempt to compensate for an incomplete Inventory transaction.

---

# 18. Integration Infrastructure

The integration shall reuse the existing enterprise Integration Framework.

The approved infrastructure includes:

- `IntegrationRequest`;
- `IntegrationResponse`;
- `IntegrationResult`;
- `IntegrationService`;
- `BaseIntegrationProvider`;
- `IntegrationProviderRegistry`;
- enterprise integration events;
- enterprise integration exceptions;
- enterprise audit; and
- enterprise governance.

The execution path is:

```text
IntegrationRequest
        ↓
IntegrationService.execute()
        ↓
IntegrationProviderRegistry
        ↓
Inventory Integration Provider
        ↓
Inventory Service
```

No parallel cross-module integration framework shall be introduced.

---

# 19. Integration Provider

The Inventory integration provider shall implement the existing enterprise provider contract.

The provider is responsible for adapting the cross-module receiving request into Inventory-owned business operations.

The provider shall not become a second Inventory service layer.

The provider's role is:

```text
Integration Adapter
       ↓
Inventory Service
```

not:

```text
Integration Adapter
       ↓
Direct StockMovement / StockBalance mutation
```

---

# 20. Workflow Boundary

Procurement Purchase Order workflow remains Procurement-owned.

Inventory receipt posting remains an Inventory business operation.

Therefore:

```text
Purchase Order Workflow
        ≠
Inventory Receipt Lifecycle
```

The Inventory receipt operation shall not automatically become a new Procurement workflow state by this architectural decision.

In particular, this decision does not introduce:

```text
purchase_order.receive
```

as a Procurement workflow operation.

Any future requirement to synchronize Purchase Order workflow status with receipt completion must be separately designed and approved.

---

# 21. Events and Audit

The integration shall reuse enterprise integration events and audit infrastructure.

Relevant integration activity may be represented through:

```text
integration.request
integration.result
integration.failure
```

Integration events provide execution/communication traceability.

They do not replace Inventory's authoritative Stock Movement ledger.

Therefore:

```text
Integration Event
    = integration activity

StockMovement
    = physical stock effect
```

No duplicate Procurement ↔ Inventory event or audit framework shall be created.

---

# 22. Security and Governance

The integration shall use the established enterprise security, authorization, governance, and audit architecture.

No parallel:

- permission engine;
- role engine;
- authorization framework;
- governance framework; or
- audit framework

shall be introduced.

Where execution authorization is required, the approved application-to-enterprise execution authorization architecture shall remain authoritative.

The integration must not bypass existing enterprise authorization.

---

# 23. Contract Boundary

The detailed business receiving contract is intentionally separated from the generic enterprise integration envelope.

The generic envelope remains:

```text
IntegrationRequest
{
    provider,
    operation,
    payload,
    headers,
    metadata,
    request_id,
    created_at,
    timeout
}
```

The receiving business contract is carried by:

```text
payload
```

This separation prevents Procurement-specific business fields from contaminating the reusable enterprise Integration Framework.

The exact receiving payload, provider identity, operation identity, reference strategy, idempotency rules, response semantics, and duplicate handling are defined in:

`PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

---

# 24. No Generic Procurement Receipt Entity

This integration does not introduce a new generic:

```text
ProcurementReceipt
```

entity.

The initial architecture can support receiving using:

- Purchase Order;
- Purchase Order Line;
- receiving business reference;
- integration contract; and
- Inventory Stock Movement.

A dedicated Procurement receipt entity may only be introduced if later implementation demonstrates a genuine Procurement-owned requirement that cannot be satisfied by the approved contract.

Such a change requires a separate architecture decision.

---

# 25. Financial Boundary

Finance and Expense Management are explicitly outside this integration.

A physical receipt does not automatically represent:

- an expense;
- an invoice;
- a payment;
- a supplier settlement;
- an accounts-payable transaction; or
- a general-ledger posting.

Therefore:

```text
Physical Receipt
        ≠
Financial Expense
```

Any future financial treatment shall occur through the approved Procurement ↔ Finance and Expense Management boundaries.

---

# 26. Inventory Redesign Exclusion

This decision does not redesign Inventory.

The existing Inventory architecture remains authoritative for:

- Stock Item;
- Inventory Location;
- Stock Balance;
- Stock Movement;
- movement posting;
- transaction coordination; and
- physical stock state.

The integration shall adapt to the existing Inventory architecture rather than changing Inventory ownership to accommodate Procurement.

---

# 27. Explicit Exclusions

The following are excluded from this integration decision:

### Procurement

- Procurement domain redesign;
- Purchase Order redesign;
- Purchase Request redesign;
- supplier redesign;
- supplier invoice processing;
- supplier payment;
- Accounts Payable;
- supplier settlement.

### Inventory

- Inventory domain redesign;
- Stock Item redesign;
- Inventory Location redesign;
- Stock Balance redesign;
- Stock Movement redesign;
- warehouse management;
- stock valuation;
- batch/lot management;
- serial management;
- expiry management;
- replenishment;
- advanced reservation;
- UOM conversion.

### Finance

- General Ledger;
- chart of accounts;
- financial expenses;
- invoices;
- payments;
- tax;
- payroll;
- financial settlement.

### Infrastructure

- distributed transactions;
- duplicate transaction managers;
- parallel integration framework;
- parallel event framework;
- parallel audit framework;
- parallel authorization framework.

---

# 28. Approved Implementation Sequence

The integration shall be implemented in the following controlled sequence:

```text
1. Integration Contract Foundation
       ↓
2. Receiving Execution Boundary
       ↓
3. Inventory Receipt Adapter / Provider
       ↓
4. Partial Receipt Handling
       ↓
5. Duplicate / Idempotency Handling
       ↓
6. Events & Audit
       ↓
7. Security / Governance Verification
       ↓
8. End-to-End Integration Verification
```

Each stage shall be implemented and verified independently.

No implementation shall silently expand the scope of the integration.

---

# 29. Implementation Principles

Implementation shall follow these principles:

1. Reuse existing enterprise infrastructure.
2. Keep Procurement and Inventory domain ownership separate.
3. Keep cross-module references explicit.
4. Keep physical stock authority inside Inventory.
5. Keep Procurement workflow inside Procurement.
6. Keep Inventory transaction ownership inside Inventory.
7. Keep integration infrastructure inside the enterprise Integration Framework.
8. Prevent duplicate physical stock effects.
9. Preserve auditability and traceability.
10. Avoid speculative abstractions.
11. Avoid duplicate business logic.
12. Avoid direct repository-level cross-module manipulation.
13. Avoid financial scope expansion.

---

# 30. Verification Expectations

Implementation derived from this architecture shall eventually demonstrate that:

- Procurement can communicate a valid physical receiving operation;
- the enterprise Integration Framework resolves the appropriate Inventory provider;
- Inventory receives explicit Procurement references;
- Inventory remains authoritative for stock posting;
- a successful receipt produces an Inventory `RECEIPT` Stock Movement;
- the Stock Balance changes only through Inventory-owned logic;
- partial receiving works;
- multiple receipts against one Purchase Order work;
- duplicate receiving does not double-post stock;
- failed receipt posting leaves no partial Inventory state;
- no direct Procurement ↔ Inventory foreign key is required;
- Procurement does not directly mutate Inventory persistence;
- Purchase Order workflow remains separate from Inventory receiving;
- enterprise authorization is preserved;
- integration events/audit remain available; and
- the full CDCS-EMP regression suite remains stable.

---

# 31. Related Architecture Decisions

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
- `PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

---

# 32. Architectural Invariants

The following invariants are locked:

### 32.1 Procurement does not own Inventory

```text
Procurement
    ≠
Inventory
```

### 32.2 Inventory owns physical stock

```text
StockMovement
+
StockBalance
+
Physical Stock State
=
Inventory Authority
```

### 32.3 Purchase Order approval does not create stock

```text
PO APPROVED
≠
STOCK RECEIVED
```

### 32.4 Receiving is an integration boundary

```text
Procurement Receiving Context
        ↓
Integration
        ↓
Inventory Physical Effect
```

### 32.5 No direct database coupling

```text
Procurement ↔ Inventory
=
Explicit Integration References
```

### 32.6 Partial receiving is valid

```text
One PO
→ Multiple Receipts
```

### 32.7 Duplicate delivery is not duplicate stock

```text
One Receiving Operation
→ At Most One Stock Effect
```

### 32.8 Inventory posting is atomic

```text
Success → Complete Stock Effect
Failure → No Partial Stock Effect
```

### 32.9 Workflow boundaries remain separate

```text
Procurement Workflow
≠
Inventory Receipt Operation
```

### 32.10 Existing enterprise infrastructure remains authoritative

```text
Enterprise Integration Framework
+
Enterprise Security
+
Enterprise Audit
+
Inventory Transaction Boundary
=
Approved Integration Foundation
```

---

# 33. Final Architectural Decision

The Procurement ↔ Inventory integration is hereby established as a controlled cross-module integration boundary.

Procurement shall communicate actual physical receiving context.

Inventory shall determine, validate, record, and own the resulting physical stock effect.

The integration shall reuse the existing enterprise Integration Framework and shall not introduce direct Procurement ↔ Inventory foreign keys or parallel infrastructure.

The detailed receiving contract is established separately in:

`PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

Together, the two documents establish the complete architecture:

```text
PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION.md
        │
        │ Overall architecture,
        │ ownership and boundaries
        ↓
PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md
        │
        │ Exact integration contract,
        │ payload, identity, idempotency
        │ and execution semantics
        ↓
Implementation
```

---

# 34. Status

**APPROVED / ACTIVE / LOCKED**

This document constitutes the authoritative architectural decision for the overall Procurement ↔ Inventory integration boundary.

The companion Integration Contract document constitutes the authoritative detailed contract for implementation.

Implementation may proceed against these decisions without reopening architectural approval, provided implementation remains within the boundaries, ownership rules, invariants, and exclusions established by these documents.

Any material deviation from these decisions requires a new architecture decision.

---

# 35. Final Architectural Statement

> **Procurement communicates what was purchased and what was physically received; Inventory remains the authoritative owner of what physically entered stock.**

The system shall therefore preserve the following boundary:

```text
                     PROCUREMENT
                          │
                    Purchase Order
                          │
                    Supplier Fulfillment
                          │
                  Physical Receiving
                          │
                          ▼
             ┌────────────────────────┐
             │ Enterprise Integration │
             │        Boundary        │
             └────────────────────────┘
                          │
                          ▼
                      INVENTORY
                          │
                 Inventory Validation
                          │
                 StockMovement(RECEIPT)
                          │
                    StockBalance
                          │
                          ▼
                 Physical Stock State
```

This boundary is the authoritative Phase 2.2 architecture for Procurement ↔ Inventory integration.

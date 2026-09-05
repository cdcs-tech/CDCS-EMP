# ADR-013 — Inventory Stock Transfer Architecture

**Status:** Planned for documentation
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory stock transfer ownership, transfer semantics, lifecycle, posting orchestration, source/destination balance effects, movement-ledger integration, and transaction atomicity

**Related ADRs:**

* ADR-001 — Phase 2 Business Module Architecture & Strategy
* ADR-004 — Catering Repository Architecture
* ADR-005 — Catering Service Architecture
* ADR-006 — Catering Security & Governance Integration
* ADR-008 — Catering Inventory Domain Boundary
* ADR-009 — Inventory Stock Item Architecture
* ADR-010 — Inventory Location Architecture
* ADR-011 — Inventory Stock Balance Architecture
* ADR-012 — Inventory Stock Movement Ledger Architecture

---

## 1. Context

The Catering module requires a controlled mechanism for moving inventory stock from one inventory location to another.

The inventory architecture established by ADR-008 defines Inventory as responsible for stock quantities, locations, balances, movements, and transfers. ADR-011 establishes `StockBalance` as the authoritative persisted current quantity for each `StockItem` at an `InventoryLocation`. ADR-012 establishes `StockMovement` as the authoritative historical inventory ledger.

A stock transfer therefore cannot be implemented as a simple update of two balances. It represents a business transaction involving:

1. a stock item,
2. a source location,
3. a destination location,
4. a positive transfer quantity,
5. transfer-specific business information,
6. two inventory effects,
7. and a single atomic posting operation.

The architecture must establish a clear ownership boundary between:

* the transfer itself,
* the inventory movement ledger,
* the current stock balances,
* repositories,
* services,
* and the enterprise transaction infrastructure.

Without an explicit boundary, transfer logic could become distributed across repositories, movement services, balance services, or routes, creating inconsistent stock state and making the transfer difficult to audit and correct.

---

## 2. Decision

`StockTransfer` is established as the **authoritative business record and orchestration boundary for inventory transfers between locations**.

A transfer represents the intent and business context of moving a quantity of one `StockItem` from one `InventoryLocation` to another.

The transfer service is responsible for validating and posting the transfer as one atomic business operation.

A successfully posted transfer produces two corresponding inventory movement effects:

1. a negative movement at the source location, and
2. a positive movement at the destination location.

The two effects must succeed or fail together.

`StockTransfer` therefore owns the transfer orchestration, while `StockMovement` owns the historical inventory effects produced by that transfer.

`StockBalance` remains the authoritative current-state representation of inventory quantity at each location.

---

## 3. Transfer Ownership Boundary

The Catering inventory domain owns `StockTransfer`.

The transfer boundary is responsible for:

* identifying the stock item being transferred;
* identifying the source location;
* identifying the destination location;
* identifying the transfer quantity;
* maintaining transfer lifecycle state;
* validating transfer-specific business rules;
* recording transfer reference and reason where provided;
* coordinating source and destination balance effects;
* coordinating transfer-generated stock movements;
* and preserving the historical relationship between the transfer and its inventory effects.

The transfer boundary does not own:

* product master data;
* purchasing;
* supplier management;
* procurement;
* sales;
* invoicing;
* financial accounting;
* expense management;
* warehouse-management functionality;
* replenishment planning;
* inventory valuation;
* or external logistics processes.

Those capabilities remain outside the transfer boundary unless a future architectural decision explicitly introduces them.

---

## 4. StockTransfer as the Transfer Record

`StockTransfer` represents the business-level transfer operation.

The transfer record contains, conceptually:

* `stock_item_id`;
* `source_location_id`;
* `destination_location_id`;
* `quantity`;
* `reference`;
* `reason`;
* transfer status;
* creation/occurrence information;
* posting information;
* and any required relationship to the resulting movement records.

The transfer quantity is always a **positive quantity**.

Direction is represented by the source and destination locations rather than by a signed transfer quantity.

This keeps the transfer record semantically clear:

> A transfer moves a positive quantity from one location to another.

Signed quantities belong to the resulting `StockMovement` records.

---

## 5. Source and Destination Locations

Every transfer requires:

* exactly one source location; and
* exactly one destination location.

Both locations must be valid `InventoryLocation` records.

The source and destination must represent distinct locations.

A transfer from a location to itself is invalid because it produces no meaningful inventory movement and would unnecessarily complicate the ledger.

Location ownership remains with the inventory domain as established by ADR-010.

`StockTransfer` therefore references locations but does not redefine or duplicate location management.

---

## 6. Stock Item

Every transfer applies to exactly one `StockItem`.

`StockItem` remains the inventory participation/configuration record for the authoritative Catering `Product`, as established by ADR-009.

`StockTransfer` does not duplicate product information.

The transfer operates on the `StockItem` identified by `stock_item_id`.

The current quantity available for transfer is obtained from the relevant `StockBalance` at the source location.

---

## 7. Transfer Quantity

Transfer quantity must be:

* numeric;
* positive;
* non-zero;
* and representable using the inventory quantity precision.

The transfer quantity follows the inventory quantity convention established by ADR-011 and ADR-012:

`Numeric(18,3)`.

A zero or negative transfer quantity is invalid.

The transfer quantity itself is stored as a positive value.

The source movement receives the negative effect, while the destination movement receives the positive effect.

---

## 8. Transfer Lifecycle

A transfer has a controlled lifecycle.

The architecture distinguishes at minimum between:

* `DRAFT`
* `POSTED`

A draft transfer represents an unposted transfer operation.

A draft transfer:

* does not change source stock;
* does not change destination stock;
* does not create posted inventory effects;
* and remains subject to modification according to the service lifecycle rules.

A posted transfer represents a completed inventory operation.

A posted transfer:

* cannot be freely edited;
* has generated its corresponding inventory effects;
* has affected source and destination balances;
* and becomes part of the historical inventory record.

The lifecycle follows the same general principle established for stock movements: **posting is the point at which the inventory state changes**.

---

## 9. Transfer Posting Semantics

Posting a transfer is a single business operation.

Conceptually:

Source balance
    quantity - transfer quantity

Destination balance
    quantity + transfer quantity

StockTransfer
    DRAFT → POSTED

StockMovement
    source: negative TRANSFER effect
    destination: positive TRANSFER effect

All of these changes form one atomic operation.

If any required validation or persistence operation fails, the complete transfer operation must be rolled back.

A partially posted transfer is not a valid state.

---

## 10. Source Balance Validation

Before posting, the transfer service must establish that sufficient stock exists at the source location.

The resulting source balance must not become negative.

If the source balance is:

Q

and the transfer quantity is:

T

then:

Q - T >= 0

must hold.

If no source balance exists, a positive transfer cannot be posted because there is no available stock from which to transfer.

This follows the invariant established by ADR-011:

> A negative inventory effect cannot create a missing balance.

---

## 11. Destination Balance Handling

The destination location may or may not already have a balance record for the transferred stock item.

If a destination balance exists:

new destination quantity =
current destination quantity + transfer quantity

If no destination balance exists, a new balance may be created with the transfer quantity.

This follows the same balance-creation semantics established for positive inventory movements.

A transfer therefore does not require the destination to have previously held the stock item.

---

## 12. StockMovement Integration

`StockMovement` remains the authoritative historical ledger.

`StockTransfer` does not replace the movement ledger.

Instead, a posted transfer produces two movement effects associated with the transfer:

### Source movement

* movement type: `TRANSFER`;
* quantity: negative transfer quantity;
* location: source location;
* stock item: transferred stock item;
* transfer reference: the associated `StockTransfer`.

### Destination movement

* movement type: `TRANSFER`;
* quantity: positive transfer quantity;
* location: destination location;
* stock item: transferred stock item;
* transfer reference: the associated `StockTransfer`.

The two movements together represent the complete inventory effect of the transfer.

The transfer record provides the business-level context; the movement records provide the location-specific inventory effects.

---

## 13. Transfer Movement Relationship

The movement ledger must retain sufficient information to identify movements generated by a transfer.

Where the established model provides `transfer_id`, the transfer-generated movements reference their originating `StockTransfer`.

This permits:

* transfer history reconstruction;
* audit tracing;
* movement-to-transfer navigation;
* reconciliation of source and destination effects;
* and future reporting.

The transfer remains the authoritative business record for the transfer operation.

The movement records remain authoritative for historical inventory effects.

---

## 14. Atomicity

Transfer posting must use the established enterprise transaction boundary.

The service/application boundary is responsible for coordinating:

1. validation;
2. source balance retrieval;
3. destination balance retrieval;
4. source balance update;
5. destination balance update;
6. source movement creation;
7. destination movement creation;
8. transfer status transition;
9. and transaction commit.

These changes must commit together.

If any step fails, the transaction must roll back.

Repositories must not independently commit portions of the transfer.

This prevents states such as:

* source stock reduced but destination stock not increased;
* destination stock increased without source stock reduction;
* one movement persisted while the other is missing;
* transfer marked posted without corresponding movements;
* or movement records persisted without the corresponding balance changes.

---

## 15. Transaction Boundary Ownership

The transfer service owns business orchestration and coordinates the established transaction infrastructure.

The repository layer remains persistence-oriented.

The dependency direction is:

Route / Application Boundary
        ↓
StockTransferService
        ↓
Repositories
        ↓
Enterprise Data Infrastructure

with the service also depending on the enterprise transaction abstraction:

StockTransferService
        ↓
TransactionManager

Repositories do not own:

* `begin`;
* `commit`;
* `rollback`;
* or transfer-level transaction coordination.

This follows ADR-004 and ADR-005.

---

## 16. Validation Ownership

Transfer-specific business validation belongs to the transfer service.

Validation includes, as applicable:

* stock item exists;
* source location exists;
* destination location exists;
* source and destination differ;
* transfer quantity is positive;
* source stock is sufficient;
* transfer lifecycle permits posting;
* referenced entities are active where required;
* and required business information is valid.

Database constraints remain responsible for persistence-level invariants.

Authorization remains distinct from business validation.

A caller may be authorized to perform a transfer while still submitting an invalid transfer.

---

## 17. Transfer Immutability

Once a transfer is posted, its inventory effect is considered historical.

Posted transfer records must not be destructively modified in ways that rewrite inventory history.

In particular, the following are not normal correction mechanisms:

* deleting a posted transfer;
* changing its quantity;
* changing its source location;
* changing its destination location;
* or rewriting its movement effects.

If a posted transfer requires correction, the correction must be represented through appropriate compensating inventory transactions or a future explicitly designed reversal mechanism.

This preserves the integrity of the inventory history.

---

## 18. No Destructive Deletion of Posted Transfer History

Posted transfers represent completed inventory operations.

They must therefore remain available for:

* audit;
* reconciliation;
* reporting;
* historical review;
* and inventory traceability.

Soft deletion, where applicable to the enterprise framework, must not be interpreted as permission to erase or rewrite the business meaning of a posted inventory transaction.

Historical inventory effects remain part of the authoritative ledger.

---

## 19. Transfer References and Reasons

A transfer may carry:

* a business reference;
* and/or a reason.

Examples include:

* internal stock relocation;
* movement between catering stores;
* kitchen replenishment;
* event preparation;
* stock consolidation.

These fields provide business context but do not replace the enterprise audit framework.

The transfer record should remain understandable independently of an external audit event.

---

## 20. Occurrence and Posting Time

The architecture distinguishes the business occurrence of the transfer from the system posting event.

Where applicable:

* `occurred_at` represents when the transfer is considered to have occurred;
* `posted_at` represents when the transfer was formally posted by the system.

This follows the distinction already established by ADR-012 for stock movements.

Historical reporting can therefore distinguish business timing from system processing timing.

---

## 21. Transfer Status and Movement Status

The transfer lifecycle and movement lifecycle are related but distinct.

A transfer may be a draft before posting.

Its inventory effects must not become posted inventory movements until the transfer itself is successfully posted.

The resulting movements must therefore reflect the final successful posting operation.

A transfer must never be represented as posted while its required movement effects remain absent or uncommitted.

---

## 22. Transfer Service Responsibilities

`StockTransferService` is responsible for:

* creating transfer records;
* validating transfer inputs;
* validating source and destination locations;
* validating transfer quantity;
* checking source availability;
* coordinating source and destination balances;
* generating transfer movement effects;
* posting the transfer;
* coordinating transaction boundaries;
* enforcing lifecycle rules;
* and raising appropriate service-layer exceptions.

The service may coordinate multiple repositories because transfer posting is inherently a multi-entity business operation.

This is consistent with ADR-005.

---

## 23. Repository Responsibilities

Transfer repositories remain persistence-oriented.

A transfer repository may provide:

* transfer retrieval;
* transfer persistence;
* transfer-specific lookup;
* and query operations supported by the enterprise repository framework.

It must not own:

* transfer business rules;
* stock sufficiency validation;
* balance orchestration;
* movement creation;
* or transaction lifecycle.

Repositories therefore remain thin and reusable.

---

## 24. Relationship to StockBalance

`StockBalance` remains the authoritative current quantity.

`StockTransfer` does not store a duplicate current quantity.

A posted transfer modifies:

* the source `StockBalance`;
* and the destination `StockBalance`.

The transfer itself provides the historical business context for why those balance changes occurred.

The separation is:

StockTransfer
    = transfer business operation

StockMovement
    = historical inventory effect

StockBalance
    = current inventory state

This separation prevents the transfer record from becoming a second inventory ledger or a second current-state store.

---

## 25. Relationship to Product and StockItem

The transfer operates on the existing inventory `StockItem`.

The conceptual relationship is:

Product
   ↓
StockItem
   ↓
StockTransfer
   ↓
StockMovement
   ↓
StockBalance

The transfer architecture does not introduce another product reference or inventory item registry.

Product remains authoritative for product identity.

StockItem remains authoritative for inventory participation and stock configuration.

---

## 26. Security and Authorization

Transfer operations must use the existing enterprise security and authorization infrastructure established under ADR-006.

Catering owns the business capability permission required to perform transfer operations.

The enterprise authorization engine remains authoritative for evaluating and enforcing permissions.

The transfer service does not create a second authorization mechanism.

Authorization should occur at the established application/business boundary before the protected operation is executed.

Business validation remains the responsibility of the transfer service.

---

## 27. Audit and Governance

Transfer operations integrate with the existing enterprise audit and governance infrastructure.

The `StockTransfer` and associated `StockMovement` records provide business history, but they do not replace enterprise audit records.

Enterprise audit remains authoritative for recording security-relevant and governed application actions.

Governance remains owned by the enterprise platform.

No Catering-specific audit, compliance, or governance framework is introduced.

---

## 28. Querying and Reporting

Transfer records must be queryable through the existing enterprise data framework.

The architecture reuses existing:

* repositories;
* `QueryOptions`;
* filtering;
* sorting;
* pagination;
* and reporting infrastructure.

Potential transfer query dimensions include:

* stock item;
* source location;
* destination location;
* status;
* reference;
* occurred-at range;
* posted-at range.

No transfer-specific query framework is introduced.

Reporting remains a consumer of authoritative transfer, movement, and balance data through the existing reporting architecture.

---

## 29. Concurrency and Consistency

Transfer posting requires consistency between source and destination balances and the movement ledger.

The initial architecture relies on the established enterprise transaction infrastructure and the database transaction semantics provided by SQL Server.

No speculative locking framework or custom concurrency subsystem is introduced at this stage.

If production concurrency requirements later demonstrate a need for explicit row-level locking, optimistic concurrency, retry policies, or other mechanisms, those changes must be introduced through a separate architectural decision based on observed requirements.

---

## 30. Failure Handling

A transfer must not be considered posted if any required operation fails.

Examples of failure conditions include:

* missing stock item;
* missing source location;
* missing destination location;
* inactive/invalid location where prohibited;
* source equals destination;
* invalid quantity;
* insufficient source stock;
* invalid transfer lifecycle state;
* movement creation failure;
* balance persistence failure;
* or transaction commit failure.

The transaction boundary must ensure that partial inventory effects are not committed.

The caller receives an appropriate service-layer exception while the transaction is rolled back according to the established transaction infrastructure.

---

## 31. Alternatives Considered

### 31.1 Update balances directly without movements

Rejected.

Direct balance updates would destroy the historical inventory trail and make reconciliation difficult.

### 31.2 Represent a transfer as one signed movement

Rejected.

A transfer affects two locations and therefore requires two location-specific inventory effects.

### 31.3 Let `StockMovementService` own transfer orchestration

Rejected.

The movement service owns movement semantics. Transfer orchestration is a higher-level business operation involving source/destination coordination and a dedicated transfer record.

### 31.4 Let repositories coordinate the transfer

Rejected.

Repositories are persistence-oriented and must not own business orchestration or transaction lifecycle.

### 31.5 Maintain current quantity on `StockTransfer`

Rejected.

Current quantity belongs to `StockBalance`. A transfer records the quantity involved in a historical business operation, not current inventory state.

### 31.6 Introduce a separate warehouse-management framework

Rejected.

The current Catering inventory requirement does not justify a separate warehouse-management architecture.

### 31.7 Introduce speculative locking infrastructure

Rejected.

The existing transaction infrastructure is sufficient for the current architectural scope. Additional concurrency architecture should be evidence-driven.

---

## 32. Architectural Invariants

The following invariants apply:

1. A transfer has exactly one stock item.
2. A transfer has exactly one source location.
3. A transfer has exactly one destination location.
4. Source and destination locations must differ.
5. Transfer quantity is positive and non-zero.
6. A transfer cannot create a negative source balance.
7. A missing source balance cannot satisfy a positive transfer.
8. A missing destination balance may be created by a successful transfer.
9. A posted transfer produces both source and destination movement effects.
10. Source and destination effects are committed atomically.
11. `StockMovement` remains the historical inventory ledger.
12. `StockBalance` remains the authoritative current quantity.
13. Posted transfer history is not destructively rewritten.
14. Transfer business rules belong to the service layer.
15. Repositories do not own transaction lifecycle.
16. Existing enterprise security and authorization remain authoritative.
17. Existing enterprise audit and governance remain authoritative.
18. No duplicate product or inventory-item registry is introduced.
19. No parallel transaction, repository, security, or inventory framework is introduced.
20. Transfer functionality remains within the Catering inventory bounded context.

---

## 33. Implementation Alignment

The architecture aligns with the existing implementation structure:

app/modules/catering/
├── models/
│   └── stock_transfer.py
├── repositories/
│   └── transfer.py
├── services/
│   └── transfer.py
└── security/
    └── permissions.py

The implementation reuses the enterprise foundations under:

app/core/data/
app/core/crud/
app/core/security/
app/core/execution/

The existing `StockTransferService` is therefore the natural business orchestration boundary for transfer posting.

The existing transaction infrastructure provides the transaction boundary required for atomic transfer posting.

---

## 34. Consequences

### Positive consequences

* Clear ownership of transfer business operations.
* Atomic source/destination inventory updates.
* Complete historical traceability through `StockMovement`.
* Clear separation between business operation, current state, and historical effects.
* Reuse of existing enterprise infrastructure.
* Consistent security, audit, governance, and reporting integration.
* Reduced risk of partial inventory transfers.
* Easier future reconciliation and reporting.

### Negative consequences

* Transfer posting is more complex than a direct balance update.
* Two movement records are required for every posted transfer.
* Transfer orchestration requires coordination across multiple repositories/entities.
* Correct transaction handling is essential.
* Future reversal/correction workflows may require additional architecture.

These consequences are accepted because inventory integrity and traceability are more important than minimizing implementation complexity.

---

## 35. Out of Scope

The following remain outside this ADR:

* supplier management;
* purchase orders;
* procurement workflows;
* goods-receiving workflows beyond the movement effect itself;
* sales orders;
* invoices;
* financial accounting;
* inventory valuation;
* automated replenishment;
* demand forecasting;
* warehouse zones;
* aisles, shelves, and bins;
* barcode/RFID architecture;
* advanced warehouse management;
* inter-module distributed transactions;
* event-driven distributed transfer orchestration;
* background transfer jobs;
* external logistics integration;
* API gateway architecture;
* new security or authorization frameworks;
* new transaction frameworks;
* speculative concurrency infrastructure.

---

## 36. Approval

This ADR documents the architectural boundary for inventory stock transfers within the Catering module.

The status remains **Planned for documentation** until:

1. the authoritative Phase 2 roadmap is reconciled;
2. the ADR is verified;
3. the documentation checkpoint is committed; and
4. the resulting working tree is confirmed clean.

Upon completion of those steps, the ADR status should be reconciled to:

**Approved — Retrospective**

# ADR-015 — Inventory Transaction & Posting Boundary

**Status:** Planned for documentation
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory transaction boundaries, posting atomicity, rollback behavior, repository participation, and transaction coordination

**Related ADRs:** ADR-001, ADR-004, ADR-005, ADR-008, ADR-011, ADR-012, ADR-013, ADR-014

---

## 1. Context

The Catering Inventory domain contains operations whose correctness depends on multiple persistent changes succeeding or failing together.

The principal examples are:

* posting a stock movement;
* updating or creating the corresponding stock balance;
* posting a stock transfer;
* reducing the source-location balance;
* increasing the destination-location balance;
* creating the corresponding transfer movement records.

These operations cannot safely be treated as independent repository writes.

For example, a movement posting operation must not leave a `StockMovement` marked `POSTED` while its corresponding `StockBalance` remains unchanged. Similarly, a stock transfer must not reduce the source balance without also increasing the destination balance and recording the corresponding movement effects.

The enterprise platform already provides transaction infrastructure through the established `TransactionManager` abstraction and its SQLAlchemy implementation. The Catering Inventory services must therefore use that infrastructure rather than introduce an inventory-specific transaction mechanism.

ADR-014 establishes the repository/service boundary for Inventory. This ADR complements that decision by defining where transaction ownership resides and how inventory posting operations participate in the existing transaction infrastructure.

The architectural objective is to ensure that inventory state transitions are atomic, consistent, recoverable on failure, and aligned with the enterprise transaction model.

---

## 2. Decision

Catering Inventory business transactions are owned and coordinated by the **service/application boundary**, using the existing enterprise `TransactionManager` abstraction.

Repositories participate in persistence operations but do not own transaction lifecycle.

Inventory posting operations that modify multiple related records must execute within a single transaction boundary so that either the complete business operation succeeds or all persistent changes are rolled back.

The established transaction architecture is authoritative:

Application Boundary
        │
        ▼
Catering Inventory Service
        │
        ├──────────────► TransactionManager
        │
        ├──────────────► Repository
        │
        ▼
Enterprise Data / SQLAlchemy

No separate Inventory transaction manager, repository transaction framework, or distributed transaction mechanism is introduced.

---

## 3. Transaction Ownership

The service/application layer owns transaction coordination because it understands the complete business operation being performed.

A service may coordinate:

* validation;
* repository reads;
* current-state evaluation;
* balance creation or update;
* movement creation;
* transfer lifecycle changes;
* movement lifecycle changes;
* transaction commit or rollback.

Repositories remain persistence-oriented.

A repository may:

* retrieve entities;
* add entities;
* update entities;
* delete entities where the domain permits it;
* execute domain-relevant persistence queries.

A repository must not:

* begin a transaction;
* commit a transaction;
* rollback a transaction;
* independently decide transaction boundaries;
* coordinate commits across other repositories.

This preserves a clear separation between persistence access and business-operation orchestration.

---

## 4. Use of the Enterprise TransactionManager

Inventory services reuse the existing enterprise transaction infrastructure.

The established `TransactionManager` abstraction provides the transaction boundary required by Inventory services, while the SQLAlchemy implementation integrates that abstraction with the application's database session.

The Inventory module therefore depends on the transaction abstraction rather than directly defining its own transaction framework.

The dependency direction is:

Catering Inventory Service
        │
        ▼
Enterprise TransactionManager
        │
        ▼
SQLAlchemy Transaction Infrastructure
        │
        ▼
SQL Server

This preserves the enterprise architecture established during Phase 1 and prevents business modules from creating parallel infrastructure.

---

## 5. Stock Movement Posting Boundary

Stock movement posting is a single business operation.

For a valid movement, the posting operation must coordinate:

1. validation of the stock item;
2. validation of the inventory location;
3. validation of movement type;
4. validation of signed quantity;
5. retrieval of the current stock balance;
6. determination of the resulting balance;
7. validation that the resulting balance is not negative;
8. creation or update of the `StockBalance`;
9. creation of the `StockMovement`;
10. transition of the movement to `POSTED`;
11. population of posting metadata;
12. transaction commit.

These changes must occur within one transaction boundary.

Conceptually:

BEGIN TRANSACTION
       │
       ├── Validate movement
       ├── Read current balance
       ├── Calculate resulting balance
       ├── Validate resulting balance
       ├── Create/update StockBalance
       ├── Create StockMovement
       ├── Mark movement POSTED
       │
       ├── SUCCESS ──► COMMIT
       │
       └── FAILURE ──► ROLLBACK

A successful posting therefore establishes both:

* the historical inventory event in `StockMovement`; and
* the resulting current inventory state in `StockBalance`.

Neither record may be considered successfully posted independently of the other.

---

## 6. Movement Type and Transaction Semantics

The existing Inventory movement model uses signed quantities and controlled movement types.

The transaction boundary preserves the following semantics:

| Movement Type     | Quantity Rule                       | Inventory Effect                       |
| ----------------- | ----------------------------------- | -------------------------------------- |
| `OPENING_BALANCE` | Signed                              | Establishes or adjusts initial stock   |
| `RECEIPT`         | Positive                            | Increases stock                        |
| `ISSUE`           | Negative                            | Decreases stock                        |
| `ADJUSTMENT`      | Signed                              | Corrects stock                         |
| `TRANSFER`        | Reserved for transfer orchestration | Changes location through StockTransfer |

Zero-quantity movements are invalid.

`TRANSFER` movements are not posted independently through the ordinary movement-posting path. They are produced as part of the `StockTransfer` orchestration defined by ADR-013.

---

## 7. DRAFT and POSTED Lifecycle

Inventory transaction lifecycle is explicitly separated from inventory effect.

### DRAFT

A draft movement or transfer represents an unposted business instruction.

A draft record:

* may be validated and persisted;
* does not change `StockBalance`;
* does not represent a completed inventory effect;
* may remain subject to permitted lifecycle changes.

### POSTED

A posted movement or transfer represents a completed inventory operation.

A posted operation:

* produces its defined inventory effect;
* updates the appropriate `StockBalance` records;
* records the historical movement effect;
* records posting metadata;
* becomes immutable with respect to the completed transaction.

The distinction ensures that merely creating an inventory transaction record does not alter stock.

---

## 8. Stock Transfer Transaction Boundary

Stock transfer posting is one atomic business operation.

A transfer coordinates:

* one `StockTransfer`;
* one source-location balance;
* one destination-location balance;
* one negative `TRANSFER` movement at the source;
* one positive `TRANSFER` movement at the destination.

Conceptually:

BEGIN TRANSACTION
       │
       ├── Validate transfer
       ├── Validate source location
       ├── Validate destination location
       ├── Validate stock item
       ├── Validate positive quantity
       ├── Verify source stock availability
       │
       ├── Decrease source StockBalance
       ├── Increase destination StockBalance
       ├── Create source TRANSFER movement
       ├── Create destination TRANSFER movement
       ├── Mark StockTransfer POSTED
       │
       ├── SUCCESS ──► COMMIT
       │
       └── FAILURE ──► ROLLBACK

The source and destination effects must therefore succeed or fail together.

A transfer must never result in:

* source stock being reduced without destination stock being increased;
* destination stock being increased without source stock being reduced;
* only one transfer movement being persisted;
* a transfer being marked `POSTED` while its inventory effects were not committed.

---

## 9. Balance Creation and Transaction Semantics

The transaction boundary also applies when a `StockBalance` does not yet exist.

For a positive movement:

* a missing balance may be created;
* the new balance receives the movement quantity;
* the movement and balance creation occur within the same transaction.

For a negative movement:

* a missing balance cannot satisfy the requested stock reduction;
* the operation fails validation/business-rule checks;
* no partial inventory record is committed.

For an existing balance:

resulting quantity = current quantity + movement quantity

The resulting quantity must remain non-negative.

The balance update and movement posting are therefore treated as one state transition.

---

## 10. Atomicity and Failure Handling

Inventory posting must provide all-or-nothing behavior.

If any part of the operation fails before commit, the transaction is rolled back.

Potential failures include:

* invalid entity references;
* invalid movement type;
* invalid quantity sign;
* zero quantity;
* insufficient stock;
* invalid source or destination location;
* invalid transfer;
* repository persistence failure;
* database constraint violation;
* transaction commit failure.

The service must not attempt to manually reconstruct partial state after a transaction failure when rollback can restore the transaction boundary.

The transaction infrastructure is responsible for maintaining transaction lifecycle integrity, while the service is responsible for invoking that infrastructure at the correct business boundary.

---

## 11. Commit and Rollback Responsibility

Commit and rollback responsibility belongs to the transaction boundary, not individual repositories.

The expected pattern is conceptually:

Service
  │
  ├── begin transaction
  │
  ├── repository operation
  ├── repository operation
  ├── repository operation
  │
  ├── success → commit
  │
  └── failure → rollback

Repositories remain unaware of whether their operation is part of:

* a stock movement;
* a stock transfer;
* another future inventory operation;
* a larger application-level transaction.

This allows the service/application layer to determine the correct scope of each business operation.

---

## 12. Commit Failure and Transaction State

The enterprise transaction implementation must preserve sufficient transaction state to permit rollback when a commit operation itself fails.

This is important because a commit failure must not leave the transaction manager in an internally inconsistent state that prevents appropriate failure handling.

Inventory services therefore rely on the established transaction manager's lifecycle guarantees rather than implementing commit-failure recovery independently.

The Inventory module does not duplicate or override these enterprise transaction semantics.

---

## 13. Posted Transaction Immutability

Once a stock movement or transfer has been successfully posted, the completed transaction is treated as immutable.

The system must not destructively modify a posted inventory history record merely to correct a previous business event.

Where correction is required, the appropriate mechanism is a compensating inventory operation or a future explicit reversal mechanism.

This preserves the integrity of the inventory ledger and ensures that historical inventory effects remain explainable.

The transaction boundary therefore protects both:

* current-state consistency in `StockBalance`; and
* historical integrity in `StockMovement`.

---

## 14. Repository Participation

Inventory repositories participate in transactionally coordinated operations without owning the transaction.

For example:

### Stock movement

StockMovementService
    │
    ├── TransactionManager
    ├── StockItemRepository
    ├── InventoryLocationRepository
    ├── StockBalanceRepository
    └── StockMovementRepository

### Stock transfer

StockTransferService
    │
    ├── TransactionManager
    ├── StockTransferRepository
    ├── StockItemRepository
    ├── InventoryLocationRepository
    ├── StockBalanceRepository
    └── StockMovementRepository

The service coordinates these repositories because the service understands the complete business operation.

No repository is permitted to commit independently during these operations.

---

## 15. Business Validation and Database Constraints

Transaction boundaries do not replace validation or database integrity constraints.

Business validation remains the responsibility of the appropriate service.

Examples include:

* movement type compatibility;
* quantity sign rules;
* sufficient source stock;
* distinct transfer locations;
* valid lifecycle transitions;
* resulting balance rules.

Database constraints remain responsible for persistence invariants such as:

* foreign keys;
* required fields;
* unique product-to-stock-item association;
* unique stock-item/location balance;
* non-negative persisted balance quantity;
* numeric precision;
* unique location codes.

The two mechanisms are complementary.

Business Rules
     │
     ▼
Service Validation
     │
     ▼
Transaction Boundary
     │
     ▼
Repository Persistence
     │
     ▼
Database Constraints

---

## 16. Concurrency Approach

The current Inventory architecture relies on the established SQLAlchemy/SQL Server transaction infrastructure for transactional consistency.

No speculative locking or custom inventory concurrency framework is introduced at this stage.

This means the module does not introduce:

* custom row-locking APIs;
* inventory-specific lock managers;
* custom retry frameworks;
* optimistic concurrency infrastructure;
* distributed locking;
* application-level mutexes.

Concurrency enhancements may be considered later if demonstrated by actual business requirements, workload characteristics, or observed contention.

Such enhancements would require a separate architectural decision.

---

## 17. Security, Audit, Governance, and Reporting

The transaction boundary does not create parallel security or governance mechanisms.

Inventory operations continue to use the enterprise capabilities established by:

* ADR-006 for security, authorization, audit, and governance integration;
* ADR-012 for movement-ledger semantics;
* ADR-013 for transfer orchestration;
* ADR-014 for repository/service ownership.

Authorization is evaluated through the enterprise security infrastructure.

Business validation remains within Inventory services.

Enterprise audit mechanisms remain authoritative for application audit.

Inventory movements and transfers provide business history but are not substitutes for the enterprise audit framework.

Reporting continues to consume authoritative inventory data through the existing enterprise reporting/data infrastructure.

---

## 18. Dependency Direction

The architectural dependency direction remains:

Enterprise Infrastructure
        ▲
        │
Catering Inventory Repository
        ▲
        │
Catering Inventory Service
        ▲
        │
Application Boundary

Transaction coordination is an enterprise capability consumed by the service layer:

Catering Inventory Service
        │
        ├──► Inventory Repositories
        │
        └──► Enterprise TransactionManager

The enterprise transaction infrastructure must not depend on Catering Inventory.

---

## 19. Alternatives Considered

### 19.1 Repository-Owned Transactions

Rejected.

Repositories should remain persistence-oriented. Repository-owned commits would make multi-repository business operations difficult to coordinate and could produce partial state.

### 19.2 Separate Inventory Transaction Manager

Rejected.

The enterprise `TransactionManager` already provides the required abstraction. A second transaction framework would fragment transaction semantics and violate platform reuse principles.

### 19.3 Database Triggers for Inventory Posting

Rejected.

Triggers would move business orchestration into the persistence layer and obscure the application-level business operation.

The service layer must remain responsible for business orchestration.

### 19.4 Event-Driven Posting

Rejected for the current scope.

Inventory posting requires immediate atomic consistency between current balances and historical movement records. Introducing asynchronous event-driven posting would add complexity without an established requirement.

### 19.5 Distributed Transactions

Rejected.

The current Inventory scope is based on one enterprise database transaction boundary. Distributed transaction infrastructure is unnecessary.

### 19.6 Speculative Locking Framework

Rejected.

No demonstrated requirement currently justifies a custom concurrency framework. The established SQL Server transaction behavior is the current foundation.

### 19.7 Manual Partial-Rollback Logic

Rejected.

Services should rely on the established transaction infrastructure rather than manually attempting to undo individual repository operations after failure.

---

## 20. Architectural Invariants

The following invariants apply to Catering Inventory transaction processing:

1. The service/application boundary owns business transaction coordination.
2. Repositories do not begin, commit, or rollback transactions.
3. Inventory reuses the enterprise `TransactionManager`.
4. Stock movement posting is atomic.
5. Stock transfer posting is atomic.
6. A failed posting leaves no partial committed inventory effect.
7. `DRAFT` records do not affect `StockBalance`.
8. `POSTED` records produce their defined inventory effects.
9. Posted inventory transactions are immutable.
10. `StockBalance` remains authoritative for current quantity.
11. `StockMovement` remains authoritative for historical inventory effects.
12. `StockTransfer` remains authoritative for transfer context and orchestration.
13. Positive movements may create missing balances.
14. Negative movements cannot create missing balances.
15. Resulting stock quantity must not be negative.
16. Transfer source and destination effects succeed or fail together.
17. Security and governance use enterprise infrastructure.
18. No parallel inventory transaction framework is introduced.
19. No speculative concurrency mechanism is introduced.
20. Cross-repository coordination remains a service responsibility.

---

## 21. Implementation Alignment

This decision aligns with the implemented architecture in:

app/core/crud/transaction.py
app/core/execution/transaction.py

app/modules/catering/services/balance.py
app/modules/catering/services/movement.py
app/modules/catering/services/transfer.py

app/modules/catering/repositories/balance.py
app/modules/catering/repositories/movement.py
app/modules/catering/repositories/transfer.py

app/modules/catering/models/stock_balance.py
app/modules/catering/models/stock_movement.py
app/modules/catering/models/stock_transfer.py

The enterprise transaction infrastructure provides:

* transaction abstraction;
* transaction context management;
* SQLAlchemy session integration;
* commit and rollback handling;
* transaction-state management.

Catering Inventory services consume that infrastructure for domain operations.

The implementation therefore follows the established architectural layering rather than introducing an Inventory-specific transaction subsystem.

---

## 22. Consequences

### Positive consequences

* Inventory posting is explicitly atomic.
* Current and historical inventory state remain synchronized.
* Transfer operations cannot partially commit their inventory effects.
* Repository responsibilities remain simple and predictable.
* Services retain ownership of business operations.
* The enterprise transaction framework is reused consistently.
* Failure handling is centralized around established transaction semantics.
* Future business modules can follow the same enterprise transaction pattern.
* Posted inventory history remains auditable and explainable.

### Negative consequences

* Business operations involving multiple repositories require service-level coordination.
* Service implementations are more explicit than simple repository CRUD.
* Transaction boundaries must be carefully chosen for each business operation.
* Future concurrency requirements may require additional architectural work.

These consequences are accepted because transactional correctness is more important than minimizing service-layer complexity.

---

## 23. Out of Scope

This ADR does not establish:

* a new enterprise transaction framework;
* a new Inventory transaction manager;
* distributed transactions;
* two-phase commit;
* event-sourced inventory;
* asynchronous inventory posting;
* background posting workers;
* a custom locking framework;
* optimistic concurrency infrastructure;
* warehouse-management transaction architecture;
* procurement transactions;
* purchasing transactions;
* sales transactions;
* finance/accounting transactions;
* invoice transactions;
* inventory valuation;
* replenishment automation;
* supplier/customer transaction integration;
* cross-module distributed transaction coordination.

Such capabilities require separate architectural decisions if and when they become necessary.

---

## 24. Verification Expectations

Before this ADR is marked **Approved — Retrospective**, the following must be verified:

1. ADR-015 exists at the documented path.
2. The roadmap status is reconciled from `Planned for documentation` to `Approved — Retrospective`.
3. `git diff --check` passes.
4. The ADR and roadmap changes contain only the intended Group 14 modifications.
5. Relevant inventory transaction tests remain passing.
6. The working tree is clean after the Git checkpoint.
7. The ADR accurately reflects the implemented transaction architecture.

---

## 25. Approval

This ADR is initially recorded as **Planned for documentation** while the documentation and reconciliation process is completed.

Following targeted verification, roadmap reconciliation, regression confirmation, and Git checkpoint creation, the status shall be changed to:

**Approved — Retrospective**

This records the transaction and posting architecture that has already been implemented for Catering Inventory and establishes it as the authoritative architectural boundary for subsequent Phase 2 inventory work.

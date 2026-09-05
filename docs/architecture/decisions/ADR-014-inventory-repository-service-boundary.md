# ADR-014 — Inventory Repository & Service Boundary

**Status:** Planned for documentation
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory repository and service ownership, persistence boundaries, business-rule orchestration, cross-entity coordination, transaction coordination, and reuse of enterprise data/service infrastructure

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
* ADR-013 — Inventory Stock Transfer Architecture

---

## 1. Context

The Catering inventory domain contains multiple related entities whose persistence and business behavior must remain clearly separated.

The inventory model includes:

* `StockItem`;
* `InventoryLocation`;
* `StockBalance`;
* `StockMovement`;
* `StockTransfer`.

These entities have different responsibilities.

`StockItem` defines inventory participation and stock configuration for an existing Catering `Product`.

`InventoryLocation` identifies where inventory may be held.

`StockBalance` represents authoritative current quantity for a StockItem at a location.

`StockMovement` represents historical inventory effects.

`StockTransfer` represents the business operation that coordinates movement of stock between two locations.

The implementation therefore requires both:

1. persistence-oriented repositories; and
2. business-rule-oriented services.

ADR-004 establishes the general Catering repository architecture, while ADR-005 establishes the general Catering service architecture.

This ADR applies those decisions specifically to the inventory domain and establishes the boundary between repositories and services so that inventory logic does not become duplicated across persistence and business layers.

---

## 2. Decision

Inventory will use **Catering-owned repositories and services that reuse the existing enterprise data and service infrastructure**.

Inventory repositories remain persistence-oriented.

Inventory services own business rules, business operations, multi-entity coordination, and transaction orchestration.

The architecture does **not** introduce:

* a separate inventory repository framework;
* a separate inventory service framework;
* a generic inventory-domain framework;
* repository-owned transaction management;
* service logic embedded in repositories;
* or a second persistence abstraction.

The dependency direction remains:

Application / Route
        ↓
Inventory Service
        ↓
Inventory Repository
        ↓
Enterprise Data Infrastructure

Services may additionally depend on the enterprise transaction abstraction:

Inventory Service
        ↓
TransactionManager

---

## 3. Repository Ownership

Inventory repositories are owned by the Catering module and reside under:

app/modules/catering/repositories/

Inventory-specific repositories include, conceptually:

stock_item.py
location.py
balance.py
movement.py
transfer.py

These repositories remain part of the Catering module rather than becoming a new enterprise-wide inventory repository package.

The enterprise repository infrastructure remains under:

app/core/data/

The enterprise layer provides the reusable persistence mechanisms.

---

## 4. Repository Responsibilities

Inventory repositories are responsible for persistence access.

Typical responsibilities include:

* retrieving inventory entities;
* persisting inventory entities;
* querying inventory entities;
* applying enterprise filtering;
* applying enterprise sorting;
* applying enterprise pagination;
* supporting meaningful inventory-specific lookups;
* and exposing persistence-oriented operations required by services.

Repositories may provide domain-specific lookup methods when those methods represent a genuine persistence/query need.

Examples include:

* retrieving a StockItem by Product;
* retrieving a Location by code;
* retrieving a Balance by StockItem and Location;
* retrieving movements for a StockItem;
* retrieving transfers by source or destination location.

These operations remain persistence-oriented.

---

## 5. Repository Non-Responsibilities

Inventory repositories must not own business orchestration.

They must not independently determine:

* whether a transfer is valid;
* whether stock is sufficient;
* whether a movement may be posted;
* whether a balance may become negative;
* whether a transfer may be posted;
* whether a movement is immutable;
* whether a stock operation is authorized;
* or whether multiple entities must be changed atomically.

Those decisions belong to the service/application boundary.

Repositories also do not own:

* `begin`;
* `commit`;
* `rollback`;
* transaction retry;
* transfer orchestration;
* movement posting;
* or cross-repository business coordination.

This prevents business rules from being hidden inside persistence methods.

---

## 6. Reuse of Enterprise Repository Infrastructure

Inventory repositories reuse the existing enterprise repository architecture established by ADR-004.

The architecture therefore uses:

* `BaseRepository`;
* `SQLAlchemyRepository`;
* `QueryOptions`;
* `PaginatedResult`;
* existing filtering;
* existing sorting;
* existing pagination;
* and existing persistence conventions.

Inventory does not introduce parallel implementations of these capabilities.

The enterprise repository layer remains the reusable foundation.

---

## 7. Thin Repository Principle

Inventory repositories should remain thin.

A repository method should exist when it represents a meaningful persistence or query operation that cannot be expressed cleanly through the existing generic repository capabilities.

Generic CRUD operations should continue to use the enterprise repository mechanisms rather than creating redundant methods.

For example, a simple entity lookup or persistence operation should not automatically receive a custom repository method if the generic repository already supports it.

This avoids repository proliferation and premature abstraction.

---

## 8. Inventory Service Ownership

Inventory services are owned by the Catering module and reside under:

app/modules/catering/services/

Conceptually, inventory services include:

stock_item.py
location.py
balance.py
movement.py
transfer.py

The services provide the business-operation boundary for inventory.

They consume repositories and enterprise infrastructure rather than implementing persistence directly.

---

## 9. Service Responsibilities

Inventory services own:

* business validation;
* domain rules;
* lifecycle rules;
* business operation orchestration;
* cross-entity coordination;
* current-state evaluation;
* movement posting;
* transfer posting;
* balance coordination;
* transaction coordination;
* service-level exception handling;
* and other inventory-specific business behavior.

The service layer therefore represents the authoritative business-operation boundary.

---

## 10. Simple CRUD versus Domain Operations

Not every inventory operation requires complex orchestration.

Simple master-data operations may use the existing enterprise CRUD infrastructure where appropriate.

Examples include straightforward management of:

* StockItem configuration;
* InventoryLocation metadata.

Domain services are required when an operation contains meaningful business rules or coordinates multiple entities.

Examples include:

* posting a stock movement;
* creating or updating a balance as a consequence of a movement;
* posting a stock transfer;
* generating source and destination transfer effects;
* validating resulting inventory quantities;
* enforcing lifecycle transitions.

This distinction avoids both extremes:

* putting all logic into generic CRUD; and
* creating unnecessary custom services for trivial persistence operations.

---

## 11. StockItem Service Boundary

`StockItemService` owns StockItem-specific business behavior.

This includes, where applicable:

* Product-to-StockItem association;
* uniqueness rules;
* inventory configuration validation;
* threshold validation;
* activation/deactivation rules;
* and StockItem lifecycle behavior.

The service does not own Product master-data rules.

Product remains authoritative for product identity and master data.

---

## 12. InventoryLocation Service Boundary

`InventoryLocationService` owns location-specific business behavior.

This includes:

* location creation validation;
* code uniqueness handling;
* lifecycle/activation rules;
* and location-specific business validation.

The service does not introduce warehouse hierarchy or advanced warehouse-management behavior.

The location repository remains persistence-oriented.

---

## 13. StockBalance Service Boundary

`StockBalanceService` owns business operations involving current inventory state.

It may coordinate:

* balance retrieval;
* current quantity evaluation;
* balance creation where permitted;
* balance updates resulting from posted inventory effects;
* and inventory-state validation.

The balance service does not become an independent source of historical inventory truth.

`StockMovement` remains the historical ledger.

The service must preserve the invariant established by ADR-011:

> `StockBalance` owns current quantity; `StockMovement` owns historical inventory effects.

---

## 14. StockMovement Service Boundary

`StockMovementService` owns movement business rules and posting semantics.

It is responsible for:

* validating movement type;
* validating signed quantity;
* validating movement lifecycle;
* retrieving the relevant StockBalance;
* calculating the resulting quantity;
* preventing negative resulting balances;
* creating a missing balance for permitted positive effects;
* preventing missing-balance negative effects;
* creating the posted movement;
* and coordinating these changes atomically.

The service distinguishes between:

* draft movement creation; and
* posted movement effects.

A draft movement does not affect current inventory quantity.

A posted movement affects the authoritative StockBalance.

---

## 15. StockTransfer Service Boundary

`StockTransferService` owns transfer orchestration.

It is responsible for:

* validating StockItem;
* validating source and destination locations;
* validating positive transfer quantity;
* ensuring source and destination differ;
* checking source stock availability;
* coordinating source and destination balances;
* creating transfer movement effects;
* changing transfer lifecycle state;
* and ensuring atomic completion.

A posted transfer therefore coordinates multiple entities and requires a service-level transaction boundary.

The transfer repository does not perform this orchestration.

---

## 16. Cross-Repository Coordination

Inventory services may coordinate multiple repositories.

This is necessary for operations such as stock transfers.

For example:

id="9byp4f"
StockTransferService
    ├── TransferRepository
    ├── StockBalanceRepository
    ├── StockMovementRepository
    └── TransactionManager

This is an intentional service-layer responsibility.

Repositories do not coordinate other repositories.

A repository remains concerned with persistence for its own aggregate/entity boundary.

---

## 17. Transaction Boundary

Inventory business operations that modify multiple related records use the established enterprise transaction infrastructure.

The transaction boundary belongs to the service/application layer.

The architecture therefore follows:

Service
    ↓
TransactionManager
    ↓
Repositories

Repositories participate in the active transaction but do not own it.

For movement posting, the transaction covers:

* balance retrieval;
* balance creation/update;
* movement creation;
* movement status/posting state;
* and related persistence.

For transfer posting, the transaction covers:

* transfer status;
* source balance;
* destination balance;
* source movement;
* destination movement;
* and all associated persistence.

All required changes must commit together.

---

## 18. Repository Transaction Prohibition

Inventory repositories must not:

id="j1nmyk"
begin()
commit()
rollback()

as part of their normal persistence operations.

This rule prevents:

* partial commits;
* hidden transaction boundaries;
* nested transaction ambiguity;
* inconsistent multi-repository operations;
* and service-level rollback from becoming ineffective.

The enterprise `TransactionManager` remains the transaction abstraction.

---

## 19. Business Validation versus Database Constraints

Business validation belongs primarily to services.

Database constraints remain responsible for persistence invariants.

Examples of database-enforced invariants include:

* unique codes;
* foreign-key integrity;
* non-null requirements;
* unique StockItem/Product association;
* unique StockBalance `(stock_item_id, location_id)`;
* nonnegative StockBalance quantity;
* valid numeric precision.

Service validation covers rules that require business context, such as:

* transfer source and destination must differ;
* source stock must be sufficient;
* movement direction must match movement type;
* posted movement cannot be modified;
* a transfer may only be posted from an appropriate lifecycle state.

Database constraints and service validation therefore complement each other.

Neither replaces the other.

---

## 20. Service Exceptions

Inventory services use the established enterprise service exception conventions.

Business failures should be represented through appropriate service-layer exceptions rather than raw database exceptions being exposed directly to callers.

Examples include:

* validation failure;
* entity not found;
* business conflict;
* invalid lifecycle operation;
* insufficient stock;
* and operation failure.

Repositories remain responsible for persistence interaction and should not become the primary business-exception layer.

---

## 21. Dependency Direction

The dependency direction is intentionally one-way:

Enterprise Infrastructure
        ↑
Catering Inventory Repository
        ↑
Catering Inventory Service
        ↑
Application Boundary

Services depend on repository abstractions/implementations and enterprise transaction infrastructure.

Repositories depend on enterprise data infrastructure.

The enterprise infrastructure must not depend on Catering Inventory.

Inventory therefore remains a consumer of the enterprise platform rather than becoming a dependency of it.

---

## 22. Security and Governance Boundary

Inventory services operate under the enterprise security and governance architecture established by ADR-006.

Authorization remains the responsibility of the enterprise authorization mechanism.

Inventory-specific permissions remain owned by the Catering module.

The service layer enforces business rules after authorization.

Services do not implement:

* authentication;
* RBAC;
* permission evaluation;
* audit infrastructure;
* compliance infrastructure;
* or governance infrastructure.

Enterprise audit and governance remain authoritative.

---

## 23. Audit Boundary

Inventory business records such as movements and transfers provide business history.

They do not replace enterprise audit.

The service boundary must therefore integrate with existing enterprise audit mechanisms where required without embedding a second audit framework inside Inventory.

This preserves the distinction between:

Inventory business history
        +
Enterprise audit history

---

## 24. Query and Reporting Boundary

Inventory services and repositories reuse the existing enterprise query infrastructure.

Query concerns such as:

* filtering;
* sorting;
* pagination;
* searching;
* date ranges;
* status;
* location;
* stock item;
* movement type;
* and transfer references

should use existing `QueryOptions` and repository mechanisms wherever applicable.

Reporting remains a consumer of authoritative inventory data.

Inventory does not create a separate reporting/query architecture.

---

## 25. Current-State Evaluation

Inventory services may calculate derived business states such as stock status.

For example, stock state may be derived from:

* current StockBalance quantity;
* minimum level;
* reorder level;
* and StockItem activity.

Such status is derived rather than persisted as a second authoritative state.

This follows ADR-009 and ADR-011.

The service layer therefore evaluates business state without creating duplicate persistence.

---

## 26. Posted Inventory Immutability

Services enforce the immutability rules established by ADR-012 and ADR-013.

Posted movements must not be rewritten.

Posted transfers must not be destructively altered in ways that rewrite inventory history.

Corrections should use compensating transactions or a future explicitly designed reversal mechanism.

Repositories must not expose convenience operations that undermine these business rules.

---

## 27. Inventory Repository/Service Matrix

| Component         | Repository                       | Service                                   |
| ----------------- | -------------------------------- | ----------------------------------------- |
| StockItem         | Persistence/query                | Business validation/lifecycle             |
| InventoryLocation | Persistence/query                | Validation/lifecycle                      |
| StockBalance      | Persistence/current-state access | Balance rules/state coordination          |
| StockMovement     | Persistence/ledger access        | Movement validation/posting               |
| StockTransfer     | Persistence/transfer access      | Transfer validation/posting/orchestration |

This division provides a consistent boundary across the inventory domain.

---

## 28. Alternatives Considered

### 28.1 Put inventory business rules in repositories

Rejected.

Repositories are persistence-oriented and would become difficult to test, reuse, and coordinate.

### 28.2 Put all inventory behavior in generic CRUD services

Rejected.

Stock movement and transfer operations contain domain-specific business rules and multi-entity orchestration that generic CRUD cannot safely represent.

### 28.3 Create a generic InventoryRepository framework

Rejected.

The current domain does not justify a new enterprise abstraction. Existing repository infrastructure is sufficient.

### 28.4 Create a generic InventoryService framework

Rejected.

The current inventory services have different responsibilities and do not justify premature generalization.

### 28.5 Allow repositories to commit independently

Rejected.

Independent commits would undermine atomic movement and transfer operations.

### 28.6 Introduce a separate inventory transaction manager

Rejected.

The established enterprise `TransactionManager` already provides the required abstraction.

### 28.7 Introduce a second inventory persistence layer

Rejected.

Inventory must reuse the existing SQLAlchemy and enterprise data architecture.

### 28.8 Move inventory rules into database triggers

Rejected.

Database constraints are appropriate for persistence invariants, but business orchestration should remain explicit and testable in services.

---

## 29. Architectural Invariants

The following invariants apply:

1. Inventory repositories remain persistence-oriented.
2. Inventory services own inventory business rules.
3. Services may coordinate multiple repositories.
4. Repositories do not coordinate other repositories.
5. Repositories do not own transaction lifecycle.
6. Services use the enterprise `TransactionManager`.
7. StockBalance remains authoritative for current quantity.
8. StockMovement remains authoritative for historical inventory effects.
9. StockTransfer remains authoritative for transfer business context.
10. Posted movement effects are immutable.
11. Posted transfers are not destructively rewritten.
12. Business validation remains separate from authorization.
13. Enterprise security remains authoritative.
14. Enterprise audit remains authoritative.
15. Existing filtering, sorting, pagination, and query infrastructure is reused.
16. No parallel inventory repository framework is introduced.
17. No parallel inventory service framework is introduced.
18. No duplicate product or inventory-item registry is introduced.
19. No separate transaction framework is introduced.
20. Inventory remains bounded within the Catering module.

---

## 30. Implementation Alignment

The architecture aligns with the existing Catering implementation:

app/modules/catering/
├── repositories/
│   ├── product.py
│   ├── product_category.py
│   ├── stock_item.py
│   ├── location.py
│   ├── balance.py
│   ├── movement.py
│   └── transfer.py
│
└── services/
    ├── product.py
    ├── product_category.py
    ├── stock_item.py
    ├── location.py
    ├── balance.py
    ├── movement.py
    └── transfer.py

The implementation reuses enterprise infrastructure under:

app/core/data/
app/core/crud/
app/core/execution/
app/core/services/
app/core/security/

No separate inventory infrastructure is required.

---

## 31. Consequences

### Positive consequences

* Clear separation of persistence and business logic.
* Consistent inventory architecture across all inventory entities.
* Atomic multi-entity operations.
* Easier testing of business rules.
* Reuse of mature enterprise infrastructure.
* Reduced duplication.
* Clear dependency direction.
* Stronger protection against hidden transaction boundaries.
* Better maintainability as additional inventory operations are introduced.

### Negative consequences

* Inventory operations require explicit service orchestration.
* Multi-entity operations require careful transaction handling.
* Some simple operations may require coordination between generic CRUD and domain services.
* The service layer becomes responsible for more explicit business logic.

These consequences are accepted because inventory integrity and architectural consistency are more important than minimizing service-layer complexity.

---

## 32. Out of Scope

This ADR does not establish:

* a new enterprise repository framework;
* a new enterprise service framework;
* a generic domain-service framework;
* a new transaction framework;
* warehouse-management architecture;
* procurement architecture;
* purchasing repositories/services;
* sales repositories/services;
* financial repositories/services;
* invoice repositories/services;
* inventory valuation services;
* replenishment services;
* supplier/customer services;
* distributed transactions;
* event-driven distributed orchestration;
* background job architecture;
* speculative concurrency infrastructure;
* or a separate API service layer.

Those concerns require separate architectural decisions if introduced later.

---

## 33. Approval

This ADR formally establishes the repository and service boundary for the Catering Inventory domain.

The status remains **Planned for documentation** until:

1. the authoritative Phase 2 roadmap is reconciled;
2. the ADR is verified;
3. the documentation checkpoint is committed; and
4. the working tree is confirmed clean.

Upon completion of those steps, the ADR status should be reconciled to:

**Approved — Retrospective**

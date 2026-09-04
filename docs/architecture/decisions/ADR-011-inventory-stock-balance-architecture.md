
# ADR-011: Inventory Stock Balance Architecture

**Status:** Approved — Retrospective
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory stock balance ownership, current-state quantity, uniqueness, invariants, relationships, and transactional update responsibilities

**Related ADRs:**

* ADR-001 — Phase 2 Business Module Architecture & Strategy
* ADR-004 — Catering Repository Architecture
* ADR-005 — Catering Service Architecture
* ADR-006 — Catering Security & Governance Integration
* ADR-008 — Catering Inventory Domain Boundary
* ADR-009 — Inventory Stock Item Architecture
* ADR-010 — Inventory Location Architecture

---

## 1. Context

The Catering inventory domain requires a reliable representation of the current quantity of each stock item at each inventory location.

The inventory model already separates several responsibilities:

* `Product` remains the authoritative Catering product master.
* `StockItem` represents the participation and inventory configuration of a product.
* `InventoryLocation` identifies where stock may be held.
* `StockMovement` records historical inventory effects.
* `StockTransfer` represents movement of stock between locations.

A separate current-state representation is therefore required to answer operational questions such as:

* How much of a stock item is currently available at a location?
* Does a stock item currently exist at a particular location?
* Has a proposed issue or transfer resulted in sufficient stock?
* What is the current quantity against minimum and reorder thresholds?
* What quantity should be presented to inventory users without replaying the entire movement history?

The current quantity must not be stored on `StockItem`, because a stock item can exist at multiple locations and therefore requires location-specific quantities.

The current quantity must also not be derived exclusively from the movement ledger for every operational request. The movement ledger remains the historical source of inventory effects, while a persisted balance provides efficient current-state access.

This ADR establishes the architectural ownership and invariants of that persisted balance.

---

## 2. Decision

`StockBalance` is the authoritative persisted representation of the **current inventory quantity for a specific StockItem at a specific InventoryLocation**.

Each balance represents exactly one:

> `StockItem × InventoryLocation`

combination.

The architecture therefore adopts the following invariant:

> **StockBalance owns the current quantity at a location; StockMovement owns the historical inventory effects that produced that quantity.**

`StockBalance` is an inventory-domain state model and is owned by the Catering inventory boundary.

The balance is updated through the established Catering inventory service and transaction boundary. Repositories provide persistence access but do not independently calculate or mutate inventory state outside the service orchestration boundary.

---

## 3. StockBalance Responsibility

`StockBalance` is responsible for representing current quantity.

It is responsible for:

* associating a `StockItem` with an `InventoryLocation`;
* storing the current quantity at that location;
* providing efficient current-state inventory queries;
* supporting inventory threshold evaluation;
* serving as the current-state target of posted inventory effects;
* participating in atomic inventory transaction processing.

It is not responsible for:

* product master data;
* stock-item configuration;
* historical movement records;
* purchasing;
* supplier management;
* expense accounting;
* income accounting;
* invoicing;
* stock valuation;
* procurement workflows;
* transfer orchestration;
* authorization;
* audit infrastructure;
* enterprise reporting infrastructure.

---

## 4. Relationship to StockItem

`StockItem` identifies the inventory-controlled representation of an existing Catering `Product`.

A StockItem may be held at zero, one, or multiple inventory locations.

Therefore:

```text
Product
   │
   │ 1 : 0..1
   ▼
StockItem
   │
   │ 1 : many
   ▼
StockBalance
   │
   │ many : 1
   ▼
InventoryLocation
```

The current quantity must not be stored directly on `StockItem`.

For example, if a Catering stock item exists in:

* Main Store;
* Kitchen Store; and
* Event Store;

each location requires an independent quantity.

The architecture therefore rejects a single `current_quantity` field on `StockItem`.

---

## 5. Relationship to InventoryLocation

`InventoryLocation` identifies where stock may be held.

`StockBalance` supplies the quantity held there.

The relationship is therefore:

> `InventoryLocation` identifies the location; `StockBalance` identifies the quantity of a StockItem at that location.

A location may contain many stock items.

A stock item may have balances at many locations.

The combination of:

```text
stock_item_id
location_id
```

therefore defines the identity of a balance.

---

## 6. Balance Identity and Uniqueness

There must be at most one `StockBalance` for each `StockItem × InventoryLocation` pair.

The database must enforce this invariant through a unique constraint on:

```text
(stock_item_id, location_id)
```

This prevents duplicate current-state records representing the same inventory position.

The repository and service layers may also perform appropriate existence checks, but application-level checks do not replace the database uniqueness constraint.

The database remains authoritative for the persistence invariant.

---

## 7. Quantity Representation

`StockBalance.quantity` represents the current quantity available for the corresponding stock item at the corresponding location.

The quantity uses the established inventory numeric precision:

```text
Numeric(18,3)
```

This supports whole-unit and fractional inventory quantities without introducing a second quantity representation.

The architecture does not prescribe a particular unit-of-measure framework at this stage.

Unit-of-measure management remains outside the current inventory architecture scope.

---

## 8. Non-Negative Quantity Invariant

A persisted StockBalance must never contain a negative quantity.

Therefore:

```text
quantity >= 0
```

is an inventory persistence invariant.

The service layer is responsible for preventing a posted inventory effect from producing a negative resulting balance.

The database constraint complements that service-level validation.

Both layers have distinct responsibilities:

* **Service layer:** enforce business rules before mutation.
* **Database:** prevent invalid persisted state.

The database constraint must not be treated as the primary business-rule engine.

---

## 9. Zero Quantity Is Valid

A zero quantity is a valid inventory state.

A balance with:

```text
quantity = 0
```

may legitimately exist when stock has been completely consumed or otherwise reduced to zero.

Zero therefore does not imply that the balance record must be deleted.

Retaining a zero balance provides stable current-state representation and avoids unnecessary creation/deletion churn.

The architecture does not require automatic deletion of zero-quantity balances.

---

## 10. Balance Creation

A StockBalance may be created when a posted inventory effect introduces stock for a StockItem at a location for which no balance currently exists.

For example:

```text
Current balance: none
Posted receipt: +50
Resulting balance: 50
```

A positive inventory effect may therefore create the balance record.

A negative effect cannot create a balance where none exists because that would require a negative resulting quantity.

For example:

```text
Current balance: none
Posted issue: -10
Result: rejected
```

The service layer is responsible for enforcing this rule.

---

## 11. Balance Updates

Posted inventory effects update the corresponding StockBalance.

Conceptually:

```text
new_balance = current_balance + posted_effect
```

For example:

```text
Current balance     100
Receipt              +25
-----------------------
New balance          125
```

or:

```text
Current balance     100
Issue                -20
-----------------------
New balance           80
```

The balance update and corresponding movement creation/posting must occur within the same transaction boundary.

A successful posted movement must not leave the balance unchanged.

A failed posting must not leave a partially updated balance.

---

## 12. StockMovement as Historical Ledger

`StockMovement` remains the authoritative historical record of inventory effects.

It records events such as:

* opening balances;
* receipts;
* issues;
* adjustments; and
* transfer effects.

The movement ledger answers:

> What inventory effects have occurred?

The balance answers:

> What is the current quantity?

These responsibilities are complementary rather than competing.

The architecture therefore does not replace the movement ledger with StockBalance, nor does it require operational current-state queries to replay the entire movement history.

---

## 13. Ledger and Balance Consistency

For a given StockItem and InventoryLocation, the StockBalance must remain consistent with posted inventory effects.

Conceptually:

```text
Current Balance
    =
Opening / Initial State
    +
Sum of Posted Inventory Effects
```

The exact historical reconstruction may depend on the interpretation of opening balances and transfer effects, but the persisted balance must represent the result of all successfully posted inventory effects applicable to that location.

Draft movements do not affect StockBalance.

Only successfully posted inventory effects may change current inventory state.

---

## 14. Draft Versus Posted State

StockBalance represents committed current state.

Therefore:

* DRAFT movements do not change StockBalance.
* POSTED movements change StockBalance.
* Failed postings do not change StockBalance.
* Cancelled or rejected operations do not change StockBalance.

This preserves the distinction between a proposed inventory operation and an actual inventory effect.

---

## 15. Transactional Integrity

Updating a StockBalance is a transactional operation.

The established enterprise transaction infrastructure remains authoritative.

The service/application boundary coordinates:

1. validation of the inventory operation;
2. retrieval of the current balance;
3. calculation of the resulting quantity;
4. validation of the resulting quantity;
5. creation or update of StockBalance;
6. creation/posting of the corresponding StockMovement;
7. transaction commit.

These operations must succeed or fail atomically.

Repositories do not own `begin`, `commit`, or `rollback`.

This follows the transaction boundary established by the Catering service architecture and the enterprise transaction infrastructure.

---

## 16. Transfer Effects

Stock transfers affect two balances:

```text
Source Location
    quantity - X

Destination Location
    quantity + X
```

The two effects must be processed atomically.

`StockTransfer` remains responsible for the transfer operation itself, while `StockBalance` remains responsible for the resulting current quantity at each affected location.

The architecture therefore avoids embedding transfer orchestration inside `StockBalance`.

Transfer-specific architectural decisions are documented separately under ADR-013.

---

## 17. Threshold Evaluation

StockBalance provides the current quantity required for inventory-level evaluation.

Threshold configuration remains on `StockItem`:

* `minimum_level`;
* `reorder_level`.

The resulting status is derived rather than persisted on StockBalance.

Conceptually:

```text
StockBalance.quantity
        +
StockItem.minimum_level
        +
StockItem.reorder_level
        ↓
Derived inventory status
```

This avoids storing duplicate or potentially stale status information.

The balance remains responsible for quantity, while threshold configuration remains the responsibility of StockItem.

---

## 18. Service Ownership

The Catering inventory service layer owns business operations affecting StockBalance.

The service layer is responsible for:

* validating stock item existence;
* validating location existence;
* retrieving the current balance;
* validating movement quantity;
* preventing negative resulting quantities;
* creating a balance when appropriate;
* updating an existing balance;
* coordinating movement creation;
* coordinating transaction boundaries;
* maintaining business consistency.

The service layer must not delegate business-rule ownership to repositories.

---

## 19. Repository Responsibility

The StockBalance repository remains persistence-oriented.

It may provide operations such as:

* retrieve by identifier;
* retrieve by StockItem and location;
* query balances using enterprise `QueryOptions`;
* persist new balances;
* update balances;
* support ordinary repository lifecycle operations.

It does not own:

* inventory business rules;
* movement posting;
* transfer orchestration;
* transaction lifecycle;
* threshold interpretation;
* authorization;
* audit policy.

The repository therefore remains thin and consistent with ADR-004.

---

## 20. Query and Filtering

Inventory balance queries reuse the enterprise data infrastructure.

Existing capabilities such as:

* filtering;
* sorting;
* pagination;
* search;
* field selection;
* inactive-record handling;

remain available through the established `QueryOptions` and repository framework.

No separate inventory query framework is introduced.

Useful balance query dimensions may include:

* stock item;
* product;
* location;
* active status;
* quantity;
* threshold-related application filtering.

Any additional query capability should be added only where an actual business requirement justifies it.

---

## 21. Security and Governance

StockBalance operations are subject to the existing enterprise security and governance architecture.

Catering does not introduce a separate:

* authorization engine;
* permission registry;
* security policy framework;
* audit framework;
* governance framework.

Application and service boundaries use the enterprise authorization mechanisms established under ADR-006.

Business inventory records do not replace enterprise audit records.

---

## 22. Persistence and Model Conventions

StockBalance follows established CDCS-EMP persistence conventions.

It uses the existing:

* enterprise ORM foundation;
* `BaseModel`;
* audit/timestamp conventions where applicable;
* soft-delete conventions where applicable;
* database migration framework;
* SQL Server persistence;
* repository infrastructure.

No parallel inventory ORM base or persistence framework is introduced.

The balance model remains inside the Catering module because the inventory capability is owned by Catering.

---

## 23. Lifecycle and Deletion

StockBalance represents current state and may be affected by the lifecycle of the associated StockItem and InventoryLocation.

Historical inventory integrity must not be compromised by destructive deletion.

In particular:

* posted movements are not deleted to correct balances;
* historical inventory effects remain preserved;
* corrections occur through compensating inventory effects;
* deactivation of a StockItem or InventoryLocation does not erase historical balances or movements.

Any cleanup or archival capability is outside the current architectural scope.

---

## 24. Failure Handling

Inventory balance operations must fail safely.

Examples include:

* nonexistent StockItem;
* nonexistent InventoryLocation;
* inactive inventory entities where business rules prohibit operation;
* negative resulting quantity;
* invalid movement type;
* invalid quantity;
* duplicate balance creation;
* transaction failure.

A failed operation must not leave a partially updated balance.

Established enterprise service exceptions and transaction failure handling remain authoritative.

No new inventory-specific exception hierarchy is introduced unless a future requirement demonstrates that existing exception contracts are insufficient.

---

## 25. Concurrency Considerations

The current architecture establishes atomic transactional updates but does not introduce a new inventory-specific locking framework.

Concurrency control must rely initially on the established database transaction infrastructure and SQL Server transactional behavior.

Explicit row-locking or optimistic-concurrency mechanisms are not added merely for the balance model.

If production requirements demonstrate a concrete concurrency problem, the issue should be addressed through a separate architectural decision rather than introducing speculative locking into the initial inventory foundation.

---

## 26. Reporting Relationship

StockBalance provides an efficient current-state source for operational reporting.

StockMovement provides the historical ledger source for movement and activity reporting.

The existing enterprise reporting framework remains authoritative.

The inventory module does not introduce a separate reporting engine or reporting persistence model.

Future inventory reports may combine:

* StockItem;
* Product;
* InventoryLocation;
* StockBalance;
* StockMovement;

through the existing reporting/data-provider architecture.

---

## 27. Alternatives Considered

### 27.1 Store Current Quantity on StockItem

Rejected.

A StockItem can exist at multiple locations, so one quantity cannot represent location-specific inventory.

### 27.2 Calculate Current Quantity Exclusively from StockMovement

Rejected as the operational current-state model.

Although the ledger remains essential for historical traceability, replaying the entire ledger for every current-state query would unnecessarily increase query complexity and operational cost.

### 27.3 Store One Balance per StockItem Without Location

Rejected.

Inventory quantities are location-specific.

### 27.4 Allow Multiple Balances per StockItem and Location

Rejected.

Duplicate balances would create ambiguous current state and undermine inventory integrity.

### 27.5 Let Repositories Own Balance Mutation Rules

Rejected.

Business rules belong to services; repositories remain persistence-oriented.

### 27.6 Introduce a Dedicated Inventory Transaction Framework

Rejected.

The enterprise transaction infrastructure already provides the required boundary.

### 27.7 Persist Derived Inventory Status

Rejected.

Inventory status can be derived from current quantity and StockItem thresholds and should not become duplicated mutable state.

---

## 28. Architectural Invariants

The following invariants are established:

1. `StockBalance` is owned by the Catering inventory domain.
2. Each balance represents one StockItem at one InventoryLocation.
3. `(stock_item_id, location_id)` is unique.
4. `quantity` uses `Numeric(18,3)`.
5. `quantity >= 0`.
6. Zero quantity is valid.
7. StockItem does not store current location-specific quantity.
8. StockMovement remains the historical inventory ledger.
9. Draft movements do not affect StockBalance.
10. Posted movements affect StockBalance.
11. Balance mutation and movement posting occur atomically.
12. Transfer operations update source and destination balances atomically.
13. Services own balance business rules and orchestration.
14. Repositories remain persistence-oriented.
15. Existing enterprise transaction infrastructure is authoritative.
16. Existing enterprise security and governance infrastructure is authoritative.
17. No parallel inventory persistence, transaction, security, query, or reporting framework is introduced.
18. Historical inventory effects are not destructively deleted.

---

## 29. Implementation Alignment

The architectural decision is aligned with the existing inventory implementation:

* `StockBalance` exists under the Catering inventory model boundary.
* The model represents `StockItem × InventoryLocation`.
* The database enforces uniqueness for the pair.
* Quantity uses the established `Numeric(18,3)` representation.
* Non-negative quantity is enforced at the persistence/business boundary.
* StockMovement posting updates or creates the corresponding balance.
* StockMovement posting uses the established transaction manager.
* StockTransfer remains a separate domain operation.
* Inventory services coordinate repository and transaction behavior.
* Enterprise repository infrastructure is reused.

No parallel inventory persistence or transaction architecture is required.

---

## 30. Scope Boundaries

This ADR does not establish architecture for:

* purchasing;
* supplier management;
* procurement;
* accounts payable;
* expense accounting;
* revenue;
* invoicing;
* inventory valuation;
* cost accounting;
* warehouse management;
* warehouse hierarchy;
* bin management;
* barcode/RFID infrastructure;
* demand forecasting;
* automated replenishment;
* batch/lot tracking;
* serial-number tracking;
* expiry management;
* unit-of-measure conversion;
* advanced concurrency control;
* inventory reporting architecture;
* cross-module distributed transactions.

Those capabilities require separate architectural decisions if and when they become necessary.

---

## 31. Consequences

### Positive consequences

* Current inventory state is explicit and efficiently queryable.
* Location-specific quantities are correctly represented.
* Duplicate balance records are prevented.
* Negative stock state is prevented.
* Historical movement records remain distinct from current state.
* Inventory posting can update ledger and current state atomically.
* Existing enterprise repository, transaction, security, governance, and reporting infrastructure is reused.
* The architecture remains simple enough for the initial Catering implementation.
* Future inventory reporting can consume both current-state and historical sources.

### Trade-offs

* Balance and movement data must remain consistent.
* Posting logic must update two related representations.
* Future concurrency requirements may require additional architectural work.
* Historical reconstruction and reconciliation require consideration of both ledger and persisted balance.

These trade-offs are accepted because the separation between current state and historical ledger provides a clear and operationally useful inventory model.

---

## 32. Decision Summary

The CDCS-EMP Catering inventory architecture adopts `StockBalance` as the authoritative current quantity for each StockItem at each InventoryLocation.

The resulting architectural relationship is:

```text
Product
   ↓
StockItem
   ↓
StockBalance ← InventoryLocation
   ↑
StockMovement
```

More precisely:

> **StockItem defines what is inventory-controlled; InventoryLocation defines where it is held; StockBalance defines how much is currently held there; StockMovement defines how the quantity changed; StockTransfer defines movement between locations.**

This separation establishes clear ownership, preserves historical traceability, supports efficient operational queries, and reuses the established CDCS-EMP enterprise architecture.

---

## 33. Approval

**Status:** Approved — Retrospective

This ADR becomes **Approved — Retrospective** after the corresponding roadmap reconciliation and final Group 10 checkpoint are completed.

# ADR-012: Inventory Stock Movement Ledger Architecture

**Status:** Planned for documentation
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory stock movement ledger ownership, movement semantics, lifecycle, immutability, posting effects, and relationship to current stock balances

**Related ADRs:**

* ADR-001 — Phase 2 Business Module Architecture & Strategy
* ADR-004 — Catering Repository Architecture
* ADR-005 — Catering Service Architecture
* ADR-006 — Catering Security & Governance Integration
* ADR-008 — Catering Inventory Domain Boundary
* ADR-009 — Inventory Stock Item Architecture
* ADR-010 — Inventory Location Architecture
* ADR-011 — Inventory Stock Balance Architecture

---

## 1. Context

The Catering inventory domain requires a reliable historical record of all inventory effects.

`StockBalance`, established by ADR-011, represents the current quantity of a StockItem at an InventoryLocation. It does not, however, explain how that quantity was produced.

Inventory operations must therefore have a durable historical ledger capable of answering questions such as:

* When did stock enter or leave the inventory?
* What type of inventory operation occurred?
* How much quantity was affected?
* At which location did the effect occur?
* Was the operation only drafted or actually posted?
* What reference or reason explains the operation?
* When was the inventory effect posted?
* Which transfer produced a particular movement?
* How can an incorrect posted operation be corrected without deleting history?

The inventory architecture therefore requires a distinct historical movement model.

`StockMovement` provides that historical ledger.

The ledger must remain separate from current-state balance storage while maintaining transactional consistency with it.

---

## 2. Decision

`StockMovement` is the authoritative historical ledger of inventory effects within the Catering inventory domain.

Each movement represents a specific inventory effect involving:

* a StockItem;
* an InventoryLocation;
* a movement type;
* a signed quantity;
* a lifecycle status;
* an occurrence timestamp;
* optional business reference and reason;
* posting information where applicable.

The architecture adopts the following invariant:

> **StockMovement records what inventory effect occurred; StockBalance records the resulting current quantity.**

`StockMovement` is therefore an append-oriented business record rather than a mutable current-state quantity store.

Posted movements are immutable.

Corrections to posted movements occur through compensating inventory movements rather than modification or deletion of the original posted record.

---

## 3. Responsibility

`StockMovement` is responsible for preserving the historical inventory effect.

It is responsible for:

* identifying the affected StockItem;
* identifying the affected InventoryLocation;
* identifying the movement type;
* recording the signed quantity;
* recording lifecycle status;
* recording when the inventory event occurred;
* recording when it was posted;
* preserving optional operational references;
* preserving the historical reason for the movement;
* supporting inventory reconciliation and historical reporting.

It is not responsible for:

* storing current inventory quantity;
* product master data;
* stock-item configuration;
* location configuration;
* transfer orchestration;
* purchasing;
* supplier management;
* expense accounting;
* income accounting;
* invoicing;
* stock valuation;
* authorization;
* audit infrastructure;
* enterprise reporting infrastructure;
* transaction lifecycle management.

---

## 4. Relationship to StockBalance

`StockMovement` and `StockBalance` have complementary responsibilities.

StockMovement
     │
     │ posted inventory effect
     ▼
StockBalance

More precisely:

Historical ledger                  Current state

StockMovement  ───────────────►  StockBalance
     │                                  │
     │                                  │
"What happened?"                 "What is there now?"

A posted movement changes the applicable StockBalance.

A draft movement does not.

The two representations must be updated consistently within the established transaction boundary.

---

## 5. Relationship to StockItem

Every StockMovement applies to a specific StockItem.

The StockItem identifies the inventory-controlled representation of a Catering Product.

The movement does not duplicate Product master data.

Therefore the movement references the StockItem rather than directly embedding product information.

This preserves the established ownership boundary:

Product
   ↓
StockItem
   ↓
StockMovement

---

## 6. Relationship to InventoryLocation

Each ordinary StockMovement identifies the inventory location affected by the movement.

The location provides the spatial context required to update the corresponding StockBalance.

The relationship is therefore:

StockMovement
    ├── StockItem
    └── InventoryLocation

The combination identifies the inventory position affected by the movement.

Transfer operations are treated separately because a transfer has both a source and destination location. ADR-013 establishes the transfer-specific architecture.

---

## 7. Movement Quantity

`StockMovement.quantity` is a signed inventory quantity.

The sign represents the effect on the affected inventory balance.

Conceptually:

positive quantity → increases stock
negative quantity → decreases stock

Examples:

Receipt       +50
Issue         -10
Adjustment     +5
Adjustment     -3
Opening        +100
Opening        -5

The quantity uses the established inventory numeric precision:

Numeric(18,3)

Zero is not a valid movement quantity.

A movement must represent an actual inventory effect.

---

## 8. Movement Types

The initial inventory architecture defines the following movement types:

* `OPENING_BALANCE`
* `RECEIPT`
* `ISSUE`
* `ADJUSTMENT`
* `TRANSFER`

These movement types provide explicit semantic classification of inventory effects.

### 8.1 OPENING_BALANCE

Represents an initial inventory quantity being established.

Opening balances may use the signed quantity required to establish the intended initial state, subject to the resulting balance remaining valid.

### 8.2 RECEIPT

Represents stock entering a location.

Receipt quantity must be positive.

RECEIPT +50

### 8.3 ISSUE

Represents stock leaving a location.

Issue quantity must be negative.

ISSUE -10

### 8.4 ADJUSTMENT

Represents a corrective inventory quantity change.

Adjustment quantity may be positive or negative, provided the resulting StockBalance remains non-negative.

### 8.5 TRANSFER

Represents an inventory movement associated with a stock transfer.

Transfer movements are not independently posted through the ordinary single-location movement posting operation.

Transfer posting is orchestrated by the StockTransfer service and produces the appropriate source and destination effects atomically.

---

## 9. Signed Quantity Semantics

Movement type and quantity sign must remain semantically consistent.

The initial rules are:

| Movement Type     | Quantity Rule                       |
| ----------------- | ----------------------------------- |
| `OPENING_BALANCE` | Signed quantity permitted           |
| `RECEIPT`         | Positive only                       |
| `ISSUE`           | Negative only                       |
| `ADJUSTMENT`      | Positive or negative                |
| `TRANSFER`        | Reserved for transfer orchestration |

A movement with zero quantity is invalid.

These rules are business validation rules owned by the inventory service layer.

---

## 10. Lifecycle Status

StockMovement has an explicit lifecycle distinction between proposed and committed inventory effects.

The initial lifecycle states are:

* `DRAFT`
* `POSTED`

### DRAFT

A DRAFT movement represents a proposed inventory operation.

It:

* exists as a business record;
* may be reviewed or validated;
* does not change StockBalance;
* does not represent committed inventory state.

### POSTED

A POSTED movement represents a committed inventory effect.

It:

* changes the applicable StockBalance;
* has posting metadata;
* becomes immutable;
* participates in historical inventory reporting and reconciliation.

---

## 11. Draft Movement Semantics

Draft movements must not affect current inventory.

For example:

Current balance: 100
Draft issue:     -20
Displayed balance: 100

The draft movement remains historical/proposed information until posting.

This distinction prevents uncommitted inventory operations from appearing as actual stock.

---

## 12. Posted Movement Semantics

Posting converts a valid inventory movement into a committed inventory effect.

Conceptually:

DRAFT
  │
  │ validate and post
  ▼
POSTED
  │
  ├── update StockBalance
  └── preserve historical ledger record

Posting must occur through the established inventory service and transaction boundary.

A movement must not be considered posted merely because its status field has been changed independently of its balance effect.

---

## 13. Posting Atomicity

Movement posting and balance mutation are one transactional operation.

The service/application boundary coordinates:

1. movement validation;
2. StockItem validation;
3. InventoryLocation validation;
4. current StockBalance retrieval;
5. resulting quantity calculation;
6. resulting quantity validation;
7. StockBalance creation or update;
8. movement posting;
9. posting metadata;
10. transaction commit.

These operations must succeed or fail atomically.

If posting fails:

* the movement must not become a partially committed posted effect;
* the StockBalance must not be left partially changed.

The existing enterprise transaction infrastructure remains authoritative.

---

## 14. Resulting Balance Validation

For ordinary inventory movements:

new_balance = current_balance + movement.quantity

The resulting balance must satisfy:

new_balance >= 0

A movement that would produce a negative balance must be rejected.

For example:

Current balance: 25
Issue:           -30
Result:           -5

The operation must fail.

The movement must not be posted and the balance must remain unchanged.

---

## 15. Balance Creation During Posting

If no StockBalance exists for the StockItem and InventoryLocation:

* a positive effect may create the balance;
* a negative effect must fail;
* a zero effect is invalid.

Example:

No existing balance
Receipt +50
        ↓
Create StockBalance(quantity=50)

This rule is enforced by the inventory service.

---

## 16. Posted Movement Immutability

Once posted, a StockMovement is immutable.

The following must not be altered after posting:

* StockItem;
* InventoryLocation;
* movement type;
* quantity;
* occurrence timestamp;
* posting state;
* posting timestamp;
* business reference;
* reason;
* transfer association.

The purpose of immutability is to preserve the integrity of the historical ledger.

A posted movement represents an event that has already affected inventory state.

Changing the event afterward would undermine historical traceability and reconciliation.

---

## 17. Corrections Through Compensating Movements

Incorrect posted movements are corrected through new compensating movements.

The original movement remains preserved.

For example:

Original receipt       +100
Incorrect by             +20
Compensating adjustment  -20
-----------------------------
Net effect              +100

The correction therefore preserves:

* the original event;
* the reason it was corrected;
* the corrective event;
* the resulting current balance.

The architecture rejects editing or deleting the original posted movement as the normal correction mechanism.

---

## 18. Deletion Rules

Posted StockMovement records must not be destructively deleted as part of ordinary inventory correction.

Historical inventory effects must remain available for:

* audit;
* reconciliation;
* operational investigation;
* reporting;
* accountability.

Draft records may be subject to lifecycle handling defined by the service layer, but no deletion mechanism is introduced solely for this ADR.

Any future archival strategy requires a separate architectural decision.

---

## 19. Occurrence and Posting Timestamps

The movement records both the business occurrence time and the posting time where applicable.

`occurred_at` represents when the inventory event occurred.

`posted_at` represents when the movement was committed as a posted inventory effect.

For a DRAFT movement, `posted_at` remains unset.

For a POSTED movement, `posted_at` is populated.

This distinction supports operational reporting and historical reconciliation.

---

## 20. Reference and Reason

StockMovement may contain operational context such as:

* reference;
* reason.

A reference can associate the movement with an external or business document identifier.

A reason explains why the movement occurred.

These fields support traceability without embedding purchasing, invoicing, finance, or other cross-module business structures into the inventory ledger.

---

## 21. Transfer Association

A StockMovement may carry an association with a StockTransfer where the movement is generated by a transfer operation.

Transfer-specific orchestration remains owned by StockTransfer.

The movement record provides the resulting ledger effect rather than becoming the transfer workflow itself.

This preserves the separation:

StockTransfer
     │
     │ orchestrates
     ▼
StockMovement
     │
     │ affects
     ▼
StockBalance

The detailed transfer architecture is documented separately in ADR-013.

---

## 22. Service Ownership

The Catering inventory service layer owns movement business operations.

The service is responsible for:

* validating movement type;
* validating quantity;
* validating StockItem;
* validating InventoryLocation;
* validating lifecycle transitions;
* validating resulting balances;
* coordinating StockBalance changes;
* setting posting metadata;
* enforcing immutability after posting;
* coordinating transaction boundaries;
* generating appropriate business exceptions.

Repositories remain persistence-oriented.

---

## 23. Repository Responsibility

The StockMovement repository provides persistence access.

It may support:

* retrieval by identifier;
* retrieval by StockItem;
* retrieval by InventoryLocation;
* filtering by movement type;
* filtering by status;
* filtering by occurrence date;
* filtering by reference;
* ordinary enterprise query capabilities.

It does not own:

* movement posting;
* movement business rules;
* balance mutation;
* transfer orchestration;
* transaction lifecycle;
* authorization policy.

The repository therefore remains consistent with ADR-004 and ADR-005.

---

## 24. Query Architecture

Historical movement queries reuse the enterprise data/query infrastructure.

Existing `QueryOptions` capabilities remain authoritative for:

* filtering;
* sorting;
* pagination;
* search;
* field selection;
* inactive-record handling where applicable.

Useful inventory movement filters may include:

* StockItem;
* InventoryLocation;
* movement type;
* lifecycle status;
* occurrence date range;
* posting date range;
* reference;
* transfer association.

No dedicated inventory query engine is introduced.

---

## 25. Security and Governance

StockMovement operations are governed by the existing enterprise security and governance architecture.

Catering continues to own the permissions associated with inventory capabilities, while the enterprise platform remains authoritative for:

* authentication;
* authorization evaluation;
* security policies;
* audit;
* compliance;
* governance.

The movement ledger itself is not a replacement for enterprise audit records.

Inventory-specific business history and enterprise security audit serve different purposes.

---

## 26. Audit Relationship

A StockMovement provides business-domain history.

Enterprise audit records provide governance and accountability history.

For example:

StockMovement:
"50 units received into Main Store."

Enterprise Audit:
"User X performed the stock-receipt operation at time Y."

The two records are complementary.

The inventory architecture does not introduce a second audit framework.

---

## 27. Reporting Relationship

StockMovement is the primary historical inventory source for reporting on:

* receipts;
* issues;
* adjustments;
* transfers;
* movement history;
* inventory activity over time;
* reconciliation.

StockBalance remains the primary current-state source.

The existing enterprise reporting framework consumes these sources through its established reporting/data-provider architecture.

No inventory-specific reporting framework is introduced.

---

## 28. Reconciliation

The movement ledger supports reconciliation of current inventory state.

Conceptually:

Opening / Initial State
          +
Posted Movement Effects
          =
Current StockBalance

A reconciliation process may compare the persisted StockBalance with the cumulative effect of posted movements.

Such reconciliation must not modify historical movements to make the numbers agree.

If a discrepancy is identified, the discrepancy must be investigated and corrected through an appropriate inventory adjustment or separate controlled process.

Automated reconciliation tooling is outside the scope of this ADR.

---

## 29. Concurrency

The initial movement architecture relies on the established transaction infrastructure and SQL Server transactional behavior.

No inventory-specific locking framework is introduced by this ADR.

The posting operation must remain atomic with the corresponding balance update.

If production requirements identify a concrete concurrency problem, a separate architectural decision should establish the appropriate optimistic or pessimistic concurrency strategy.

Speculative row-locking mechanisms are not introduced at this stage.

---

## 30. Failure Handling

Movement posting must fail safely.

Examples include:

* nonexistent StockItem;
* nonexistent InventoryLocation;
* invalid movement type;
* invalid quantity;
* zero quantity;
* invalid quantity sign;
* insufficient stock;
* invalid lifecycle transition;
* duplicate posting attempt;
* transaction failure.

A failed operation must not partially modify the movement ledger or StockBalance.

Existing enterprise service exceptions and transaction failure handling remain authoritative.

No separate inventory exception framework is introduced.

---

## 31. Architectural Alternatives Considered

### 31.1 Store Only Current Balance

Rejected.

Current quantity alone cannot provide historical traceability.

### 31.2 Calculate Current Balance Exclusively from the Ledger

Rejected as the operational current-state architecture.

The ledger remains the historical authority, but replaying the entire movement history for every current-state query would unnecessarily increase operational complexity.

### 31.3 Allow Posted Movement Editing

Rejected.

Editing historical events would undermine ledger integrity and reconciliation.

### 31.4 Delete Incorrect Posted Movements

Rejected.

Deletion would destroy the historical explanation of inventory state.

Compensating movements preserve both the original event and its correction.

### 31.5 Store Unsigned Quantities

Rejected.

Signed quantities provide a direct representation of inventory effect and simplify balance calculation.

### 31.6 Allow Zero-Quantity Movements

Rejected.

A zero movement has no inventory effect and creates unnecessary ledger noise.

### 31.7 Let Repositories Post Movements

Rejected.

Business rules and transaction orchestration belong to services.

### 31.8 Introduce a Separate Inventory Transaction Framework

Rejected.

The enterprise transaction infrastructure already provides the required transaction boundary.

---

## 32. Architectural Invariants

The following invariants are established:

1. `StockMovement` is owned by the Catering inventory domain.
2. StockMovement is the historical inventory ledger.
3. StockBalance is the current-state quantity representation.
4. Movement quantities are signed.
5. Movement quantity uses `Numeric(18,3)`.
6. Zero movement quantity is invalid.
7. `RECEIPT` quantities are positive.
8. `ISSUE` quantities are negative.
9. `ADJUSTMENT` quantities may be positive or negative.
10. `OPENING_BALANCE` quantities may be signed.
11. `TRANSFER` is reserved for transfer orchestration.
12. DRAFT movements do not affect StockBalance.
13. POSTED movements affect StockBalance.
14. Posted movements are immutable.
15. Posted movement corrections use compensating movements.
16. Posted movement and balance mutation occur atomically.
17. Resulting StockBalance quantity must not be negative.
18. A positive movement may create a missing balance.
19. A negative movement cannot create a missing balance.
20. StockMovement does not own current quantity.
21. StockMovement does not own transfer orchestration.
22. Services own movement business rules and transaction coordination.
23. Repositories remain persistence-oriented.
24. Enterprise transaction infrastructure remains authoritative.
25. Enterprise security and governance infrastructure remains authoritative.
26. No parallel inventory ledger, transaction, audit, or reporting framework is introduced.

---

## 33. Implementation Alignment

The architectural decision is aligned with the existing inventory implementation:

* `StockMovement` exists within the Catering inventory model boundary.
* Movement types include `OPENING_BALANCE`, `RECEIPT`, `ISSUE`, `ADJUSTMENT`, and `TRANSFER`.
* Quantity is signed and uses `Numeric(18,3)`.
* Zero quantity is rejected.
* Receipt and issue sign rules are enforced by the inventory service.
* Transfer posting is reserved for StockTransfer orchestration.
* DRAFT movements do not change current inventory.
* POSTED movements update StockBalance.
* Resulting balances cannot become negative.
* Positive effects can create a missing balance.
* Posted movement state is preserved as historical inventory data.
* Movement posting uses the established transaction manager.
* Repository and service responsibilities follow ADR-004 and ADR-005.

No parallel movement-ledger architecture is required.

---

## 34. Scope Boundaries

This ADR does not establish architecture for:

* StockTransfer orchestration in detail;
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
* batch or lot tracking;
* serial-number tracking;
* expiry management;
* unit-of-measure conversion;
* automated replenishment;
* demand forecasting;
* advanced warehouse operations;
* advanced concurrency control;
* inventory reporting implementation;
* cross-module distributed transactions.

These capabilities require separate architectural decisions if and when they become necessary.

---

## 35. Consequences

### Positive consequences

* Inventory history is preserved.
* Current state remains separate from historical events.
* Inventory effects have explicit semantic types.
* Signed quantities make balance effects clear.
* Draft operations cannot accidentally affect current inventory.
* Posted operations provide durable historical traceability.
* Incorrect posted operations can be corrected without destroying history.
* Movement and balance changes can remain transactionally consistent.
* Existing enterprise repository, transaction, security, governance, and reporting infrastructure is reused.
* Historical inventory reporting becomes straightforward.

### Trade-offs

* Movement records must remain consistent with balances.
* Posting requires coordinated movement and balance operations.
* Immutable history requires compensating corrections rather than simple edits.
* Future concurrency requirements may require additional architecture.
* Reconciliation requires consideration of both ledger and current-state data.

These trade-offs are accepted because historical integrity and operational clarity are essential properties of an inventory system.

---

## 36. Decision Summary

The CDCS-EMP Catering inventory architecture adopts `StockMovement` as the authoritative historical inventory ledger.

The resulting relationship is:

                    ┌────────────────────┐
                    │    StockMovement   │
                    │ Historical ledger   │
                    └─────────┬──────────┘
                              │
                        posted effect
                              │
                              ▼
                    ┌────────────────────┐
                    │    StockBalance    │
                    │   Current state    │
                    └────────────────────┘
                              ▲
                              │
                    ┌─────────┴──────────┐
                    │                    │
               StockItem          InventoryLocation

The fundamental architectural rule is:

> **StockMovement records how inventory changed; StockBalance records how much inventory currently exists.**

Movement history is append-oriented and posted movements are immutable. Corrections occur through compensating movements. Posting and balance mutation are coordinated atomically through the established enterprise transaction boundary.

This provides a durable inventory history while preserving efficient current-state operations.

---

## 37. Approval

**Status:** Planned for documentation

This ADR becomes **Approved — Retrospective** after the corresponding roadmap reconciliation and final Group 11 checkpoint are completed.


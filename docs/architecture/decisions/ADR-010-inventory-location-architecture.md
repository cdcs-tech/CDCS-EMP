
# ADR-010: Inventory Location Architecture

**Status:** Approved — Retrospective
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory location ownership, structure, lifecycle, uniqueness, and relationship to inventory balances

**Related ADRs:**

* ADR-001 — Phase 2 Business Module Architecture & Strategy
* ADR-004 — Catering Repository Architecture
* ADR-005 — Catering Service Architecture
* ADR-006 — Catering Security & Governance Integration
* ADR-008 — Catering Inventory Domain Boundary
* ADR-009 — Inventory Stock Item Architecture

---

## 1. Context

The Catering inventory domain requires a defined representation of the physical or logical locations at which stock is held.

Inventory quantities cannot be represented solely at the StockItem level because the same stocked product may exist in multiple locations.

The inventory domain therefore requires a dedicated **`InventoryLocation`** entity that provides the location dimension for StockBalance.

The initial SSRC-IBMS inventory requirements do not justify a full warehouse-management hierarchy. Introducing warehouse zones, bins, shelves, sub-locations, or other hierarchical structures at this stage would add complexity without a demonstrated business requirement.

The location architecture must therefore provide a simple, extensible location model while preserving a clear boundary between:

* product master data;
* inventory participation;
* inventory locations;
* current stock balances; and
* inventory transaction history.

---

## 2. Decision

The Catering inventory domain will use a dedicated **`InventoryLocation`** entity to represent a location at which inventory may be held.

The initial location model is intentionally **flat**.

An InventoryLocation represents one inventory location and does not contain a parent-child hierarchy.

The conceptual relationship is:

```text
StockItem ───────────────┐
                         │
                         ▼
                    StockBalance
                         ▲
                         │
InventoryLocation ──────┘
```

A StockBalance represents the current quantity of one StockItem at one InventoryLocation.

---

## 3. Ownership

`InventoryLocation` is owned by the Catering module's inventory domain.

The Catering module owns:

* InventoryLocation model definition;
* InventoryLocation repository;
* InventoryLocation service;
* location validation rules;
* location lifecycle;
* inventory-specific location configuration.

The enterprise platform remains responsible for shared infrastructure, including:

* ORM/base model infrastructure;
* database session and transaction management;
* repository infrastructure;
* query, filtering, sorting and pagination;
* validation infrastructure;
* security and authorization;
* audit and governance;
* module discovery and lifecycle.

This follows the bounded business-module architecture established by ADR-001 and the inventory boundary established by ADR-008.

---

## 4. Location Identity

Each InventoryLocation has a stable business identity consisting of:

* `code`;
* `name`.

The location code is the unique business identifier used for operational reference.

The code must be unique within the inventory location domain.

The location name provides the human-readable description used by users and application interfaces.

A location may additionally contain an optional `description` field for operational context.

---

## 5. Initial Data Model

The initial InventoryLocation model consists of:

| Field         | Purpose                                                                     |
| ------------- | --------------------------------------------------------------------------- |
| `code`        | Required unique location identifier                                         |
| `name`        | Required human-readable location name                                       |
| `description` | Optional descriptive information                                            |
| `is_active`   | Indicates whether the location is available for active inventory operations |

The model uses the existing enterprise `BaseModel` and applicable shared model mixins.

No parallel entity base or inventory-specific ORM framework is introduced.

---

## 6. Flat Location Model

The initial inventory architecture deliberately uses a flat location model.

An InventoryLocation does **not** initially contain:

* `parent_id`;
* warehouse hierarchy;
* zone hierarchy;
* aisle hierarchy;
* shelf hierarchy;
* bin hierarchy;
* nested location trees.

The initial conceptual structure is:

```text
Inventory
├── Main Store
├── Kitchen Store
├── Event Store
└── Other Operational Store
```

Each location is an independent inventory location.

This structure is sufficient for the current Catering inventory requirements while leaving room for a future architectural decision if hierarchical warehouse management becomes necessary.

---

## 7. Relationship to StockBalance

InventoryLocation participates in the StockBalance model.

The relationship is:

**InventoryLocation 1 → many StockBalance**

A StockBalance associates:

* one StockItem;
* one InventoryLocation;
* one current quantity.

The combination of:

**`stock_item_id + location_id`**

must uniquely identify one StockBalance.

This means the same StockItem can have independent quantities at multiple locations.

For example:

```text
StockItem: Rice 25kg
    │
    ├── Main Store   → 120.000
    ├── Kitchen Store → 35.000
    └── Event Store   → 20.000
```

The quantities belong to StockBalance, not InventoryLocation.

---

## 8. Location Does Not Store Stock Quantity

InventoryLocation does not store aggregate or current stock quantities.

It must not contain fields such as:

* `current_quantity`;
* `total_quantity`;
* `stock_value`;
* `item_count`.

Current quantity is represented by StockBalance.

This preserves normalization and allows each StockItem to be independently tracked at each location.

---

## 9. Location Does Not Own Stock Movements

InventoryLocation does not own the inventory movement ledger.

StockMovement records identify the relevant location for inventory effects, while the movement ledger remains responsible for historical inventory changes.

InventoryLocation therefore does not contain:

* movement history;
* receipts;
* issues;
* adjustments;
* opening balances;
* transfer transactions.

The location provides the contextual dimension for those operations.

---

## 10. Location and Transfers

Inventory transfers may involve two InventoryLocation records:

* source location;
* destination location.

The StockTransfer domain owns the transfer transaction.

InventoryLocation does not own transfer orchestration.

A transfer therefore follows the conceptual relationship:

```text
Source InventoryLocation
          │
          ▼
    StockTransfer
          │
          ▼
Destination InventoryLocation
```

The transfer service remains responsible for validating the source and destination locations and coordinating the resulting stock effects.

---

## 11. Lifecycle

InventoryLocation supports an active/inactive lifecycle through `is_active`.

An inactive location must not be treated as an available destination for new inventory operations unless explicitly permitted by a future business rule.

Deactivation does not destructively remove historical inventory information.

Existing:

* StockBalance records;
* StockMovement records;
* StockTransfer records; and
* enterprise audit records

must remain historically preserved.

The existing enterprise lifecycle and soft-delete conventions remain authoritative.

---

## 12. Location Validation

The InventoryLocation service owns business validation associated with location operations.

At minimum, service-level validation should ensure:

* code is present;
* name is present;
* code uniqueness is respected;
* location lifecycle rules are respected;
* active/inactive state is applied consistently.

The database provides structural enforcement for persistence invariants, particularly unique location codes.

Database constraints do not replace service-level business validation.

---

## 13. Repository and Service Boundary

InventoryLocation persistence is accessed through the Catering inventory repository boundary.

The InventoryLocation repository remains persistence-oriented.

The InventoryLocation service owns:

* business validation;
* lifecycle rules;
* operational eligibility;
* coordination with other inventory entities where required;
* transaction coordination through the enterprise TransactionManager.

Repositories do not own:

* business rules;
* authorization;
* transaction lifecycle;
* inventory orchestration.

This follows ADR-004 and ADR-005.

---

## 14. Query and Data Access

InventoryLocation repositories reuse the enterprise data infrastructure.

Location queries should use the established:

* `QueryOptions`;
* filtering;
* sorting;
* pagination;
* repository abstractions.

The initial implementation does not require a separate location query framework.

Meaningful domain-specific lookups may be added where justified by actual inventory use cases.

---

## 15. Authorization and Governance

InventoryLocation operations integrate with the enterprise security and governance architecture established by ADR-006.

Catering owns the business capability permissions required for inventory-location management.

The enterprise platform remains authoritative for:

* authentication;
* authorization evaluation;
* security policy;
* audit;
* governance;
* compliance infrastructure.

InventoryLocation introduces no separate security or authorization mechanism.

---

## 16. Relationship to Other Inventory Entities

The intended domain relationships are:

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
   ▲
   │ many : 1
   │
InventoryLocation

StockMovement ── references StockItem + InventoryLocation
StockTransfer ── references source + destination InventoryLocation
```

This establishes InventoryLocation as a location dimension rather than a container for inventory state or transaction history.

---

## 17. Database Constraints

The database should enforce the structural invariants of InventoryLocation.

At minimum:

1. `code` is required.
2. `code` is unique.
3. `name` is required.
4. `description` is nullable.
5. `is_active` represents the location lifecycle state.

Foreign-key relationships from StockBalance and StockMovement provide referential integrity where applicable.

The exact migration implementation must follow the existing SQL Server and enterprise migration conventions.

---

## 18. Deliberate Exclusions

The initial InventoryLocation architecture does not include:

* warehouse hierarchy;
* parent-child location relationships;
* zones;
* aisles;
* shelves;
* bins;
* warehouse management functionality;
* location capacity management;
* temperature zones;
* hazardous-material classifications;
* location-specific valuation;
* location-specific accounting;
* location-specific procurement;
* location-specific supplier ownership;
* automated replenishment;
* route optimization;
* barcode infrastructure;
* RFID infrastructure;
* advanced warehouse operations.

These capabilities require separate architectural decisions if future requirements justify them.

---

## 19. Consequences

### Positive consequences

* Inventory quantities can be independently maintained by location.
* Multiple stores can participate in inventory without duplicating StockItem records.
* Location identity is simple and operationally clear.
* The initial model avoids premature warehouse-management complexity.
* StockBalance remains the authoritative current-state representation.
* StockMovement remains the authoritative historical inventory ledger.
* StockTransfer remains responsible for transfer orchestration.
* Existing enterprise repository, service, transaction, security and governance infrastructure is reused.
* The flat model can later be extended through a deliberate architectural decision if required.

### Trade-offs

* Complex warehouse layouts cannot be represented natively in the initial model.
* Users must treat each operational location as an independent location.
* Future hierarchical warehouse requirements may require a separate architecture and migration.
* Location-level aggregate information must be derived from StockBalance rather than stored directly.

These trade-offs are intentional and appropriate for the current Phase 2 scope.

---

## 20. Implementation Alignment

The implementation must maintain:

* InventoryLocation ownership within Catering inventory;
* unique location codes;
* required location names;
* optional descriptions;
* active/inactive lifecycle;
* flat location structure;
* StockBalance as the quantity owner;
* StockMovement as the historical ledger;
* StockTransfer as the transfer transaction owner;
* enterprise BaseModel and shared infrastructure;
* service-owned business validation;
* repository-owned persistence access.

---

## 21. Non-Goals

This ADR does not define:

* StockItem architecture;
* StockBalance architecture;
* StockMovement ledger architecture;
* StockTransfer architecture;
* purchasing;
* financial integration;
* warehouse-management architecture;
* replenishment automation;
* inventory valuation;
* reporting architecture.

Those concerns remain subject to their respective architectural decisions.

---

## 22. Decision Summary

The Catering inventory domain will use `InventoryLocation` as a simple, flat representation of a location where stock may be held.

The key invariant is:

> **InventoryLocation identifies where stock may be held; StockBalance owns the current quantity at that location; StockMovement owns historical inventory effects; StockTransfer owns movement between locations.**

This provides the location dimension required by the inventory domain while deliberately avoiding premature warehouse-management complexity.

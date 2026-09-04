
# ADR-009: Inventory Stock Item Architecture

**Status:** Approved — Retrospective
**Decision Date:** 4 September 2026
**Documentation Date:** 5 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — First Business Modules
**Module:** Catering
**Scope:** Inventory Stock Item architecture, ownership, relationship to Catering Product, inventory configuration, and separation from stock state

**Related ADRs:**

* ADR-001 — Phase 2 Business Module Architecture & Strategy
* ADR-002 — Catering Model Registration Boundary
* ADR-003 — Catering Relationships & Database Constraints
* ADR-005 — Catering Service Architecture
* ADR-008 — Catering Inventory Domain Boundary

---

## 1. Context

The Catering module requires inventory participation for products that are physically stocked and managed through the inventory domain.

The existing Catering `Product` model is the authoritative product master. Inventory therefore must not introduce a second product registry or duplicate product-master information.

A product may participate in inventory, but not every Catering product is necessarily stocked. Inventory requires its own domain representation to hold inventory-specific configuration and lifecycle state without taking ownership of the underlying product master.

The inventory architecture also requires a clear separation between:

* product identity and master data;
* inventory participation and configuration;
* current stock quantities;
* stock movement history;
* stock transfers; and
* derived inventory status.

Without this separation, the StockItem model could become an inappropriate container for current quantities, movement history, purchasing information, or duplicated product attributes.

---

## 2. Decision

The Catering inventory domain will use a dedicated **`StockItem`** entity to represent the participation of an existing Catering `Product` in inventory.

`StockItem` is an inventory-domain configuration entity, not a replacement for `Product`.

The architectural relationship is:

```text
Catering Product
       │
       │ 1 : 0..1
       ▼
   StockItem
       │
       ├── inventory configuration
       │
       └── participates in StockBalance
```

A Catering Product may therefore exist without a StockItem, while each StockItem must reference exactly one existing Catering Product.

---

## 3. Ownership

`StockItem` is owned by the Catering module's inventory domain.

The Catering module owns:

* StockItem model definition;
* StockItem repository;
* StockItem service;
* StockItem validation rules;
* StockItem lifecycle;
* inventory-specific configuration associated with the stock item.

The enterprise platform remains responsible for the underlying shared infrastructure, including:

* ORM/base model infrastructure;
* database session and transaction management;
* repository infrastructure;
* query, filtering, sorting and pagination infrastructure;
* validation infrastructure;
* security and authorization;
* audit and governance;
* module discovery and lifecycle.

This follows the bounded-module architecture established by ADR-001 and the inventory boundary established by ADR-008.

---

## 4. Relationship to Catering Product

`StockItem.product_id` is a required foreign key to the authoritative Catering `Product`.

The relationship is:

**Product 1 → 0..1 StockItem**

The `product_id` value must therefore be unique within StockItem.

This ensures:

* a product cannot have multiple StockItem records;
* inventory does not duplicate the product registry;
* product identity remains owned by Catering master data;
* inventory configuration remains independently manageable.

The StockItem entity must not copy authoritative Product fields such as:

* product code;
* product name;
* category;
* product description; or
* other product-master attributes.

Those values remain authoritative on `Product`.

---

## 5. StockItem Responsibilities

StockItem represents whether and how a Catering Product participates in inventory.

The initial StockItem responsibility includes:

* linking an inventory item to a Product;
* inventory activation state;
* minimum stock threshold;
* reorder threshold;
* inventory-specific configuration required by the current inventory domain.

The initial model consists of:

| Field           | Purpose                                                            |
| --------------- | ------------------------------------------------------------------ |
| `product_id`    | Required reference to the authoritative Catering Product           |
| `minimum_level` | Optional minimum stock threshold                                   |
| `reorder_level` | Optional reorder threshold                                         |
| `is_active`     | Indicates whether the StockItem is active for inventory operations |

Threshold quantities use the platform's established decimal quantity representation:

**`Numeric(18,3)`**

This provides sufficient precision for the current inventory domain while avoiding premature specialization for particular units or measurement systems.

---

## 6. StockItem Does Not Store Current Quantity

Current inventory quantity is explicitly **not** stored on StockItem.

StockItem represents inventory configuration and participation.

Current quantity belongs to:

**`StockBalance`**

The conceptual separation is:

```text
StockItem
  ├── Product reference
  ├── Minimum level
  ├── Reorder level
  └── Active state

StockBalance
  └── Current quantity by StockItem and Location
```

This prevents StockItem from becoming a denormalized inventory-state container.

A product may therefore have one StockItem while having multiple StockBalance records across inventory locations.

---

## 7. StockItem Does Not Store Inventory Status

Inventory status such as:

* below minimum;
* below reorder level;
* adequately stocked;

is derived from the relationship between configured thresholds and current StockBalance quantities.

Such status is therefore not persisted as an authoritative StockItem field.

This avoids duplicated and potentially stale state.

The service/application layer is responsible for evaluating the applicable inventory status when required.

---

## 8. StockItem Does Not Own Movement History

StockItem does not contain stock movement history or transaction quantities.

Movement history belongs to the inventory movement ledger represented by `StockMovement`.

StockItem therefore does not directly store:

* receipts;
* issues;
* adjustments;
* opening balances;
* transfers;
* posted quantities;
* movement timestamps; or
* movement references.

The movement ledger remains the authoritative historical record of inventory changes.

---

## 9. Database Constraints

The database enforces the structural invariants of StockItem.

At minimum:

1. `product_id` is required.
2. `product_id` references `Product.id`.
3. `product_id` is unique.
4. `minimum_level` uses `Numeric(18,3)` when supplied.
5. `reorder_level` uses `Numeric(18,3)` when supplied.
6. `is_active` represents the StockItem lifecycle state.

Database constraints protect persistence integrity.

They do not replace service-level business validation.

Business rules governing whether a StockItem may be created, activated, deactivated, or used in a particular inventory operation remain service responsibilities.

---

## 10. Threshold Semantics

`minimum_level` and `reorder_level` are inventory configuration values.

They do not represent current quantity.

The architecture therefore distinguishes:

```text
Configured thresholds
        │
        ├── minimum_level
        └── reorder_level

Current inventory state
        │
        └── StockBalance.quantity
```

Threshold semantics must be validated by the inventory service layer.

The initial architecture does not impose additional procurement or replenishment automation based solely on these fields.

---

## 11. Lifecycle

StockItem supports an active/inactive lifecycle through `is_active`.

Deactivation does not delete historical inventory information.

In particular, deactivating a StockItem must not destructively remove:

* StockBalance records;
* StockMovement records;
* StockTransfer records; or
* enterprise audit records.

The existing enterprise soft-delete/lifecycle conventions remain authoritative where applicable.

Destructive deletion of inventory transaction history is not part of this architecture.

---

## 12. Service and Repository Boundary

StockItem persistence is accessed through Catering's inventory repository boundary.

The StockItem service owns:

* business validation;
* lifecycle rules;
* coordination with Product;
* coordination with StockBalance and other inventory entities where required;
* authorization-aware business operations;
* transaction coordination through the enterprise TransactionManager.

The StockItem repository remains persistence-oriented.

It does not own:

* business rules;
* transaction lifecycle;
* authorization decisions;
* inventory orchestration.

This follows ADR-004 and ADR-005.

---

## 13. Authorization and Governance

StockItem operations integrate with the enterprise security and governance architecture established by ADR-006.

Catering owns the business capability permissions required for inventory operations.

The enterprise platform remains authoritative for:

* authentication;
* authorization evaluation;
* security policy;
* audit;
* governance;
* compliance infrastructure.

StockItem does not introduce a separate security or authorization mechanism.

---

## 14. Query and Data Access

StockItem repositories reuse the enterprise data infrastructure.

Queries should use the established:

* `QueryOptions`;
* filtering;
* sorting;
* pagination;
* repository abstractions.

No parallel inventory-specific query framework is introduced.

Inventory-specific lookup methods may be added to the Catering repository where they represent meaningful domain access patterns.

---

## 15. Deliberate Exclusions

The initial StockItem architecture does not include:

* a duplicate Product entity;
* a duplicate product-master registry;
* current quantity fields;
* persisted inventory status;
* movement history fields;
* supplier ownership;
* purchasing fields;
* purchase-order relationships;
* invoice relationships;
* expense relationships;
* sales relationships;
* customer relationships;
* unit-of-measure master-data ownership;
* warehouse hierarchy;
* automated replenishment;
* demand forecasting;
* batch/lot tracking;
* serial-number tracking;
* expiry management;
* valuation/accounting fields;
* advanced warehouse management capabilities.

These capabilities may be considered through separate architectural decisions if future requirements justify them.

---

## 16. Consequences

### Positive consequences

* Product remains the single authoritative product master.
* Inventory participation is modeled explicitly.
* Product master data is not duplicated.
* Current stock is separated from inventory configuration.
* Inventory thresholds remain independently configurable.
* Stock status can be derived rather than persisted.
* Movement history remains in the dedicated ledger.
* The architecture supports multiple locations through StockBalance.
* Existing enterprise repository, service, transaction, security and governance infrastructure is reused.
* Future inventory capabilities can be added without overloading StockItem.

### Trade-offs

* Inventory operations require navigation between Product, StockItem and StockBalance.
* Some inventory views require joins or coordinated service queries.
* Derived stock status requires current balance evaluation.
* Future advanced inventory capabilities may require additional domain entities and architectural decisions.

These trade-offs are intentional and preserve clear domain boundaries.

---

## 17. Implementation Alignment

The current implementation aligns StockItem with this decision through the Catering inventory model boundary.

The implementation must maintain:

* `StockItem.product_id` as the authoritative Product relationship;
* unique Product-to-StockItem participation;
* threshold fields as inventory configuration;
* no current quantity on StockItem;
* no movement ledger embedded in StockItem;
* reuse of enterprise BaseModel and mixins;
* reuse of enterprise repository and service infrastructure;
* service-owned business rules and transaction coordination.

---

## 18. Non-Goals

This ADR does not define:

* StockBalance architecture;
* StockMovement ledger architecture;
* StockTransfer architecture;
* inventory posting transaction semantics;
* purchasing integration;
* financial integration;
* reporting architecture;
* replenishment automation;
* warehouse-management architecture.

Those concerns remain subject to their respective architectural decisions and implementation stages.

---

## 19. Decision Summary

The Catering inventory domain will use `StockItem` as the inventory-specific configuration and participation entity for an existing Catering `Product`.

The key invariant is:

> **Product owns product identity and master data; StockItem owns inventory participation and configuration; StockBalance owns current quantity; StockMovement owns inventory history.**

This separation is the authoritative architectural boundary for StockItem within the Phase 2 Catering inventory implementation.

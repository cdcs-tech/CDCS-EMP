# CDCS-EMP — Phase 2 Business Modules

# Authoritative Architecture & Implementation Roadmap

**Document Type:** Authoritative Phase Roadmap
**Status:** Approved / Active
**Version:** 1.0
**Phase:** Phase 2 — Business Modules
**Current Module:** Catering
**Authoritative Location:** `docs/architecture/decisions/`
**Last Updated:** 30 August 2026

---

## 1. Purpose

This document establishes the authoritative roadmap for **Phase 2 of the CDCS Enterprise Management Platform (CDCS-EMP)**.

It consolidates the previously developed Phase 2 planning, architecture, persistence design, implementation sequencing, and verification decisions into a single source of truth.

Where earlier planning notes, duplicated roadmap fragments, or chat discussions conflict with this document, this document takes precedence unless a subsequent approved Architecture Decision Record (ADR) explicitly supersedes a decision.

---

# 2. Phase 2 Objective

Phase 2 introduces the first real business modules into CDCS-EMP.

The objective is to demonstrate that the existing CDCS-EMP enterprise platform foundation can support complete, independently bounded business capabilities without creating separate applications or duplicating platform infrastructure.

The first Phase 2 pilot business module is:

**Catering**

The Catering module is being implemented as the first business-domain implementation against the established CDCS-EMP platform architecture.

---

# 3. Phase 2 Architectural Principles

All Phase 2 business modules shall:

1. Consume the existing CDCS-EMP platform foundation.
2. Remain bounded within their own business-domain package.
3. Use the established module lifecycle and discovery framework.
4. Use the established persistence architecture.
5. Use the established security and governance framework.
6. Avoid duplicating platform infrastructure.
7. Avoid introducing unnecessary dependencies between business modules.
8. Preserve organization-level data isolation.
9. Preserve enterprise auditability.
10. Be implemented incrementally with focused verification gates.

A business module must not become a second independent application inside CDCS-EMP.

---

# 4. Catering Module Boundary

The initial Catering module covers the operational management of catering activities, including:

* Customers
* Catering services / engagements
* Menus
* Menu items
* Products and product categories
* Suppliers
* Inventory items
* Food stores
* Stock movements
* Purchases
* Purchase lines
* Catering expenses
* Invoices
* Invoice lines
* Catering payments

The module deliberately does **not** initially implement:

* Full accounting ledgers
* General Finance functionality
* Payroll
* Staffing management
* Production planning
* Recipe management
* Asset management
* Enterprise-wide Procurement
* Enterprise-wide Inventory
* Other business modules

Those capabilities may be introduced later as independent platform or business capabilities.

---

# 5. Phase 2.1 — Catering Implementation Roadmap

## 5.1 Phase 2.1.1 — Catering Module Selection & Scope

**Status:** Complete

Established Catering as the first Phase 2 business module and defined its initial operational scope.

---

## 5.2 Phase 2.1.2 — Catering Domain Boundaries

**Status:** Complete

Established the Catering domain boundary and its relationship with the wider CDCS-EMP platform.

---

## 5.3 Phase 2.1.3 — Domain Entities & Relationships

**Status:** Complete

Established the initial Catering domain entities and their relationships.

The domain model was subsequently refined through the persistence-design stage and the approved master-data foundation.

---

## 5.4 Phase 2.1.4 — Data Model & Persistence Design

**Status:** Complete — Approved for implementation

The persistence architecture is based entirely on the existing CDCS-EMP persistence stack.

### Persistence flow

```text
Catering Domain
      │
      ▼
SQLAlchemy Models
      │
      ▼
Existing BaseModel + Mixins
      │
      ▼
Existing SQLAlchemy db Extension
      │
      ▼
Existing Repository / Data Framework
      │
      ▼
SQL Server
```

The Catering module shall not introduce:

* A second database abstraction
* A Catering-specific ORM base
* A second transaction mechanism
* Module-specific generic CRUD infrastructure
* A separate tenant model

---

# 6. Common Persistence Contract

Persistent Catering entities shall use the existing CDCS-EMP model foundation.

Where applicable, entities inherit:

```text
BaseModel
TimestampMixin
AuditMixin
SoftDeleteMixin
```

## BaseModel

Provides:

* `id` — integer primary key
* `guid` — SQL Server `UNIQUEIDENTIFIER`

## TimestampMixin

Provides:

* `created_at`
* `updated_at`

## AuditMixin

Provides:

* `created_by`
* `updated_by`

## SoftDeleteMixin

Provides:

* `is_deleted`
* `deleted_at`

The Catering module shall not redefine these platform-wide concerns.

---

# 7. Organization Ownership

Organizational Catering records shall contain:

```text
organization_id
```

with:

```text
FOREIGN KEY → organizations.id
nullable = False
```

where the record represents organizationally owned data.

The tenant boundary is established through the existing:

```text
Tenant
  │
  └── Organization
        │
        └── Catering Data
```

The Catering module shall **not add `tenant_id` to every table** unless a future platform-level requirement demonstrates that this is necessary.

---

# 8. Initial Catering Persistence Surface

The approved initial persistence boundary consists of the following tables.

| #  | Table               | Purpose                      |
| -- | ------------------- | ---------------------------- |
| 1  | `customers`         | Catering customers           |
| 2  | `catering_services` | Catering engagements/events  |
| 3  | `menus`             | Menu definitions             |
| 4  | `menu_items`        | Menu offerings               |
| 5  | `suppliers`         | Suppliers                    |
| 6  | `stock_items`       | Inventory master             |
| 7  | `food_stores`       | Storage locations            |
| 8  | `stock_movements`   | Inventory transaction ledger |
| 9  | `purchases`         | Procurement headers          |
| 10 | `purchase_lines`    | Procurement details          |
| 11 | `catering_expenses` | Catering expenses            |
| 12 | `invoices`          | Customer billing             |
| 13 | `invoice_lines`     | Billing details              |
| 14 | `catering_payments` | Customer payments            |

---

# 9. Core Data Model Rules

## 9.1 Business identifiers

Organizational business identifiers shall use composite uniqueness where appropriate.

Examples:

```text
UNIQUE(organization_id, customer_code)
UNIQUE(organization_id, service_number)
UNIQUE(organization_id, supplier_code)
UNIQUE(organization_id, item_code)
UNIQUE(organization_id, invoice_number)
UNIQUE(organization_id, purchase_number)
UNIQUE(organization_id, payment_number)
```

This permits different organizations to use the same local business identifier without violating organizational isolation.

---

## 9.2 Monetary precision

All financial values shall use SQLAlchemy `Numeric` / SQL Server `DECIMAL`.

Default monetary precision:

```text
Numeric(18, 2)
```

Floating-point types shall not be used for monetary values.

---

## 9.3 Inventory precision

Inventory quantities shall use:

```text
Numeric(18, 3)
```

This supports fractional quantities such as:

```text
1.500 kg
0.250 kg
2.750 litres
```

Greater precision may be considered later if required by a platform-wide inventory capability.

---

# 10. Stock Movement Design

`stock_movements` is the inventory transaction ledger for the initial Catering implementation.

The stored movement quantity represents a **positive quantity**.

Movement direction is determined by the movement type.

Examples:

| Movement Type  | Direction      |
| -------------- | -------------- |
| `PURCHASE`     | +              |
| `RECEIPT`      | +              |
| `RETURN`       | +              |
| `ISSUE`        | −              |
| `WASTAGE`      | −              |
| `TRANSFER_OUT` | −              |
| `TRANSFER_IN`  | +              |
| `ADJUSTMENT`   | Domain-defined |

The domain/service layer shall control movement direction rather than allowing arbitrary positive/negative quantities from user input.

---

# 11. Invoice Design

An invoice is a billable financial document.

`invoice_lines` intentionally does **not** require a `menu_item_id`.

An invoice line represents a billable item and may therefore describe:

* A menu item
* A service
* A custom charge
* Another billable item

This preserves flexibility while avoiding unnecessary coupling between billing and menu definitions.

---

# 12. Payment Design

`catering_payments` supports multiple payments against a single invoice.

Each payment has its own:

* Payment number
* Payment date
* Amount
* Payment method
* Optional reference
* Optional notes

Payment numbers are unique within an organization.

---

# 13. Foreign-Key Strategy

The principal relationships are:

```text
Organization
│
├── Customers
│     └── Catering Services
│
├── Menus
│     └── Menu Items
│
├── Suppliers
│     └── Purchases
│           └── Purchase Lines
│                 └── Stock Items
│
├── Food Stores
│     └── Stock Movements
│
├── Stock Items
│     └── Stock Movements
│
├── Catering Services
│     └── Catering Expenses
│
└── Invoices
      ├── Invoice Lines
      └── Catering Payments
```

Individual foreign keys shall be enforced by the database.

Cross-organization consistency shall be enforced through domain/application services and tests.

The database shall not introduce unnecessarily complex composite foreign keys solely to enforce organization consistency between related entities.

---

# 14. Delete Strategy

Catering business records are auditable business data.

Therefore:

* Organization deletion shall not physically cascade into Catering transactional data.
* Soft deletion shall be preferred for business entities where appropriate.
* Blanket `ON DELETE CASCADE` shall not be used across transactional Catering tables.
* Aggregate-dependent records may have controlled lifecycle handling.
* Physical deletion of transactional data shall be treated as an exceptional operation subject to enterprise governance.

---

# 15. Indexing Strategy

Indexes shall support actual organizational, relational, operational, and reporting queries.

## Organizational indexes

`organization_id` shall be indexed on organization-owned tables.

## Foreign-key indexes

Likely indexed foreign keys include:

* `customer_id`
* `supplier_id`
* `catering_service_id`
* `menu_id`
* `purchase_id`
* `stock_item_id`
* `food_store_id`
* `invoice_id`

## Business identifier indexes

Composite unique indexes shall support organizational identifiers.

## Operational indexes

Likely operational indexes include:

* `service_date`
* `purchase_date`
* `expense_date`
* `invoice_date`
* `payment_date`
* `movement_date`
* `status`

Indexes shall not be added indiscriminately to every column.

---

# 16. Audit User Foreign Keys

The existing `AuditMixin` defines:

```text
created_by
updated_by
```

as integer fields without foreign-key constraints.

Catering shall follow this existing platform contract.

The Catering implementation shall **not modify `AuditMixin`** merely to introduce user foreign keys.

Any future formalization of audit-user foreign keys shall be implemented as a platform-wide enhancement.

---

# 17. Module Package Architecture

The Catering module is a proper Phase 2 business module.

Its package resides under:

```text
app/modules/catering/
```

The module is discovered through the existing CDCS-EMP module discovery framework.

The architectural flow is:

```text
app.modules
      │
      ▼
ModuleDiscovery
      │
      ▼
catering.manifest
      │
      ▼
MODULE_MANIFEST
      │
      ▼
CateringModule
      │
      ▼
ModuleLoader
      │
      ▼
ModuleManager
      │
      ▼
CateringModule.initialize()
```

No Catering-specific startup modification is required in `app/__init__.py`.

---

# 18. Catering Module Foundation

The initial package foundation consists of:

```text
app/modules/catering/
├── __init__.py
├── manifest.py
├── module.py
└── models/
    └── __init__.py
```

The model package consumes the existing platform model foundation:

```text
BaseModel
TimestampMixin
AuditMixin
SoftDeleteMixin
```

No Catering-specific ORM base or database abstraction shall be introduced.

---

# 19. Phase 2.1.5 — Catering Module Package & Model Implementation

## 19.1 Phase 2.1.5.1 — Catering Module Package & Manifest Foundation

**Status: COMPLETE**

Delivered:

* Catering package
* `CateringModule`
* `ModuleMetadata`
* Catering discovery manifest
* Catering public API
* Focused architecture tests
* Automatic discovery integration

Verification:

* Catering foundation tests: **5 passed**
* Full regression at checkpoint: **1,716 passed**
* No startup modification required

---

## 19.2 Phase 2.1.5.2 — Catering Model Package Foundation

**Status: COMPLETE**

Delivered:

```text
app/modules/catering/models/__init__.py
```

The model package exposes:

* `BaseModel`
* `TimestampMixin`
* `AuditMixin`
* `SoftDeleteMixin`

Verification:

* Model package contents verified
* Shared model foundation imports successfully
* `BaseModel.__abstract__ == True`
* Catering unit tests: **5 passed**

---

## 19.3 Phase 2.1.5.3 — Core Catering Domain Models

**Status: COMPLETE — COMMITTED — PENDING GIT PUSH**

The first actual Catering domain model implementation has been completed.

The approved master-data foundation consists initially of:

* `ProductCategory`
* `Product`

These models provide the classification and product foundation required for subsequent:

* Inventory
* Purchasing
* Stock
* Sales
* Reporting

capabilities.

The corresponding architectural decision is documented in:

```text
docs/architecture/decisions/ADR-002-catering-model-registration-boundary.md
```

Current repository state:

```text
Phase 2.1.5.3
    COMPLETE
    COMMITTED
    PENDING GIT PUSH
```

---

# 20. Remaining Phase 2.1.5 Roadmap

## 20.1 Phase 2.1.5.4 — Relationships & Database Constraints

**Status: NEXT**

Scope:

* Model relationships
* Foreign keys
* Organizational ownership
* Composite uniqueness
* Check constraints where appropriate
* Relationship validation
* Cross-organization consistency tests
* Aggregate relationship behavior

No unrelated platform changes should be introduced.

---

## 20.2 Phase 2.1.5.5 — Model Registration & Migration

Scope:

* Controlled model registration/import boundary
* Alembic migration
* Catering-owned database tables
* Catering indexes
* Catering constraints
* Migration verification

The original enterprise migration:

```text
d8196139a024_initial_enterprise_schema
```

shall not be modified.

Catering shall be introduced through a new Alembic revision.

Conceptually:

```text
d8196139a024
      │
      ▼
<new Catering revision>
      │
      ▼
future Phase 2 migrations
```

---

## 20.3 Phase 2.1.5.6 — Catering Repositories

Repositories shall consume the existing:

* `BaseRepository`
* `SQLAlchemyRepository`
* Existing Data Framework

No second repository abstraction shall be introduced.

---

## 20.4 Phase 2.1.5.7 — Catering Services

Business services shall implement domain behavior such as:

* Customer operations
* Catering-service operations
* Product/menu operations
* Purchasing
* Inventory movements
* Expense recording
* Invoicing
* Payment processing
* Business-rule validation

Services shall enforce invariants that are intentionally not represented as complex database constraints.

---

## 20.5 Phase 2.1.5.8 — Security & Governance Integration

Catering shall integrate with the existing:

* Authentication
* RBAC
* Permissions
* Authorization
* Security policies
* Audit
* Governance

framework.

No independent Catering security mechanism shall be created.

---

## 20.6 Phase 2.1.5.9 — Module Verification & Baseline

Final verification shall include:

* Focused Catering tests
* Model tests
* Repository tests
* Service tests
* Security tests
* Migration tests
* Module discovery tests
* Full regression suite
* Git status verification
* Clean working-tree checkpoint
* Final Phase 2.1 baseline

---

# 21. Verification Strategy

Implementation shall follow controlled verification gates.

The standard sequence is:

```text
Implement
   │
   ▼
Focused verification
   │
   ▼
Module-level tests
   │
   ▼
Integration verification
   │
   ▼
Full regression
   │
   ▼
Git status
   │
   ▼
Commit
   │
   ▼
Push
   │
   ▼
Checkpoint
```

The full regression suite should not be unnecessarily repeated after every tiny implementation increment.

A full regression is required at meaningful architectural checkpoints.

---

# 22. Explicit Non-Goals

The following shall not be introduced merely for convenience:

* Second ORM base
* Second database extension
* Second transaction manager
* Catering-specific tenant model
* Duplicate repository framework
* Duplicate CRUD framework
* Duplicate audit mechanism
* Duplicate authorization system
* Automatic blanket cascade deletion
* Premature Finance integration
* Premature Procurement integration
* Premature Asset integration
* Premature Payroll integration
* Recipe management
* Production planning
* Full accounting ledger
* Unnecessary cross-module dependencies

---

# 23. Architectural Change Control

This document is the **authoritative Phase 2 roadmap**.

Any material change to:

* Module boundaries
* Persistence architecture
* Domain entities
* Organizational ownership
* Migration strategy
* Module lifecycle integration
* Security architecture
* Repository architecture
* Service architecture

shall be explicitly reviewed before implementation.

Where a change constitutes an architectural decision, it should be documented through an ADR in:

```text
docs/architecture/decisions/
```

The roadmap shall then be updated to reflect the approved decision.

---

# 24. Current Status

As of **30 August 2026**:

```text
Phase 2
│
└── Phase 2.1 — Catering
      │
      ├── 2.1.1 Scope & Selection ................ COMPLETE
      ├── 2.1.2 Domain Boundaries ................ COMPLETE
      ├── 2.1.3 Entities & Relationships ........ COMPLETE
      ├── 2.1.4 Persistence Design ............... COMPLETE
      │
      └── 2.1.5 Module & Model Implementation
            │
            ├── 2.1.5.1 Module Foundation ........ COMPLETE
            ├── 2.1.5.2 Model Foundation ......... COMPLETE
            ├── 2.1.5.3 Core Domain Models ........ COMPLETE*
            ├── 2.1.5.4 Relationships & Constraints PENDING
            ├── 2.1.5.5 Registration & Migration .. PENDING
            ├── 2.1.5.6 Repositories .............. PENDING
            ├── 2.1.5.7 Services .................. PENDING
            ├── 2.1.5.8 Security & Governance ..... PENDING
            └── 2.1.5.9 Verification & Baseline ... PENDING

* Complete and committed; git push pending.
```

---

# 25. Immediate Next Step

The next implementation stage is:

## **Phase 2.1.5.4 — Relationships & Database Constraints**

Before implementation, the existing `ProductCategory` and `Product` models should be inspected against the approved Phase 2.1.4 persistence design.

The stage should establish the actual SQLAlchemy relationship and constraint implementation without prematurely moving into repositories, services, security, or migration work.

---

# 26. Source-of-Truth Statement

**This document is the authoritative roadmap for Phase 2 of CDCS-EMP.**

It consolidates the approved Phase 2 planning and implementation decisions available as of 30 August 2026.

Earlier duplicated roadmap fragments and informal planning notes are superseded where they conflict with this document.

Individual ADRs remain authoritative for the specific architectural decisions they document. This roadmap incorporates those decisions into the overall Phase 2 implementation sequence.

Future architectural changes must be explicitly approved and recorded through the appropriate ADR and reflected in this roadmap.

---

**End of Document**

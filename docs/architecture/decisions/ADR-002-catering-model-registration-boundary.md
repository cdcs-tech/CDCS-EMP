# CDCS-EMP — Phase 2 Project Decision Record

## Phase 2.1.5.3 — Catering Master Data Foundation

**Status:** Approved
**Decision Date:** 29 August 2026
**Module:** Catering
**Phase:** Phase 2 — Business Modules

---

## 1. Decision

The Catering module will establish a focused master-data foundation consisting initially of:

* `ProductCategory`
* `Product`

These models will provide the foundational classification and product structure required for subsequent Catering inventory, purchasing, stock, sales, and reporting capabilities.

---

## 2. Approved Architecture

### 2.1 Model Location

Catering business-domain models will reside within the Catering module:

```text
app/modules/catering/models/
```

They will not be added to the global `app/models/` package unless a future platform-wide requirement justifies doing so.

### 2.2 Persistence Model

Catering models will use the existing SQLAlchemy enterprise model foundation:

* `BaseModel`
* `TimestampMixin`
* `AuditMixin`
* `SoftDeleteMixin`

This ensures consistency with existing CDCS-EMP enterprise models.

### 2.3 Entity Relationship

The initial master-data relationship is:

```text
ProductCategory
       │
       │ 1
       │
       └──────────< Product
                       many
```

A `ProductCategory` may contain multiple `Product` records.

Each `Product` belongs to one `ProductCategory`.

### 2.4 Controlled Values

Where Catering requires controlled values, the implementation will follow the established Python `Enum` convention used by CDCS-EMP.

A database-level `db.Enum` will not be introduced unless a later requirement specifically justifies database-level enum enforcement.

### 2.5 Tenant and Organization Scope

Catering master data must respect the existing enterprise ownership architecture:

```text
Tenant
   │
   └── Organization
          │
          └── Catering business data
```

Catering records must not be implicitly owned by individual users.

The final organization-scoping fields will follow the approved Catering domain model and existing enterprise relationship conventions.

---

## 3. Data Framework Integration

The existing enterprise data framework will be reused.

The following existing abstractions remain the standard infrastructure:

```text
BaseRepository
       ↓
SQLAlchemyRepository

BaseService
       ↓
Repository
```

No Catering-specific repository abstraction will be introduced at this stage.

No Catering-specific service abstraction will be introduced until business rules or orchestration requirements justify one.

The existing transaction boundary remains responsible for commit and rollback behavior.

---

## 4. Domain Entity Decision

The Catering module will not create parallel persistence-independent `BaseEntity` dataclasses for `ProductCategory` and `Product` at this stage.

The existing `BaseEntity` abstraction remains available for future use where a concrete application-service or domain requirement requires persistence-independent representations.

This avoids unnecessary duplication between domain objects and SQLAlchemy models.

---

## 5. Master-Data Framework Decision

A generic enterprise-wide master-data framework will not be introduced during this stage.

The initial implementation will focus on the concrete Catering requirements.

Future reusable abstractions may be introduced only when multiple business modules demonstrate a genuine shared requirement.

---

## 6. Testing Decision

Catering master-data tests will be placed under:

```text
tests/unit/modules/catering/
```

The existing project application/database fixtures will be reused.

Testing will cover:

* model construction
* required fields
* default values
* relationships
* constraints
* persistence behavior
* soft deletion behavior where applicable

No new database-testing framework will be introduced.

---

## 7. Scope Exclusions

The following are intentionally outside the scope of Phase 2.1.5.3:

* Supplier master data
* Customer master data
* Generic Party framework
* Unit-of-measure framework
* Inventory transactions
* Stock movements
* Purchasing workflows
* Sales workflows
* Invoice/receipt processing
* Reporting implementation
* Catering-specific repository infrastructure
* Generic enterprise master-data framework

These may be addressed in later approved phases where justified by the business domain.

---

## 8. Rationale

The selected approach preserves the existing CDCS-EMP architecture while avoiding premature generalization.

The Catering module receives concrete, usable master-data models while continuing to rely on established platform capabilities for:

* persistence
* auditing
* timestamps
* soft deletion
* repositories
* services
* transactions
* testing infrastructure

This keeps the Phase 2 implementation modular and prevents business-specific requirements from unnecessarily expanding the platform core.

---

## 9. Approval

**Decision:** Approved for implementation.

**Next implementation stage:** Final Catering module registration-boundary inspection followed by implementation of `ProductCategory` and `Product`.

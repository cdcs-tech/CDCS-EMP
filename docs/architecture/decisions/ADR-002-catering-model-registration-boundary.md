# CDCS-EMP — ADR-002 — Catering Model Registration Boundary

**Status:** Approved — Retrospective
**Decision Date:** 29 August 2026
**Documentation Date:** 4 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — Business Modules
**Module:** Catering
**Scope:** Catering master-data model registration and ownership boundary
**Supersedes:** None
**Superseded By:** None
**Related ADRs:** ADR-001, ADR-003

---

## 1. Context

The first Phase 2 business module is Catering.

The Catering implementation requires concrete master-data models while preserving the architectural principle established by ADR-001: business modules consume the existing CDCS-EMP enterprise platform rather than introducing parallel platform infrastructure.

The initial Catering master-data requirement is the classification and product foundation required by subsequent inventory, purchasing, stock, sales, and reporting capabilities.

The architectural question is therefore where these models belong, which persistence foundation they should consume, and which reusable abstractions should deliberately remain outside the initial implementation.

---

## 2. Decision

The Catering module shall establish a focused master-data foundation consisting initially of:

* `ProductCategory`
* `Product`

These models shall be owned by the Catering business module and shall provide the foundational classification and product structure required for subsequent Catering capabilities.

This decision implements the bounded-business-module architecture established by **ADR-001**.

---

## 3. Approved Model Boundary

### 3.1 Model Location

Catering business-domain models shall reside within:

app/modules/catering/models/

They shall not be added to the global:

app/models/

package unless a future platform-wide requirement explicitly justifies such a change.


### 3.2 Persistence Foundation

Catering models shall consume the existing enterprise SQLAlchemy model foundation:

BaseModel
TimestampMixin
AuditMixin
SoftDeleteMixin

The Catering module shall not introduce:

a second ORM base;
a Catering-specific database abstraction;
a second database extension;
a parallel persistence foundation.


### 3.3 Initial Entity Relationship

The initial master-data relationship is:

ProductCategory
       │
       │ 1
       │
       └──────────< Product
                       many

A ProductCategory may contain multiple Product records.

Each Product belongs to one ProductCategory.

The detailed relationship and database-constraint decisions are recorded separately in ADR-003.


## 4. Controlled Values

Where Catering requires controlled values, the established Python Enum convention used by CDCS-EMP shall be followed.

A database-level db.Enum shall not be introduced unless a later requirement specifically justifies database-level enum enforcement.


## 5. Organization and Tenant Scope

Catering master data shall respect the existing enterprise ownership architecture:

Tenant
   │
   └── Organization
          │
          └── Catering business data

Catering records shall not be implicitly owned by individual users.

Organization and tenant ownership remain responsibilities of the existing CDCS-EMP platform architecture.

The Catering module shall not introduce duplicate Tenant, Organization, or equivalent platform identity models.

Where organizational ownership is required, the final organization-scoping implementation shall follow the approved Catering domain model and established enterprise relationship conventions.


## 6. Data Framework Integration

The existing enterprise data framework remains authoritative.

Catering persistence shall consume the established abstractions:

BaseRepository
       ↓
SQLAlchemyRepository

BaseService
       ↓
Repository

No Catering-specific repository abstraction shall be introduced merely for the master-data foundation.

No Catering-specific service abstraction shall be introduced until business rules or orchestration requirements justify one.

The existing enterprise transaction boundary remains responsible for commit and rollback behavior.


## 7. Domain Entity Decision

The Catering module shall not create parallel persistence-independent BaseEntity dataclasses for ProductCategory and Product at this stage.

The existing BaseEntity abstraction remains available for future use where a concrete application-service or domain requirement requires persistence-independent representations.

This avoids unnecessary duplication between domain objects and SQLAlchemy persistence models.


## 8. Master-Data Framework Decision

A generic enterprise-wide master-data framework shall not be introduced at this stage.

The implementation shall focus on the concrete Catering requirements.

Reusable abstractions may be introduced later only when multiple business modules demonstrate a genuine shared requirement.

This preserves the Phase 2 principle of avoiding premature generalization.


## 9. Testing Boundary

Catering master-data tests shall reside under:

tests/unit/modules/catering/

The existing application and database fixtures shall be reused.

Testing shall cover, as applicable:

model construction;
required fields;
default values;
relationships;
constraints;
persistence behavior;
soft-deletion behavior.

No separate Catering database-testing framework shall be introduced.


## 10. Scope Exclusions

This ADR does not establish or authorize:

Supplier master data;
Customer master data;
a generic Party framework;
a unit-of-measure framework;
inventory transactions;
stock movements;
purchasing workflows;
sales workflows;
invoice or receipt processing;
reporting implementation;
Catering-specific repository infrastructure;
a generic enterprise master-data framework.

These capabilities may be addressed by later approved implementation stages or architectural decisions.


## 11. Rationale

The selected boundary provides concrete Catering master data without expanding the CDCS-EMP platform core unnecessarily.

It preserves the separation established by ADR-001:

CDCS-EMP Platform
        │
        ├── reusable enterprise capabilities
        │
        └── Catering Business Module
                │
                ├── ProductCategory
                └── Product

The Catering module therefore receives usable business-domain models while continuing to rely on established platform capabilities for:

persistence;
auditing;
timestamps;
soft deletion;
repositories;
services;
transactions;
security and governance;
testing infrastructure.


## 12. Relationship to Other ADRs
ADR-001 — Phase 2 Business Module Architecture & Strategy

ADR-001 establishes the overarching Phase 2 architectural strategy.

This ADR applies that strategy to the first concrete Catering master-data boundary.

ADR-002 does not supersede ADR-001.

ADR-003 — Catering Relationships & Constraints

ADR-003 records the subsequent detailed relationship and database-constraint decisions for the Catering master-data foundation.

ADR-003 does not replace the model ownership and registration boundary established here.


## 13. Implementation Status

The decision has been implemented through the Catering master-data foundation consisting of:

ProductCategory
Product

The models reside within the Catering module rather than the global platform model package.

The implementation consumes the existing enterprise model foundation.

The corresponding relationship and constraint verification is recorded separately by ADR-003.


## 14. Architectural Authority

This ADR is authoritative for the Catering master-data model registration boundary.

Any future change to:

model ownership;
model package location;
persistence foundation;
organization/tenant ownership boundary;
introduction of a generic master-data framework;

shall be explicitly reviewed.

A material architectural change shall be recorded through a subsequent ADR and shall identify whether it supersedes this decision.


## 15. Approval

Decision: Approved — Retrospective.

Architectural conclusion: The Catering master-data models are business-domain assets of the Catering module and shall consume the existing CDCS-EMP enterprise platform foundation without introducing duplicate infrastructure.

End of ADR-002

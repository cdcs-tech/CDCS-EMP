# CDCS-EMP — ADR-004 — Catering Repository Architecture

**Status:** Approved — Retrospective
**Decision Date:** 31 August 2026
**Documentation Date:** 4 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — Business Modules
**Module:** Catering
**Scope:** Catering repository ownership, reuse of enterprise data infrastructure, and transaction boundary
**Supersedes:** None
**Superseded By:** None
**Related ADRs:** ADR-001, ADR-002, ADR-003

---

## 1. Context

The Catering module requires persistence access for its business-owned master data and subsequent business capabilities.

CDCS-EMP already provides an enterprise data and repository framework under `app/core/data`, including the base repository contract, SQLAlchemy repository implementation, query options, pagination, filtering, sorting, and related persistence infrastructure.

The architectural question is how Catering repositories should consume this existing framework while maintaining module ownership and avoiding duplication of enterprise persistence infrastructure.

The decision must also preserve the established separation between repositories and business-service transaction orchestration.

---

## 2. Decision

Catering repositories shall be owned by the Catering module and shall reuse the existing CDCS-EMP enterprise repository framework.

Catering-specific repositories shall be located under:

app/modules/catering/repositories/

The enterprise repository infrastructure shall remain under:

app/core/data/

Catering repositories shall extend or otherwise consume the existing repository abstractions rather than introducing a second persistence framework.

---

## 3. Repository Ownership

The Catering module owns repository classes required to persist and query Catering-owned business entities.

Examples include:

app/modules/catering/repositories/
├── product.py
├── product_category.py
├── stock_item.py
├── location.py
├── balance.py
├── movement.py
└── transfer.py

These repositories represent the persistence access boundary for Catering-owned entities.

The enterprise platform does not own Catering-specific repository classes.

This preserves the bounded-module principle established by ADR-001 while allowing all modules to share the same enterprise persistence infrastructure.

---

## 4. Enterprise Repository Framework Reuse

Catering repositories shall reuse the existing enterprise data framework, including:

* `BaseRepository`
* `SQLAlchemyRepository`
* `QueryOptions`
* `PaginatedResult`
* Existing filtering and sorting mechanisms
* Existing pagination mechanisms
* Existing persistence conventions

Generic CRUD and query behavior shall not be reimplemented independently inside the Catering module when the enterprise framework already provides the required capability.

The purpose of Catering repositories is therefore to express **Catering-specific persistence access**, not to recreate enterprise persistence infrastructure.

---

## 5. Thin Repository Principle

Catering repositories shall remain intentionally thin.

A repository may provide a specialized method when the business module requires a meaningful, reusable persistence query that is not adequately expressed through the generic repository framework.

Examples include domain-specific lookups such as:

* Product by code
* Product category by code
* Stock item by product
* Inventory location by code
* Stock balance by stock item and location
* Movement by reference
* Similar explicitly required module-specific queries

Generic operations such as ordinary retrieval, pagination, filtering, sorting, and persistence shall continue to use the existing enterprise repository capabilities.

Repositories shall not become a second business-service layer.

---

## 6. Transaction Boundary

Catering repositories shall not own transaction lifecycle management.

Repositories shall not independently perform:

commit()
rollback()
begin()

unless a future architectural decision explicitly establishes a different repository contract.

Transaction ownership remains at the service/application orchestration boundary.

The established architecture is therefore:

Application / Route
        │
        ▼
     Service
        │
        ├── Repository access
        │
        └── Transaction boundary
                │
                ▼
              Database

This ensures that a business operation involving multiple repository operations can be executed atomically within one transaction.

---

## 7. No Catering-Specific Persistence Framework

The Catering module shall not introduce:

* A second ORM abstraction
* A second repository base class without architectural justification
* A separate database session abstraction
* A separate transaction framework
* Module-specific pagination infrastructure
* Module-specific generic filtering infrastructure
* Module-specific generic sorting infrastructure

Such abstractions would duplicate capabilities already provided by the enterprise platform.

Any future requirement that cannot be satisfied by the existing framework shall be evaluated as an architectural decision before introducing a parallel abstraction.

---

## 8. No Premature Generic Catering Repository

The implementation shall not introduce a generic abstraction such as:

CateringRepository[T]

solely to unify Catering repositories.

Repository commonality shall be expressed through the existing enterprise repository framework.

A new Catering-level abstraction may only be introduced if a concrete business requirement demonstrates that it provides meaningful architectural value beyond the existing framework.

---

## 9. Relationship to Services

Catering services are responsible for business rules and orchestration.

Repositories are responsible for persistence access.

The separation is:

Service
  ├── business validation
  ├── business rules
  ├── orchestration
  ├── transaction coordination
  └── repository usage

Repository
  ├── persistence access
  ├── domain-specific queries
  └── enterprise query framework usage

Repositories shall not absorb business rules merely because those rules involve database state.

---

## 10. Relationship to ADR-001

ADR-001 establishes that Phase 2 business modules consume and extend the existing CDCS-EMP platform rather than creating parallel platform infrastructure.

This ADR applies that principle specifically to Catering persistence.

Catering owns its repository classes, while the enterprise platform owns the reusable repository infrastructure.

---

## 11. Relationship to ADR-002

ADR-002 establishes that Catering-owned models reside within the Catering module and consume the existing enterprise persistence foundation.

ADR-004 extends that ownership boundary to persistence access.

The resulting structure is:

app/modules/catering/
├── models/
└── repositories/

while reusable persistence infrastructure remains under:

app/core/data/

---

## 12. Relationship to ADR-003

ADR-003 establishes the relational relationships and database constraints for Catering master data.

ADR-004 does not change those relationships or constraints.

Repositories are responsible for accessing the resulting persistence model but do not redefine the database schema.

---

## 13. Architectural Rationale

This decision provides:

### Module ownership

Catering persistence access remains inside the Catering bounded module.

### Platform reuse

All business modules can use the same enterprise repository infrastructure.

### Consistency

Filtering, sorting, pagination, and persistence behavior remain consistent across the platform.

### Transaction integrity

Business services retain control over multi-step transaction boundaries.

### Maintainability

Repository classes remain focused on persistence access rather than accumulating business logic.

### Extensibility

Future business modules can follow the same repository pattern without requiring Catering-specific infrastructure to become an enterprise dependency.

---

## 14. Scope Exclusions

This ADR does not establish:

* New enterprise repository capabilities
* New database locking infrastructure
* Advanced concurrency mechanisms
* Purchasing repositories
* Finance repositories
* Invoice repositories
* Cross-module repositories
* Generic enterprise domain repositories
* Repository-level transaction ownership
* New persistence abstractions
* Reporting data-provider architecture

Those concerns shall be addressed only when their respective architectural requirements arise.

---

## 15. Implementation Status

The Catering repository foundation has been implemented using the established enterprise data framework.

The current implementation includes repositories for Catering master data and inventory entities, with specialized lookup methods where required.

Focused repository verification has been completed successfully.

The repository layer remains free of transaction ownership, with transaction orchestration delegated to the service layer.

---

## 16. Architectural Authority

This ADR is authoritative for the Catering repository architecture unless superseded by a later approved ADR.

Implementation decisions shall remain consistent with:

* ADR-001 — Phase 2 Business Module Architecture & Strategy
* ADR-002 — Catering Model Registration Boundary
* ADR-003 — Catering Relationships & Database Constraints
* This ADR — Catering Repository Architecture

Future deviations requiring a new persistence abstraction or transaction boundary shall undergo architectural review before implementation.

# ADR-005: Catering Service Architecture

- Status: Approved — Retrospective
- Decision Date: 31 Aug 2026
- Documentation Date: 5 Sep 2026
- Decision Type: Architectural
- Phase: Phase 2 — Business Modules
- Module: Catering
- Scope: Catering service ownership, business-rule orchestration, repository coordination, and transaction boundary
- Supersedes: None
- Superseded By: None
- Related ADRs: ADR-001, ADR-002, ADR-003, ADR-004

## 1. Context

The Catering module requires a service layer to coordinate business operations above the persistence layer.

CDCS-EMP already provides enterprise service and CRUD infrastructure. Catering therefore requires a clear boundary defining which responsibilities belong to Catering services, which responsibilities remain with the enterprise service framework, how repositories are coordinated, and where transaction ownership resides.

Simple master-data operations can be represented through generic CRUD behavior. However, domain operations such as inventory stock posting require business-rule validation, current-state evaluation, coordination of multiple persistence operations, and atomic transaction handling.

A service architecture is therefore required that preserves the bounded-module architecture established by ADR-001 while reusing existing CDCS-EMP infrastructure.

## 2. Decision

Catering services SHALL be implemented under:

    app/modules/catering/services/

Catering services SHALL reuse the existing enterprise service and CRUD infrastructure rather than introducing a parallel service framework.

Catering-specific domain services SHALL own Catering business rules and business-operation orchestration.

Catering services SHALL coordinate Catering repositories and the established enterprise transaction infrastructure.

Catering repositories SHALL remain persistence-oriented and SHALL NOT own business-rule orchestration or transaction lifecycle management.

## 3. Service Ownership

Service implementations that represent Catering business capabilities SHALL remain inside the Catering module.

The module SHALL own the service layer for its business domain, while enterprise service infrastructure SHALL remain responsible for reusable service and CRUD capabilities.

This preserves the bounded context established by ADR-001:

- platform capabilities remain in `app/core/`;
- Catering business services remain in `app/modules/catering/services/`;
- Catering services operate on Catering-owned domain models;
- cross-module behavior is introduced through explicit integration boundaries rather than hidden service dependencies.

## 4. Reuse of Enterprise Service Infrastructure

Catering services SHALL reuse existing CDCS-EMP service infrastructure, including:

- generic CRUD service behavior where appropriate;
- existing repository abstractions;
- existing validation infrastructure;
- existing transaction infrastructure;
- established exception types and service conventions.

Catering SHALL NOT introduce a parallel:

- generic CRUD framework;
- validation framework;
- repository coordination framework;
- transaction framework;
- service lifecycle framework.

## 5. Generic CRUD Services versus Domain Services

Generic CRUD behavior SHALL be used where the business operation is sufficiently simple and does not require additional domain orchestration.

Domain-specific services SHALL be used where operations require:

- business-rule enforcement;
- multi-entity coordination;
- current-state evaluation;
- transaction orchestration;
- sequencing of business operations;
- coordination of multiple repositories;
- domain-specific conflict or validation handling.

The architecture SHALL NOT force domain operations into generic CRUD methods merely to avoid creating a domain service.

## 6. Business Rule Ownership

Business rules SHALL normally be enforced within the Catering service layer unless a later architectural decision establishes a more appropriate boundary.

Catering services SHALL be responsible for rules involving:

- business state;
- relationships between domain entities;
- current inventory state;
- permitted operation sequencing;
- cross-entity consistency;
- transaction-sensitive operations.

Database constraints SHALL continue to enforce persistence-level invariants such as:

- required fields;
- uniqueness;
- foreign-key integrity;
- valid constrained values;
- numeric constraints.

Application input validation MAY occur before service execution, but service-level validation remains authoritative for business rules.

## 7. Repository Coordination

Catering services SHALL coordinate repository operations when a business operation requires more than one persistence action.

Repositories SHALL NOT coordinate other repositories.

For example, a stock-posting operation may require:

1. locating the StockItem;
2. locating or creating the relevant StockBalance;
3. validating the resulting quantity;
4. updating the StockBalance;
5. creating the corresponding StockMovement;
6. completing the operation atomically.

The service layer owns this orchestration.

This preserves the repository boundary established by ADR-004.

## 8. Transaction Ownership

Catering services SHALL use the existing enterprise transaction infrastructure for operations requiring transactional integrity.

Repositories SHALL NOT:

- begin transactions;
- commit transactions;
- roll back transactions;
- independently manage transaction lifecycle.

The service layer SHALL coordinate transaction-sensitive operations so that multi-step business operations succeed or fail atomically.

This includes operations where a business state change must remain consistent with its corresponding ledger or audit record.

## 9. Inventory Stock Posting as a Service Responsibility

Inventory stock posting is a representative domain operation that demonstrates the service boundary.

The stock movement service is responsible for:

1. validating the StockItem;
2. validating the InventoryLocation;
3. validating the movement type;
4. validating the movement quantity and sign;
5. retrieving the current balance;
6. calculating the resulting balance;
7. rejecting operations that would create an invalid negative balance;
8. creating or updating the StockBalance as required;
9. creating the corresponding posted StockMovement;
10. completing the operation within the established transaction boundary.

The repository layer provides persistence access but does not decide whether the operation is a valid business transaction.

## 10. Dependency Direction

The intended dependency direction is:

    Catering Service
        |
        +--> Catering Repository
        |
        +--> Enterprise TransactionManager
        |
        +--> Enterprise Validation / Service Infrastructure

The service layer SHALL depend on repository abstractions and the enterprise transaction abstraction.

The repository layer SHALL NOT depend on Catering services.

Catering services SHALL NOT introduce direct dependencies on infrastructure-specific transaction mechanisms where an existing enterprise abstraction is available.

## 11. Validation Responsibility

Validation is divided according to responsibility.

### Input validation

Responsible for determining whether supplied values have an acceptable structural form.

### Business validation

Responsible for determining whether the requested operation is valid in the current business context.

### Persistence validation

Responsible for enforcing database-level structural and integrity constraints.

Catering services SHALL perform business validation even where database constraints exist, because database constraints alone cannot express all domain rules.

## 12. Error Handling

Catering services SHALL use the established service exception model for business failures.

Expected categories include:

- validation failures;
- not-found conditions;
- conflicts;
- invalid operations;
- transaction-sensitive operation failures.

Services SHALL translate domain failures into the established enterprise exception conventions rather than leaking low-level persistence errors as the primary business API.

## 13. Catering Service Scope

The Catering service layer covers services for the business capabilities currently established within the module, including:

- Product;
- ProductCategory;
- StockItem;
- InventoryLocation;
- StockBalance;
- StockMovement;
- StockTransfer.

The existence of a service does not imply that every operation must be exposed through generic CRUD behavior.

Business complexity determines whether an operation belongs in generic CRUD behavior or a domain-specific service.

## 14. Architectural Constraints

Catering SHALL NOT introduce:

- a parallel Catering service framework;
- a second generic CRUD abstraction;
- a second transaction abstraction;
- repository-owned business logic;
- repository-owned transaction lifecycle;
- a generic domain-service framework without an established enterprise requirement;
- premature service generalization across business modules.

Service abstractions SHALL remain proportional to demonstrated business requirements.

## 15. Relationship to Previous ADRs

### ADR-001 — Phase 2 Business Module Architecture & Strategy

ADR-005 applies the bounded-module architecture to the Catering service layer.

### ADR-002 — Catering Model Registration Boundary

Catering services operate on models owned and registered by the Catering module.

### ADR-003 — Catering Relationships & Database Constraints

Service-level business rules complement, but do not replace, database relationships and constraints.

### ADR-004 — Catering Repository Architecture

ADR-005 establishes the service boundary above the repository boundary defined by ADR-004.

## 16. Rationale

This decision provides:

- clear ownership of Catering business behavior;
- separation between business logic and persistence access;
- atomic transaction handling for multi-step operations;
- reuse of existing enterprise infrastructure;
- improved testability of business rules;
- predictable dependency direction;
- a scalable foundation for future Catering capabilities.

The architecture allows simple operations to remain lightweight while providing domain services where business behavior requires explicit orchestration.

## 17. Explicit Exclusions

This ADR does not establish:

- a new enterprise service framework;
- a generic domain-service framework;
- event-driven service orchestration;
- cross-module distributed transactions;
- workflow integration beyond existing CDCS-EMP capabilities;
- background job architecture;
- API-specific service architecture;
- reporting service architecture.

Those concerns remain outside the scope of this decision unless a future architectural decision establishes otherwise.

## 18. Implementation Status

The Catering service foundation has been implemented using the existing enterprise service and repository infrastructure.

The implementation includes:

- Catering master-data services;
- Inventory services;
- repository coordination through service operations;
- transaction-manager integration;
- domain-level stock movement posting;
- service-level business validation.

Focused service verification has been completed for the implemented service behavior.

## 19. Authority

This ADR is authoritative for the Catering service architecture unless superseded by a later approved architectural decision.

Any future change to the service ownership, transaction boundary, repository/service dependency direction, or introduction of a competing service architecture SHALL be evaluated against this ADR.

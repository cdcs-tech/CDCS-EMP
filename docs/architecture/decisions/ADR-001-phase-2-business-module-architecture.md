# ADR-001 — Phase 2 Business Module Architecture & Strategy

**Status:** Approved — Retrospective
**Decision Date:** 30 August 2026
**Documentation Date:** 4 September 2026
**Decision Type:** Architectural
**Phase:** Phase 2 — Business Modules
**Scope:** CDCS-EMP Enterprise Platform
**Supersedes:** None
**Superseded By:** None

---

## 1. Decision Summary

CDCS-EMP Phase 2 business capabilities shall be implemented as bounded business modules that consume and extend the existing CDCS-EMP platform rather than creating parallel application, persistence, security, transaction, or infrastructure frameworks.

Each business module shall own a clearly defined business capability and the authoritative business data associated with that capability.

The existing CDCS-EMP platform remains responsible for reusable enterprise capabilities such as:

* application architecture;
* configuration;
* module discovery and lifecycle;
* enterprise services;
* data access infrastructure;
* CRUD infrastructure;
* validation;
* workflow;
* execution;
* authentication;
* authorization;
* security and governance;
* audit;
* notifications;
* reporting;
* transaction infrastructure; and
* other reusable platform services.

Business modules shall consume these capabilities through established platform contracts and shall introduce module-specific abstractions only where a genuine business requirement justifies them.

---

## 2. Context

Phase 1 established the reusable CDCS-EMP platform foundation.

By the beginning of Phase 2, the platform already provided the infrastructure required to begin implementing real business capabilities, including:

* Flask application architecture and application factory;
* modular blueprint organization;
* enterprise module discovery and lifecycle management;
* service container and service registration;
* SQL Server persistence;
* SQLAlchemy and migration support;
* repository and data-access infrastructure;
* generic CRUD capabilities;
* validation and workflow infrastructure;
* authentication and RBAC;
* authorization and permission management;
* security and governance;
* audit capabilities;
* reporting infrastructure; and
* execution and transaction infrastructure.

Phase 2 therefore required a different architectural approach from Phase 1.

The objective was no longer to build generic infrastructure first. The objective was to build the first real business capabilities while preserving the reusable enterprise architecture.

Catering was selected as the first business module for the SSRC-IBMS pilot.

---

## 3. Architectural Problem

Without explicit architectural boundaries, business modules could gradually introduce:

* duplicate entity models;
* duplicate tenant or organization models;
* independent repositories;
* independent service frameworks;
* independent transaction managers;
* independent security mechanisms;
* independent persistence layers;
* parallel application surfaces;
* duplicated reporting mechanisms; and
* tightly coupled cross-module business logic.

Such duplication would undermine the purpose of CDCS-EMP as an enterprise platform.

The Phase 2 architecture therefore requires a clear separation between:

1. reusable enterprise platform capabilities; and
2. module-owned business capabilities.

---

## 4. Decision

### 4.1 Business Modules Are Bounded Capabilities

Each business module shall represent a clearly defined business capability.

A module shall own:

* its business entities;
* its business rules;
* its business workflows;
* its business services;
* its module-specific persistence adapters; and
* its application surface where required.

The module shall not automatically own enterprise-wide concepts merely because it requires them.

---

### 4.2 Existing Platform Infrastructure Shall Be Reused

Business modules shall use the existing CDCS-EMP platform wherever an appropriate capability already exists.

Examples include:

```text
Business Module
      │
      ├── Existing Module Framework
      ├── Existing Security / RBAC
      ├── Existing Data Framework
      ├── Existing CRUD Framework
      ├── Existing Validation
      ├── Existing Workflow
      ├── Existing Transaction Infrastructure
      ├── Existing Reporting
      └── Existing Application Surface
```

A new enterprise-wide abstraction shall not be introduced merely because a module has a local requirement.

---

### 4.3 Module-Owned Domain Models

Business entities that belong specifically to a business module shall live within that module.

For Catering:

```text
app/modules/catering/
    models/
```

rather than being placed in a global application model namespace.

This preserves ownership and prevents unrelated modules from becoming coupled to Catering's internal domain model.

---

### 4.4 No Duplicate Enterprise Identity

Business modules shall reuse the platform's existing organizational and identity architecture.

A module shall not introduce a parallel:

* Tenant;
* Organization;
* User;
* authentication system; or
* authorization system

unless a future architectural decision explicitly establishes such a requirement.

---

### 4.5 Repository and Service Boundaries

Business modules shall reuse the enterprise repository and service foundations.

The normal dependency direction is:

```text
Application / Route
        │
        ▼
      Service
        │
        ▼
    Repository
        │
        ▼
 Enterprise Data Framework
        │
        ▼
    Persistence
```

Repositories remain primarily concerned with persistence and retrieval.

Services own business rules, validation, orchestration, and business operations where those concerns exist.

---

### 4.6 Transaction Ownership

Transactions shall be managed through the existing platform transaction abstraction.

Repositories shall not independently own application transaction boundaries.

Where a business operation requires atomicity, the appropriate service or execution boundary shall coordinate the transaction using the existing transaction infrastructure.

---

### 4.7 Security and Governance

Business modules shall integrate with the existing CDCS-EMP:

* authentication;
* RBAC;
* permissions;
* authorization;
* audit; and
* governance

mechanisms.

A module shall not create an independent security subsystem.

---

### 4.8 Application Surface

Business modules may provide their own routes, forms, templates, and user-facing workflows where required.

Those surfaces shall remain integrated with the existing CDCS-EMP application rather than becoming independent applications.

---

### 4.9 Cross-Module Integration

A module shall not absorb another module's business capability merely because integration is required.

Cross-module requirements shall be handled through explicit interfaces, services, contracts, or other approved integration mechanisms.

For example, Catering Inventory may consume Catering Product information without becoming the owner of the Product master.

---

### 4.10 Avoid Premature Generalization

Phase 2 implementation shall favor concrete business capability over speculative enterprise-wide frameworks.

A reusable abstraction should be introduced only when:

1. a real business requirement exists;
2. the abstraction has a clearly defined ownership boundary; and
3. reuse is demonstrated or strongly justified.

---

## 5. Catering Application of the Decision

The first implementation of this architecture is the Catering module.

The current Catering structure follows the bounded-module principle:

```text
app/modules/catering/
    models/
    repositories/
    services/
    routes/
    forms/
    security/
```

Catering owns its business capabilities while consuming platform infrastructure.

The Product and ProductCategory master-data implementation established the initial module boundary.

---

## 6. Inventory Boundary

The same architectural principle applies to Catering Inventory.

Inventory owns:

* stock configuration;
* stock items;
* inventory locations;
* stock balances;
* stock movements;
* stock transfers; and
* inventory-related stock controls.

Inventory does not automatically own:

* purchasing;
* supplier management;
* expenses;
* income;
* invoicing;
* payments; or
* general accounting.

Those capabilities remain separate business concerns and may integrate with Inventory through explicit interfaces in later phases.

---

## 7. Consequences

### Positive Consequences

This decision:

* preserves the reusable CDCS-EMP platform;
* establishes clear module ownership;
* reduces architectural duplication;
* limits coupling between business modules;
* improves maintainability;
* supports independent module evolution;
* provides clear data ownership;
* supports auditability and governance;
* allows future modules to reuse proven platform capabilities; and
* prevents premature enterprise-wide generalization.

### Negative Consequences

This decision requires developers to:

* understand existing platform contracts before adding infrastructure;
* distinguish business capability from enterprise infrastructure;
* maintain explicit module boundaries;
* introduce additional interfaces when cross-module integration is required; and
* resist creating convenient but architecturally duplicated abstractions.

These costs are intentional and support the long-term enterprise architecture.

---

## 8. Alternatives Considered

### 8.1 Independent Application per Business Module

Rejected.

This would duplicate application infrastructure, authentication, configuration, persistence, and deployment concerns.

### 8.2 Global Business Entity Model

Rejected.

A global model namespace would blur business ownership and encourage unrelated modules to depend directly on one another's internal entities.

### 8.3 Generic Enterprise Business-Module Framework

Rejected at this stage.

The platform already provides the module lifecycle and reusable infrastructure required. Additional generic business abstractions should only be introduced when justified by actual cross-module requirements.

### 8.4 Module-Specific Infrastructure Frameworks

Rejected.

Business modules should consume the established enterprise frameworks rather than create parallel repository, service, transaction, security, or persistence frameworks.

---

## 9. Governance

Material changes to the following require architectural review and, where appropriate, a new or superseding ADR:

* module boundaries;
* business data ownership;
* persistence architecture;
* organization or tenant ownership;
* transaction architecture;
* security architecture;
* repository architecture;
* service architecture;
* module lifecycle;
* cross-module integration strategy.

---

## 10. Implementation Traceability

### Related Phase

Phase 2 — First Business Modules and Business Module Strategy.

### Primary Module

Catering.

### Related Architectural Evidence

* Phase 2 authoritative roadmap, Version 1.0;
* Catering master-data implementation;
* Catering module registration boundary;
* Catering repository and service implementation;
* Catering security and governance integration;
* Catering application surface;
* Catering Inventory domain implementation;
* Enterprise transaction management implementation.

### Related ADRs

* ADR-002 — Catering Model Registration Boundary
* ADR-003 — Catering Relationships & Database Constraints

### Related Implementation History

The decision is reflected progressively in the Phase 2 implementation history, beginning with the Catering master-data foundation and continuing through the current Inventory architecture.

---

## 11. Roadmap Impact

This ADR establishes the architectural foundation against which the Phase 2 roadmap shall be maintained.

The Phase 2 roadmap remains the planning and sequencing authority.

ADRs remain the authority for the architectural decisions they document.

Where implementation subsequently changes an architectural decision, a new ADR or superseding ADR shall be created and the roadmap shall be reconciled accordingly.

---

## 12. Status

**Approved — Retrospective**

This ADR documents the Phase 2 architecture already established through approved planning and implementation evidence.

It does not claim to be a contemporaneous decision record from the original Phase 2 planning date.

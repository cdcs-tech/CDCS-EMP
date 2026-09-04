
# ADR-007 — Catering Application Surface Architecture

* **Status:** Approved — Retrospective
* **Decision Date:** 31 August 2026
* **Documentation Date:** 5 September 2026
* **Decision Type:** Architectural
* **Phase:** Phase 2 — Business Modules
* **Module:** Catering
* **Scope:** Catering application routes, templates, forms, navigation, authorization integration, and application-surface ownership
* **Related ADRs:** ADR-001, ADR-002, ADR-005, ADR-006

---

## 1. Context

The Catering module requires a user-facing application surface through which authorized users can access Catering functionality.

The implemented Catering application surface includes module-owned routes, templates, forms, navigation integration, and authorization checks. These components must operate within the established CDCS-EMP application architecture rather than creating a parallel application or presentation framework.

The platform already provides the foundational application mechanisms required by business modules, including the Flask application factory, blueprint/module registration, routing infrastructure, authentication, authorization, enterprise layout and template conventions, validation, services, repositories, and transaction boundaries.

A clear architectural boundary is therefore required to establish:

* which application-surface components are owned by the Catering module;
* which application capabilities remain platform-owned;
* how Catering routes interact with Catering services;
* how templates and forms participate in the application boundary;
* how navigation integrates with the enterprise application shell;
* how authorization is applied at the application surface; and
* which application or frontend capabilities are explicitly outside the scope of the Catering module.

This ADR formalizes the application-surface architecture already established through the Catering implementation.

---

## 2. Decision

The Catering module shall own its business-specific application surface while consuming the existing CDCS-EMP enterprise application foundation.

The Catering application surface shall remain a bounded module concern and shall not introduce a parallel application, routing, frontend, authentication, authorization, or presentation framework.

The architecture is defined by the following decisions.

### 2.1 Module-owned application surface

Catering-specific application components shall reside within the Catering module boundary.

These components include, as applicable:

* routes;
* route registration;
* Catering templates;
* Catering forms;
* Catering navigation integration;
* Catering application-surface permission declarations; and
* application-specific presentation coordination.

The module owns the application surface required to expose its business capabilities but does not own the enterprise application shell or shared platform infrastructure.

---

### 2.2 Existing enterprise application foundation remains authoritative

The Catering module shall reuse the existing CDCS-EMP application foundation.

The following remain platform-owned and authoritative:

* Flask application factory;
* application configuration;
* module and blueprint registration;
* enterprise routing mechanisms;
* authentication;
* authorization evaluation and enforcement;
* enterprise security policies;
* enterprise template/layout foundations;
* shared validation infrastructure;
* enterprise services;
* repository infrastructure;
* transaction infrastructure; and
* other established platform capabilities.

Catering shall integrate with these mechanisms rather than replacing or duplicating them.

---

### 2.3 Route boundary

Catering routes constitute the HTTP/application boundary of the module.

Routes are responsible for application-level concerns such as:

* receiving HTTP requests;
* resolving route parameters;
* obtaining authenticated-user context;
* invoking authorization mechanisms;
* validating or constructing form/input data;
* invoking the appropriate Catering service;
* preparing response data; and
* returning the appropriate template or application response.

Routes shall not become the location for Catering business rules, persistence logic, or transaction lifecycle management.

Business operations shall be delegated to the appropriate Catering services in accordance with ADR-005.

---

### 2.4 Service delegation

The application surface shall delegate business operations to Catering services.

The dependency direction shall remain:

HTTP Request
    ↓
Catering Route
    ↓
Catering Service
    ↓
Catering Repository
    ↓
Enterprise Data Infrastructure

Where transaction coordination is required, the service shall use the established enterprise transaction abstraction.

The route layer shall not directly coordinate repository transactions or implement multi-step business workflows.

---

### 2.5 Template boundary

Catering templates shall remain module-owned presentation components while consuming the existing enterprise application layout and presentation conventions.

Templates are responsible for:

* presenting application data;
* rendering forms;
* displaying validation or operation feedback;
* providing navigation relevant to Catering; and
* invoking established presentation conventions.

Templates shall not become a secondary location for business rules, persistence operations, authorization decisions, or transaction management.

The enterprise application shell, layout conventions, and shared presentation infrastructure remain platform-owned.

---

### 2.6 Form boundary

Catering forms shall handle application input concerns such as:

* request data structure;
* field definitions;
* user input representation;
* basic form-level input handling; and
* presentation of validation feedback where appropriate.

Forms shall not replace the domain/business validation performed by Catering services.

Business invariants and business-operation rules remain service-owned in accordance with ADR-005, while persistence invariants continue to be reinforced by database constraints where appropriate.

---

### 2.7 Navigation integration

Catering shall integrate into the existing CDCS-EMP enterprise navigation and application shell.

The module may contribute Catering-specific navigation entries required to expose its authorized capabilities, but it shall not create:

* a separate application shell;
* a separate sidebar framework;
* a separate navigation registry architecture;
* an independent layout hierarchy; or
* a parallel UI framework.

Navigation integration shall respect the existing enterprise authorization model and application conventions.

---

### 2.8 Application-surface authorization

Authorization at the Catering application surface shall use the enterprise authorization mechanisms established by the platform.

Catering owns the definition of permissions representing its business capabilities, as established under ADR-006.

The application surface shall use those permissions through the existing enterprise authorization mechanism.

The architectural distinction remains:

Catering
    owns → business permissions

Enterprise Security
    owns → authorization evaluation and enforcement

Application-surface authorization does not replace service-level business validation.

Authorization determines whether an actor may access or invoke a capability; business validation determines whether the requested operation is valid.

---

### 2.9 Separation of presentation and business logic

The Catering application surface shall maintain a clear separation between presentation concerns and business concerns.

The principal boundaries are:

| Layer                 | Primary responsibility                 |
| --------------------- | -------------------------------------- |
| Route                 | HTTP/application coordination          |
| Form                  | User input representation              |
| Template              | Presentation                           |
| Service               | Business rules and orchestration       |
| Repository            | Persistence access                     |
| Enterprise data layer | Shared persistence infrastructure      |
| Enterprise security   | Authorization and security enforcement |

No layer shall assume responsibilities belonging to another layer merely for implementation convenience.

---

### 2.10 Error and feedback handling

The Catering application surface shall use the existing enterprise/application conventions for communicating validation errors, operation failures, and user feedback.

Routes may translate service/application outcomes into appropriate HTTP or presentation responses, but they shall not duplicate the underlying business rules merely to produce user-facing feedback.

Where enterprise error-handling or flash-message conventions already exist, Catering shall reuse them.

---

### 2.11 No parallel application framework

The Catering module shall not introduce a second application framework for its own use.

Specifically, the module shall not create parallel mechanisms for:

* application factory management;
* route registration;
* blueprint management;
* authentication;
* authorization;
* template/layout management;
* form framework;
* validation framework;
* service framework;
* repository framework;
* transaction management; or
* enterprise navigation infrastructure.

Any genuinely reusable enterprise capability discovered during implementation shall be considered through the normal platform architecture rather than being silently duplicated inside Catering.

---

## 3. Dependency Direction

The application-surface dependency direction shall remain consistent with the broader CDCS-EMP architecture.

Enterprise Application Foundation
            ↑
            │
       Catering Module
            │
     ┌──────┴──────┐
     ↓             ↓
Application      Services
Surface            │
                   ↓
             Repositories
                   │
                   ↓
          Enterprise Data Layer

Catering consumes enterprise application capabilities.

The enterprise application foundation shall not acquire dependencies on Catering-specific application components merely to support the module.

---

## 4. Consequences

### Positive consequences

* Catering receives a complete user-facing application surface without duplicating platform infrastructure.
* Application responsibilities remain clearly separated.
* Routes remain thin and easier to maintain.
* Business rules remain concentrated in services.
* Templates remain focused on presentation.
* Forms remain focused on input handling.
* Existing enterprise authorization and security controls remain authoritative.
* Catering can integrate naturally with the enterprise application shell.
* Future business modules can follow the same bounded-module pattern.
* The architecture avoids premature creation of a separate frontend or application framework.

### Trade-offs

* Catering-specific UI requirements must conform to established enterprise application conventions.
* Some presentation capabilities may initially require reuse of existing platform mechanisms rather than module-specific abstractions.
* New reusable application infrastructure must be evaluated at the enterprise-platform level instead of being introduced solely for Catering.

These trade-offs are intentional and support consistency across CDCS-EMP business modules.

---

## 5. Scope

This ADR applies to the Catering application surface, including:

* Catering routes;
* Catering route registration;
* Catering templates;
* Catering forms;
* Catering navigation integration;
* application-surface authorization;
* interaction between routes and Catering services; and
* interaction between the Catering application surface and the enterprise application foundation.

---

## 6. Explicit Exclusions

This ADR does not establish or authorize:

* a new frontend framework;
* a single-page application architecture;
* a separate JavaScript application;
* a new REST API architecture;
* a new API gateway;
* a separate authentication system;
* a separate authorization system;
* a separate template engine;
* a separate UI component framework;
* a Catering-specific application shell;
* a separate navigation framework;
* a reporting UI architecture;
* a workflow UI architecture;
* a mobile application architecture;
* background-job architecture; or
* a generalized enterprise UI framework.

Such capabilities, if required in the future, shall be addressed through separate architectural decisions.

---

## 7. Relationship to Other ADRs

### ADR-001 — Phase 2 Business Module Architecture & Strategy

ADR-001 establishes the overall bounded business-module architecture. ADR-007 applies that architecture specifically to the Catering application surface.

### ADR-002 — Catering Model Registration Boundary

ADR-002 establishes Catering ownership of its business-domain models. ADR-007 addresses how those business capabilities are exposed through the application surface.

### ADR-005 — Catering Service Architecture

ADR-005 establishes service ownership of Catering business rules, orchestration, and transaction coordination. ADR-007 establishes that routes delegate business operations to those services.

### ADR-006 — Catering Security & Governance Integration

ADR-006 establishes Catering's integration with enterprise authorization, security, audit, and governance. ADR-007 applies the authorization boundary to the user-facing application surface.

---

## 8. Implementation Alignment

The Catering application surface is implemented within the established module architecture using:

app/modules/catering/routes/
app/modules/catering/forms/
app/modules/catering/security/
app/templates/modules/catering/
app/templates/partials/

The application surface integrates with the existing CDCS-EMP application shell, module registration, enterprise authorization, services, repositories, validation, and persistence infrastructure.

This ADR documents the architectural boundary represented by that implementation.

---

## 9. Decision Rationale

The chosen architecture preserves the central CDCS-EMP principle that business modules own business capabilities while the platform owns reusable enterprise capabilities.

Catering therefore owns what is specific to exposing Catering functionality, but it does not become an independent application within the application.

This approach provides:

1. clear ownership;
2. consistent application behavior;
3. centralized security enforcement;
4. reuse of enterprise infrastructure;
5. separation of presentation and business logic;
6. lower architectural duplication; and
7. a repeatable pattern for subsequent Phase 2 business modules.

The architecture deliberately favors composition over duplication and reuse over premature generalization.

---

## 10. Status

**Approved — Retrospective**

This ADR formally records the application-surface architecture established during the implementation of the Catering module.

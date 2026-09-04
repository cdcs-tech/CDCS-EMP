# ADR-006: Catering Security & Governance Integration

- Status: Approved — Retrospective
- Decision Date: 31 Aug 2026
- Documentation Date: 5 Sep 2026
- Decision Type: Architectural
- Phase: Phase 2 — Business Modules
- Module: Catering
- Scope: Catering security, authorization, audit, and governance integration
- Supersedes: None
- Superseded By: None
- Related ADRs: ADR-001, ADR-002, ADR-005

## 1. Context

The Catering module operates within the CDCS-EMP enterprise security and governance architecture.

CDCS-EMP already provides centralized capabilities for authentication, authorization, roles, permissions, security policies, audit, compliance, and governance.

The Catering module therefore requires a defined integration boundary that allows it to express its business-specific security requirements without introducing a parallel security or governance framework.

Catering operations include business capabilities that must be protected according to established authorization rules. The module also participates in enterprise audit and governance requirements.

The architectural question is how Catering-specific permissions, authorization enforcement, audit behavior, and governance controls should integrate with the existing enterprise security architecture.

## 2. Decision

Catering SHALL integrate with the existing CDCS-EMP enterprise security and governance infrastructure.

Catering SHALL define and own the permissions required by its business capabilities, while the enterprise security architecture SHALL remain responsible for authentication, authorization evaluation, policy enforcement, audit infrastructure, compliance infrastructure, and governance mechanisms.

The Catering module SHALL NOT introduce a parallel security, authorization, audit, compliance, or governance framework.

The established enterprise authorization engine SHALL be the authoritative mechanism for determining whether a user or execution context is permitted to perform a protected Catering operation.

## 3. Security Ownership Boundary

Security responsibility is divided between the Catering module and the enterprise platform.

### Catering owns

- Catering-specific permission definitions;
- mapping of business capabilities to required permissions;
- identification of operations requiring authorization;
- module-specific security metadata where required.

### Enterprise platform owns

- authentication;
- identity management;
- role management;
- permission evaluation;
- authorization enforcement mechanisms;
- security policies;
- audit infrastructure;
- compliance infrastructure;
- governance controls.

This preserves the bounded-module architecture established by ADR-001.

Catering expresses its security requirements; the enterprise platform provides and enforces the security mechanisms.

## 4. Permission Definition and Registration

Catering-specific permissions SHALL be defined within the Catering module's security boundary.

Permissions SHALL represent meaningful business capabilities rather than implementation details.

Examples include permissions governing capabilities such as:

- viewing Catering data;
- creating or maintaining Catering master data;
- managing inventory configuration;
- recording or posting stock movements;
- managing stock transfers;
- performing other protected Catering operations.

The exact permission set remains a module implementation concern and may evolve as business capabilities are introduced.

Catering permissions SHALL integrate with the existing enterprise permission and RBAC model.

The module SHALL NOT create a separate permission registry or authorization store.

## 5. Authorization Enforcement

Authorization SHALL be evaluated through the existing CDCS-EMP authorization engine.

Catering routes, services, and other protected application boundaries SHALL use the established authorization mechanisms rather than implementing independent authorization logic.

Where an operation crosses multiple service or repository calls, authorization SHALL be established before the protected business operation proceeds.

Business services SHALL remain responsible for enforcing business rules after authorization has been established.

Authorization and business validation therefore remain distinct responsibilities:

```text
Request
   |
   v
Authentication / Identity
   |
   v
Enterprise Authorization
   |
   v
Catering Service
   |
   v
Business Validation
   |
   v
Repository / Transaction Boundary

The precise enforcement location may vary according to the established application architecture, but the enterprise authorization engine remains authoritative.

6. Relationship Between Authorization and Database Constraints

Authorization controls whether an execution context is permitted to perform an operation.

Database constraints control whether persisted data satisfies structural and integrity requirements.

Neither replaces the other.

For example:

a user may be authorized to post stock;
the stock-posting service must still validate the business operation;
the database must still enforce applicable integrity constraints.

Security SHALL therefore be treated as an application and enterprise governance responsibility rather than delegated to database constraints.

7. Service-Level Security Boundary

ADR-005 establishes the Catering service layer as the owner of business-rule orchestration.

Security integration SHALL complement this boundary.

Catering services SHALL rely on the established enterprise authorization mechanisms and SHALL NOT create service-specific authorization engines.

Where a protected service operation requires authorization-aware execution, the service boundary may participate in authorization enforcement according to existing CDCS-EMP security conventions.

The service layer remains responsible for business rules; the enterprise security layer remains responsible for authorization policy.

8. Audit Integration

Catering SHALL participate in the existing enterprise audit infrastructure.

Security-relevant and governance-relevant Catering operations SHALL use established audit mechanisms where audit requirements apply.

The Catering module SHALL NOT create a separate audit framework merely to record Catering operations.

Where the existing audit infrastructure captures:

actor identity;
operation;
affected entity;
timestamp;
execution context;
relevant outcome;

Catering SHALL use those established mechanisms rather than duplicating them.

Business-specific operational records, such as stock movements, remain domain records and are not automatically substitutes for enterprise audit records.

9. Governance Integration

Catering SHALL operate within the enterprise governance framework.

Governance requirements applicable to Catering SHALL be enforced through existing CDCS-EMP governance capabilities wherever those capabilities already provide the required control.

The module may define business-specific governance metadata or permission requirements where necessary, but governance mechanisms themselves remain platform-owned.

This allows governance policies to be applied consistently across current and future business modules.

10. Security and Business Responsibility Separation

Security authorization and business validation SHALL remain separate concerns.

For a protected stock operation, for example:

the execution context is authenticated;
authorization determines whether the actor may perform the operation;
the Catering service validates the business request;
the service evaluates current stock state;
the service coordinates the transaction;
the resulting business records are persisted;
applicable enterprise audit/governance mechanisms record the operation.

A successful authorization decision SHALL NOT be interpreted as approval of the business operation itself.

Likewise, a valid business operation SHALL NOT bypass required authorization.

11. Dependency Direction

The intended dependency direction is:

Catering
   |
   +--> Enterprise Security / Authorization Abstractions
   |
   +--> Catering Services
   |
   +--> Catering Repositories
   |
   +--> Enterprise Audit / Governance Infrastructure

Catering may consume enterprise security and governance capabilities.

Enterprise security infrastructure SHALL NOT become dependent on Catering-specific implementation details.

This preserves platform independence from individual business modules.

12. No Parallel Security Framework

Catering SHALL NOT introduce:

a second RBAC implementation;
a second permission engine;
Catering-specific authentication;
a parallel identity system;
a separate security-policy framework;
a separate audit framework;
a separate compliance framework;
a separate governance framework.

Existing CDCS-EMP security and governance capabilities remain authoritative.

13. Security and Governance Scope

The current Catering security boundary covers the business capabilities implemented within the module, including:

Product;
ProductCategory;
StockItem;
InventoryLocation;
StockBalance;
StockMovement;
StockTransfer.

As additional Catering capabilities are introduced, their required permissions and governance requirements SHALL be defined within the same established architecture.

The addition of a new business capability does not justify creating a new security framework.

14. Relationship to Previous ADRs
ADR-001 — Phase 2 Business Module Architecture & Strategy

ADR-006 applies the bounded-module architecture to Catering security and governance.

ADR-002 — Catering Model Registration Boundary

Security and governance apply to models owned by the Catering module without changing their ownership boundary.

ADR-005 — Catering Service Architecture

ADR-006 complements the service boundary by establishing how protected Catering operations integrate with enterprise authorization and governance.

ADR-006 does not redefine the service transaction boundary established by ADR-005.

15. Rationale

This decision provides:

centralized enterprise security enforcement;
clear ownership of Catering-specific permissions;
consistent RBAC behavior across modules;
reuse of existing audit and governance capabilities;
reduced security duplication;
predictable authorization behavior;
improved maintainability;
consistent governance across business modules;
a scalable security boundary for future Catering capabilities.

The architecture allows Catering to express its business security requirements without fragmenting the enterprise security model.

16. Explicit Exclusions

This ADR does not establish:

a new enterprise security framework;
a new RBAC framework;
a new permission engine;
a new authentication architecture;
a new identity-provider architecture;
a Catering-specific audit framework;
a Catering-specific compliance framework;
a Catering-specific governance framework;
distributed authorization;
cross-module security-policy architecture;
API gateway security architecture.

These concerns remain outside the scope of this decision unless established by a future architectural decision.

17. Implementation Status

The Catering security and governance integration has been implemented using the existing CDCS-EMP security architecture.

The implementation includes:

Catering-specific permission definitions;
integration with the enterprise permission and RBAC model;
established authorization enforcement;
integration with existing security and governance mechanisms;
protection of Catering application capabilities according to the established authorization model.

Focused security and application verification has been completed for the implemented Catering security boundary.

18. Authority

This ADR is authoritative for the Catering security and governance integration unless superseded by a later approved architectural decision.

Any future change introducing a competing security, authorization, audit, compliance, or governance mechanism SHALL be evaluated against this ADR.

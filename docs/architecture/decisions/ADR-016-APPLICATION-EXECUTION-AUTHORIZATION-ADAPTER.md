# ADR-016 — Application Execution Authorization Adapter

## Status

Approved — Active

## Decision Date

19 September 2026

## Context

CDCS-EMP contains two complementary security layers.

The application persistence layer represents authenticated users and their effective permissions through:

`User → UserRole → Role → RolePermission → Permission`

The enterprise security framework represents authorization subjects and capabilities through:

`Role → Permission → AuthorizationEngine`

The application authorization service and HTTP authorization decorators already resolve permissions through the authenticated application `User`.

The enterprise execution framework, however, evaluates execution permissions using `ExecutionContext.user_id`.

The execution startup integration therefore passes the application user identifier to the enterprise `AuthorizationEngine`. The concrete enterprise authorization engine expects an enterprise security subject such as the core `Role` abstraction and must remain independent of application persistence models.

The architecture must therefore provide a bridge between the application identity/RBAC boundary and the enterprise execution authorization boundary without introducing a second authorization engine or coupling the enterprise security framework to application persistence.

## Decision

CDCS-EMP will use an **application-level execution authorization adapter** at the application/security integration boundary.

The adapter will:

1. Resolve the authenticated application user from the supplied application user identifier.
2. Use the existing application `User.has_permission()` capability to determine whether the user holds the requested permission.
3. Construct an enterprise `Permission` representation for the requested execution permission.
4. Construct an enterprise `Role` representation for the application user for the purpose of enterprise authorization evaluation.
5. Pass that enterprise `Role` subject through the existing `AuthorizationEngine`.
6. Preserve the existing enterprise policy evaluation and audit behavior.
7. Remain outside the enterprise security core.

The adapter is an integration boundary, not a new authorization framework.

## Architectural Boundary

The approved execution authorization flow is:

`ExecutionContext.user_id`
→ `Application Execution Authorization Adapter`
→ `app.models.User`
→ `User.has_permission()`
→ `Enterprise Role/Permission representation`
→ `AuthorizationEngine.can()`
→ enterprise authorization policies/audit
→ execution authorization decision

The enterprise security core must not import or directly depend on:

- `app.models.User`
- `UserRole`
- application persistence `Role`
- application persistence `Permission`
- Flask-Login
- application database/session details

## Rationale

This approach preserves the existing architecture in both directions.

The application layer remains responsible for resolving application identity and persisted RBAC.

The enterprise layer remains responsible for authorization semantics, policy evaluation, audit behavior, and execution enforcement.

The adapter provides translation between the two models without requiring either layer to absorb the implementation details of the other.

## Authorization Semantics

The adapter must not introduce permission aliases, alternative permission stores, or duplicate permission evaluation rules.

Execution permissions continue to use the existing canonical Procurement execution permission codes, for example:

- `PROCUREMENT.PURCHASE_REQUEST.SUBMIT`
- `PROCUREMENT.PURCHASE_ORDER.SUBMIT`

The application `User.has_permission()` method remains the persistence-layer permission resolution mechanism.

## Security Requirements

Execution authorization must occur before command handler execution.

An unauthorized user must continue to receive an authorization failure and the command handler must not execute.

An authorized user must be able to pass through the same real startup execution authorization path and reach the registered command handler.

## Scope

This decision applies to application-to-enterprise authorization integration for command execution.

It does not change:

- application RBAC persistence
- enterprise `AuthorizationEngine`
- enterprise `Role`
- enterprise `Permission`
- command dispatcher semantics
- Procurement workflow definitions
- Procurement command definitions
- Procurement handlers
- HTTP authorization decorators
- authentication

## Verification

The implementation must verify both sides of the execution authorization boundary:

### Unauthorized execution

An application user without the required permission must be denied before the command handler executes.

### Authorized execution

An application user holding the required persisted permission must pass the enterprise execution authorization path and allow the registered command handler to execute.

Both cases must use the real application startup authorization composition rather than a standalone mocked authorization path.

## Consequences

### Positive

- Enterprise security remains application-independent.
- Existing application RBAC remains authoritative for persisted user permissions.
- Existing enterprise authorization policies and auditing remain in use.
- Procurement does not require module-specific authorization logic.
- The execution framework receives a real authorization decision for application users.
- No parallel RBAC or authorization framework is introduced.

### Constraint

The application/security integration layer owns the translation between application RBAC subjects and enterprise authorization subjects.

That translation must remain thin and must not become a second authorization engine.

## Related Architecture

- ADR-006 — Catering Security & Governance Integration
- Phase 2.2 Purchasing & Expense Management architecture
- Phase 2.2.4.1 — Procurement Workflow Scope & Lifecycle Ownership
- Phase 2.2.4.4 — Procurement Workflow Authorization & Execution Architecture

## Decision Summary

CDCS-EMP will bridge application users into enterprise command authorization through a thin application-level adapter.

The enterprise security core remains independent of application persistence and remains the authoritative mechanism for execution authorization enforcement.

# Phase 2.2.6 — Expense Workflow HTTP/UI Integration and Browser Verification

**Status:** IMPLEMENTED / VERIFIED
**Phase:** Phase 2.2 — Purchasing & Expense Management
**Module:** Expense Management
**Component:** Expense Workflow HTTP/UI Integration and Browser Verification
**Decision Type:** Implementation & Verification Checkpoint

---

## 1. Purpose

This document records the completed implementation and verification of the **Phase 2.2.6 Expense Workflow HTTP/UI Integration and Browser Verification** stage.

The stage integrates the already-approved and implemented Expense workflow into the Expense Management HTTP/UI surface and verifies the complete workflow lifecycle through both automated tests and browser-based execution.

This checkpoint does **not** introduce or modify the workflow architecture established under the preceding Phase 2.2.5 decisions.

The approved workflow model, authorization design, enterprise execution path, transaction boundary, and domain responsibilities remain authoritative.

---

## 2. Preceding Authoritative Decisions

Phase 2.2.6 is implemented in accordance with the following previously approved decisions:

1. **Phase 2.2 — Purchasing & Expense Management**
2. **Phase 2.2.5.1 — Expense Workflow Scope & Lifecycle Ownership**
3. **Phase 2.2.5.2 — Expense Workflow Detailed Transition Design**
4. **Phase 2.2.5.3 — Expense Workflow Authorization & Execution Design**
5. **Phase 2.2.5 — Expense Workflow Implementation and Verification**

These preceding decisions establish:

- Expense as the sole workflow-bearing entity within the initial Expense Management capability.
- The six-state Expense workflow.
- The six approved workflow transitions.
- The six workflow operation identities.
- Enterprise authorization and execution ownership.
- Command/dispatcher/authorization/transaction/handler/service/workflow separation.
- No Expense-specific authorization or execution infrastructure.
- No `ExpenseApproval` entity.
- No direct persistence dependency on Procurement, Inventory, Catering, or Finance.
- `Approved Expense` remains distinct from a financial transaction.

Phase 2.2.6 implements the HTTP/UI boundary against those established contracts.

---

# 3. Approved Expense Workflow Lifecycle

The implemented Expense workflow contains exactly six states:

- `DRAFT`
- `SUBMITTED`
- `RETURNED`
- `APPROVED`
- `REJECTED`
- `CLOSED`

The approved transitions are:

| Current State | Operation | Target State |
|---|---|---|
| DRAFT | `expense.submit` | SUBMITTED |
| SUBMITTED | `expense.approve` | APPROVED |
| SUBMITTED | `expense.reject` | REJECTED |
| SUBMITTED | `expense.return` | RETURNED |
| RETURNED | `expense.resubmit` | SUBMITTED |
| APPROVED | `expense.close` | CLOSED |

Terminal states remain:

- `REJECTED`
- `CLOSED`

No reopening transition was introduced.

---

# 4. HTTP Workflow Integration

The Expense Management HTTP layer now exposes dedicated POST endpoints for all six workflow operations:

```text
/expenses/<expense_id>/submit
/expenses/<expense_id>/approve
/expenses/<expense_id>/reject
/expenses/<expense_id>/return
/expenses/<expense_id>/resubmit
/expenses/<expense_id>/close
```

Each workflow endpoint:

1. Requires an authenticated user.
2. Requires the corresponding workflow permission.
3. Constructs the appropriate Expense workflow command.
4. Creates an enterprise `ExecutionContext`.
5. Supplies the authenticated user's ID through `ExecutionContext.user_id`.
6. Identifies the Expense module as `EXPENSE`.
7. Supplies the appropriate workflow operation identity.
8. Dispatches through the enterprise `CommandDispatcher`.
9. Uses the established authorization and transaction boundaries.
10. Flashes the execution result.
11. Redirects to the Expense detail page.

The routes do not directly change the Expense status.

---

# 5. Execution Context and Authorization

The HTTP workflow integration correctly supplies the authenticated user's identity to the enterprise execution context.

The execution context follows the established pattern:

```python
ExecutionContext(
    user_id=str(current_user.id),
    module_name="EXPENSE",
    operation="<expense workflow operation>",
)
```

The workflow routes therefore remain inside the established enterprise authorization path.

The implementation does not introduce:

- Direct `current_user.has_permission()` checks inside handlers.
- Direct `AuthorizationEngine` calls from handlers.
- Expense-specific authorization engines.
- Expense-specific transaction managers.
- HTTP-level bypasses of the command dispatcher.
- Hard-coded workflow role authority.

Authorization remains governed by the enterprise authorization architecture established in Phase 2.2.5.3.

---

# 6. CSRF Protection

All Expense workflow forms are protected by CSRF tokens.

Each workflow form includes the application's CSRF token:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

CSRF protection is therefore maintained for all six workflow operations:

- Submit
- Approve
- Reject
- Return
- Resubmit
- Close

The implementation does not introduce an alternative or workflow-specific CSRF mechanism.

---

# 7. State-Driven Expense UI

The Expense detail page exposes workflow actions according to the persisted Expense state.

### DRAFT

Available workflow action:

- Submit Expense

### SUBMITTED

Available workflow actions:

- Approve Expense
- Reject Expense
- Return Expense

### RETURNED

Available workflow action:

- Resubmit Expense

### APPROVED

Available workflow action:

- Close Expense

### REJECTED

No workflow action is displayed.

### CLOSED

No workflow action is displayed.

The UI therefore reflects the approved workflow transition graph rather than exposing arbitrary status manipulation.

The Expense status is displayed as part of the Expense detail view.

---

# 8. Workflow UI and CRUD Separation

The implementation preserves the architectural distinction between ordinary Expense CRUD operations and workflow execution.

Workflow actions are implemented as dedicated operations rather than as ordinary edits to the `status` field.

The UI does not provide a generic mechanism allowing users to select or directly assign arbitrary workflow states.

This preserves the previously approved rule that:

> Expense workflow state is controlled by workflow transitions, not arbitrary CRUD status mutation.

---

# 9. Expense Management Navigation

The Expense Management navigation was updated to expose the two operational areas separately.

The navigation structure is:

```text
Expense Management
├── Expense Classifications
└── Expenses
```

The corresponding endpoints are:

```text
expense.classifications
expense.expenses
```

The parent navigation item remains expanded while viewing either child page, and the active child is highlighted.

This change improves discoverability of the Expense Management operational surface without introducing a new module boundary.

---

# 10. Browser Verification

The complete Expense workflow lifecycle was verified through the browser.

## 10.1 Submission Path

### DRAFT → SUBMITTED

Verified:

- Expense opened in DRAFT state.
- Submit Expense action was visible.
- Submit operation completed successfully.
- No Access Denied response occurred.
- Expense status persisted as `SUBMITTED`.
- Approve, Reject, and Return actions became available.

**Result:** PASS

---

## 10.2 Return Path

### SUBMITTED → RETURNED

Verified:

- Expense was in SUBMITTED state.
- Return Expense action was available.
- Return operation completed successfully.
- Expense status persisted as `RETURNED`.
- Resubmit Expense became the available workflow action.

**Result:** PASS

---

## 10.3 Resubmission Path

### RETURNED → SUBMITTED

Verified:

- Expense was in RETURNED state.
- Resubmit Expense action was available.
- Resubmission completed successfully.
- Expense status persisted as `SUBMITTED`.
- Approve, Reject, and Return actions became available again.

**Result:** PASS

---

## 10.4 Approval Path

### SUBMITTED → APPROVED

Verified:

- Expense was in SUBMITTED state.
- Approve Expense action was available.
- Approval completed successfully.
- Expense status persisted as `APPROVED`.
- Close Expense became available.

**Result:** PASS

---

## 10.5 Closure Path

### APPROVED → CLOSED

Verified:

- Expense was in APPROVED state.
- Close Expense action was available.
- Closure completed successfully.
- Expense status persisted as `CLOSED`.
- No further workflow action was displayed.

**Result:** PASS

---

## 10.6 Rejection Path

### SUBMITTED → REJECTED

A separate rejection branch was verified.

Verified sequence:

```text
DRAFT
  ↓ SUBMIT
SUBMITTED
  ↓ REJECT
REJECTED
```

Verified:

- Submit operation completed successfully.
- Reject Expense action was available from SUBMITTED.
- Rejection completed successfully.
- Expense status persisted as `REJECTED`.
- No further workflow action was displayed.

**Result:** PASS

---

# 11. Complete Browser Lifecycle Verification

The complete verified lifecycle is:

```text
                    ┌───────────────┐
                    │     DRAFT     │
                    └───────┬───────┘
                            │ SUBMIT
                            ▼
                    ┌───────────────┐
                    │   SUBMITTED   │
                    └───┬────┬────┬─┘
              RETURN    │    │    │    REJECT
                        │    │    └──────────► REJECTED
                        │    │
                        │    └ APPROVE ──────► APPROVED
                        │                          │
                        │                          │ CLOSE
                        │                          ▼
                        │                       CLOSED
                        ▼
                  ┌───────────────┐
                  │   RETURNED    │
                  └───────┬───────┘
                          │ RESUBMIT
                          └──────────────► SUBMITTED
```

All valid lifecycle branches were exercised successfully.

---

# 12. Automated Verification

## 12.1 Expense Route Tests

The Expense route test suite was executed after completing the HTTP/UI workflow integration.

Result:

```text
26 passed
```

This verifies the six workflow route integrations together with the existing Expense route behavior.

---

## 12.2 Focused Platform Verification

The focused Expense and enterprise integration verification was executed:

```powershell
pytest -q tests\modules\expense tests\core\startup\test_execution_authorization_composition.py tests\core\execution\test_dispatcher_transaction.py tests\core\platform
```

Result:

```text
340 passed
```

This confirms compatibility across:

- Expense module behavior.
- Expense workflow integration.
- Execution authorization composition.
- Enterprise dispatcher transaction behavior.
- Platform transaction lifecycle behavior.

---

## 12.3 Full Regression Verification

The complete platform test suite was executed:

```powershell
pytest -q
```

Result:

```text
2,569 passed
0 failed
```

The full regression therefore confirms that the Phase 2.2.6 implementation did not introduce regressions into the existing platform.

---

# 13. Architecture Conformance

The Phase 2.2.6 implementation conforms to the approved architecture.

### Enterprise infrastructure reused

The implementation reuses:

- Enterprise workflow definitions.
- Enterprise command framework.
- Enterprise command dispatcher.
- Enterprise execution context.
- Enterprise authorization service.
- Enterprise authorization engine.
- Enterprise permission registry.
- Enterprise transaction boundary.
- Existing RBAC and governance mechanisms.

### Expense-owned responsibilities

Expense Management owns:

- Expense workflow commands.
- Expense workflow handlers.
- Expense workflow service methods.
- Expense workflow definition.
- Expense workflow permissions.
- Expense workflow HTTP integration.
- Expense workflow UI presentation.

### Responsibilities not introduced

Phase 2.2.6 does not introduce:

- A new workflow engine.
- A new authorization engine.
- A new transaction manager.
- An Expense-specific execution framework.
- An `ExpenseApproval` entity.
- Financial transactions.
- Journal entries.
- General ledger entities.
- Payment processing.
- Invoice processing.
- Procurement persistence dependencies.
- Inventory persistence dependencies.
- Catering persistence dependencies.

---

# 14. Security and Governance Conformance

The workflow HTTP layer preserves the approved security model.

Each workflow operation requires:

```text
Authenticated User
        ↓
Workflow Permission
        ↓
ExecutionContext
        ↓
CommandDispatcher
        ↓
Enterprise Authorization
        ↓
Transaction Boundary
        ↓
Expense Handler
        ↓
Expense Service
        ↓
Expense Workflow
```

The implementation therefore maintains the separation between:

- Authentication
- Authorization
- Workflow validity
- Command execution
- Transaction management
- Persistence

No security or governance responsibility has been moved into the Expense workflow handlers.

---

# 15. Implementation Files

The Phase 2.2.6 implementation affected the following primary areas:

```text
app/modules/expense/routes/routes.py
app/modules/expense/security/__init__.py
app/navigation/menu.py
app/seeds/constants.py
app/templates/modules/expense/expenses/view.html
tests/modules/expense/routes/test_expense_routes.py
```

The previously implemented Expense workflow domain components remain under the Expense module, including:

```text
app/modules/expense/workflows/
app/modules/expense/commands/
app/modules/expense/handlers/
app/modules/expense/services/
```

No duplicate workflow infrastructure was created.

---

# 16. Permission Model

The six workflow permissions remain the approved permissions established in Phase 2.2.5.3:

| Operation | Permission |
|---|---|
| `expense.submit` | `EXPENSE.EXPENSE.SUBMIT` |
| `expense.approve` | `EXPENSE.EXPENSE.APPROVE` |
| `expense.reject` | `EXPENSE.EXPENSE.REJECT` |
| `expense.return` | `EXPENSE.EXPENSE.RETURN` |
| `expense.resubmit` | `EXPENSE.EXPENSE.RESUBMIT` |
| `expense.close` | `EXPENSE.EXPENSE.CLOSE` |

The HTTP layer uses these permissions through the established enterprise permission enforcement mechanism.

No new role-specific workflow authority was hard-coded into the routes or handlers.

---

# 17. Verification Summary

| Area | Verification | Result |
|---|---|---|
| Expense workflow routes | Automated route tests | PASS — 26 passed |
| Expense workflow UI | State-driven action verification | PASS |
| CSRF protection | Workflow forms | PASS |
| Authorization context | Authenticated user ID supplied | PASS |
| Submission lifecycle | DRAFT → SUBMITTED | PASS |
| Return lifecycle | SUBMITTED → RETURNED | PASS |
| Resubmission lifecycle | RETURNED → SUBMITTED | PASS |
| Approval lifecycle | SUBMITTED → APPROVED | PASS |
| Closure lifecycle | APPROVED → CLOSED | PASS |
| Rejection lifecycle | SUBMITTED → REJECTED | PASS |
| Navigation | Classifications + Expenses | PASS |
| Focused regression | Expense + execution + platform | PASS — 340 passed |
| Full regression | Entire platform | PASS — 2,569 passed, 0 failed |

---

# 18. Completion Decision

Phase 2.2.6 — **Expense Workflow HTTP/UI Integration and Browser Verification** is hereby recorded as:

**IMPLEMENTED / VERIFIED / COMPLETED**

The Expense workflow is integrated into the HTTP/UI layer and has been verified across all approved workflow branches.

The browser verification confirms that:

- Workflow actions are exposed according to state.
- Workflow transitions execute successfully.
- Authorization is correctly enforced through the enterprise execution path.
- The authenticated user identity is correctly supplied to execution authorization.
- CSRF protection is present.
- Terminal states prevent further workflow actions.
- Workflow state is persisted correctly.
- Expense Management navigation exposes both operational areas.
- No workflow architecture bypasses were introduced.

The full platform regression of **2,569 passed and 0 failed** confirms that the completed stage is compatible with the existing CDCS-EMP platform baseline.

---

# 19. Architectural Stability

This checkpoint does not modify the previously approved Expense workflow architecture.

The following remain locked:

- Six Expense workflow states.
- Six Expense workflow transitions.
- Six workflow operation identities.
- Enterprise authorization ownership.
- Enterprise execution ownership.
- Enterprise transaction ownership.
- Expense workflow service ownership.
- Expense workflow validity ownership.
- No `ExpenseApproval` entity.
- No Finance implementation within Expense Management.
- No direct persistence integration with Procurement, Inventory, Catering, or Finance.
- No new ADR or replacement authorization architecture.

In particular, this checkpoint does **not** introduce ADR-016 or any separate Expense-specific authorization architecture.

---

# 20. Next Stage

This completion checkpoint introduces no change to the approved Phase 2.2 sequencing.

The next Phase 2.2 implementation stage shall be taken from the authoritative Phase 2.2 roadmap and existing approved architecture documentation.

No new business-module scope, workflow scope, or integration dependency is introduced by this checkpoint.

---

# 21. Final Status

**Phase 2.2.6 — Expense Workflow HTTP/UI Integration and Browser Verification**

**Status: IMPLEMENTED / VERIFIED / COMPLETED**

**Automated Verification:** PASS
**Focused Verification:** 340 passed
**Full Regression:** 2,569 passed, 0 failed
**Browser Lifecycle Verification:** PASS — all six approved workflow transitions verified
**Architecture Conformance:** PASS
**Security/Authorization Conformance:** PASS
**UI/Navigation Verification:** PASS

This document serves as the formal implementation and verification checkpoint for Phase 2.2.6.

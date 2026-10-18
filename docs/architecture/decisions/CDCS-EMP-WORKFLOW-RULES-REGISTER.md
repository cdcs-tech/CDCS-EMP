# CDCS-EMP Workflow Rules Register

**Status:** APPROVED
**Scope:** SSRC-IBMS Pilot Catering workflows and cross-module boundaries
**Purpose:** Provide a navigable register of approved workflow rules, implementation behavior, source locations, test evidence, verification status, and unresolved alignment items.

## 1. Purpose and authority

This register consolidates references to workflow rules across CDCS-EMP. It is an index and verification aid; it does not supersede approved architecture decision records, domain baselines, integration contracts, or implementation code.

When sources disagree, record the discrepancy and follow the applicable approved decision or contract. Do not resolve architectural or business-policy conflicts by silently changing this register.

### 1.1 Status labels

- **Verified** — implementation behavior was checked through the stated focused tests or other explicitly identified evidence. This status applies only to the stated scope.
- **Implemented — not independently verified** — implementation or a source reference is known, but adequate focused verification evidence has not been collected.
- **Pending decision** — a business or architectural decision remains unresolved, or the approved baseline and implementation require explicit reconciliation.

### 1.2 Evidence principles

1. Distinguish approved architectural rules from current implementation behavior.
2. Record exact test files and actual test-run results.
3. Do not infer that a workflow is fully verified merely because related tests exist.
4. Do not infer database-level enforcement from an application-level check.
5. Keep unresolved differences visible until an authorized decision is recorded.

## 2. Customer lifecycle and access control

**Status:** Verified — focused Customer service and route suites passed.

### Rules

1. Customer is a Catering-owned business entity.
2. Customer listing and viewing require `CATERING_CUSTOMER_READ`.
3. Customer creation requires `CATERING_CUSTOMER_CREATE`.
4. Customer editing, activation, and deactivation require `CATERING_CUSTOMER_UPDATE`.
5. Customer HTTP routes require authentication.
6. Activation sets Customer status to `ACTIVE`; deactivation sets it to `INACTIVE`.
7. Catering Request forms filter Customer choices to active Customers. This is a form/route behavior; do not assume it proves a universal model-level restriction.
8. Service lifecycle operations and HTTP authorization are separate responsibilities: route permission checks do not mean the service independently enforces the same user permission.

### Source locations

- `app/modules/catering/services/customer.py`
- `app/modules/catering/routes/routes.py`
- `app/modules/catering/forms/`
- `tests/modules/catering/services/test_customer_services.py`
- `tests/modules/catering/routes/test_customer_routes.py`

### Verification evidence

- Customer service and route tests: **23 passed**.
- Coverage includes authentication, permissions, list query options, validation, service delegation, activation, and deactivation.

## 3. Catering Request workflow

**Status:** Verified — Request-to-Event entry-point behavior covered by the Event route and coordination suites. Full Request lifecycle coverage has not been established by this evidence alone.

### Rules

1. A Catering Request records customer demand; it is distinct from a Catering Event.
2. The Event selection page filters Requests to those with status `SUBMITTED`.
3. The Request-to-Event coordination service requires authorization before loading the Request.
4. The service rejects a missing Request and a Request that is not `SUBMITTED`.
5. The service rejects creation when an Event is already found for that Request.
6. Event creation does not mutate the source Request.
7. Route handling covers missing-record, permission, and validation errors.

### Source locations

- `app/modules/catering/services/catering_request_event_coordination.py`
- `app/modules/catering/routes/routes.py`
- `app/modules/catering/repositories/catering_event.py`
- `tests/modules/catering/routes/test_catering_event_routes.py`
- `tests/modules/catering/services/test_catering_request_event_coordination.py`

### Important implementation boundary

The duplicate check is an application-level lookup by Request ID. The inspected evidence does not establish a database uniqueness constraint or concurrency-safe duplicate prevention. Do not describe the rule as database-enforced without separate schema evidence.

### Verification evidence

- Core Event service and route tests: **62 passed**.
- The route suite covers submitted-Request selection, the empty state, service delegation, and selected error handling.
- The coordination suite’s test inventory covers authorization order, eligibility, duplicate detection, and preservation of the source Request.

## 4. Catering Event lifecycle

**Status:** Verified — focused Event service and route suites passed.

### Approved conceptual lifecycle

The B1 baseline defines this Event lifecycle:

`REQUESTED → QUOTED → PENDING_CONFIRMATION → CONFIRMED → PLANNING → READY → IN_PRODUCTION → DELIVERED → COMPLETED`

### Rules

1. Event creation from a Request begins with an Event in `REQUESTED`.
2. The source Request must be `SUBMITTED`.
3. Quotation acceptance and Event progression are separate operations.
4. Event confirmation follows the explicit transition from `QUOTED` to `PENDING_CONFIRMATION`, then from `PENDING_CONFIRMATION` to `CONFIRMED`.
5. Lifecycle operations require an authorization adapter and authorize before workflow transition.
6. Authorization denial must not transition or persist the Event.
7. Workflow rejection must not persist an invalid state.
8. Planning, readiness, production, delivery, and completion use explicit workflow operations rather than unguarded status assignment.
9. The Catering Event service is designed to work with an injected authorization adapter rather than depending directly on Flask’s `current_user`.

### Source locations

- `app/modules/catering/services/catering_event.py`
- `app/modules/catering/services/catering_request_event_coordination.py`
- `app/modules/catering/routes/routes.py`
- `app/modules/catering/models/catering_event.py`
- `tests/modules/catering/services/test_catering_event_service.py`
- `tests/modules/catering/routes/test_catering_event_routes.py`
- `tests/modules/catering/services/test_catering_request_event_coordination.py`
- `tests/modules/catering/services/test_catering_quotation_event_coordination.py`

### Verification evidence

- Core Event service and route tests: **62 passed**.
- Tested areas include authorization ordering, denied operations, workflow failure safety, lifecycle persistence, and the Request-to-Event entry point.

## 5. Event Requirements

**Status:** Verified — focused Event Requirement service and route suites passed. Baseline-to-implementation alignment remains open.

### Rules supported by implementation tests

1. Creating an Event Requirement requires authorization before Event validation and persistence.
2. The associated Event must exist and be `CONFIRMED` for creation.
3. Updates validate the confirmed-Event boundary before writing.
4. Identify, ready, and cancel actions use explicit workflow transitions.
5. Workflow failure must not persist or change the Requirement’s state.
6. Routes include a check that prevents viewing a Requirement through a different Event’s route.
7. Event Requirements belong to Catering and must be associated with an Event.
8. Catering Purchase Requirements are the subset of Event Requirements that need Procurement fulfilment.
9. Catering must not duplicate Procurement’s Purchase Request lifecycle within the Event Requirement workflow.

### Implementation locations

- `app/modules/catering/forms/`
- `app/modules/catering/models/`
- `app/modules/catering/repositories/`
- `app/modules/catering/services/event_requirement.py`
- `app/modules/catering/workflows/`

### Baseline-to-implementation alignment item

The B1 conceptual Requirement lifecycle describes `IDENTIFIED`, `PLANNED`, fulfilment outcomes, and `CANCELLED`. The implementation evidence identifies `DRAFT`, `IDENTIFIED`, and `READY`, with cancellation rules.

**Pending decision:** reconcile the approved conceptual vocabulary with the implemented state model. Until that reconciliation is approved, document the two vocabularies separately. Do not treat them as interchangeable.

### Authoritative reference and tests

- `docs/architecture/decisions/SSRC-IBMS-PILOT-B1-CATERING-DOMAIN-WORKFLOW-DEFINITION.md`
- `tests/modules/catering/services/test_event_requirement_service.py`
- `tests/modules/catering/routes/test_event_requirement_routes.py`

### Verification evidence

- Event Requirement service and route tests: **24 passed**.
- Tested areas include authorization, confirmed-Event constraints, lifecycle transitions, failure safety, and route-level Event ownership checks.

## 6. Quotation lifecycle and Event coordination

**Status:** Verified — focused Quotation service, coordination, and route suites passed.

### Rules

1. Quotation is a Catering-owned business concept.
2. Quotation creation validates the draft, customer, associated Event, customer/Event consistency, validity-date input, line items, quantities, unit prices, and descriptions.
3. Derived line totals, subtotal, and total are calculated by the service; caller-supplied derived totals are not authoritative.
4. Issue, accept, decline, and expire are explicit lifecycle operations with authorization and workflow validation.
5. Acceptance is not itself an Event-coordination operation.
6. Progressing an Event from an accepted Quotation requires a separate coordination service.
7. Coordination validates that the Quotation exists, is `ACCEPTED`, references the loaded Event consistently, has the same Customer as that Event, and that the Event is `REQUESTED`.
8. Coordination authorizes before accessing or mutating entities.
9. The Event transition is performed through the Event workflow; coordination does not re-accept or mutate the Quotation.
10. Failed preconditions or workflow rejection must not persist the Event transition.

### Expiry behavior and policy

**Verified implementation fact:** the tested expiry operation does not automatically depend on `valid_until`.

**Policy recommendation:** retain this current behavior as an implementation fact. If automatic or date-driven expiry is required, record that as a separate policy decision before changing behavior.

### Source locations

- `app/modules/catering/services/catering_quotation.py`
- `app/modules/catering/services/catering_event.py`
- `app/modules/catering/routes/routes.py`
- `tests/modules/catering/services/test_catering_quotation_service.py`
- `tests/modules/catering/services/test_catering_quotation_event_coordination.py`
- `tests/modules/catering/routes/test_quotation_routes.py`
- `docs/architecture/decisions/SSRC-IBMS-PILOT-B1-CATERING-DOMAIN-WORKFLOW-DEFINITION.md`

### Verification evidence

- Quotation service, coordination, and route tests: **67 passed**.
- Tested areas include validation, lifecycle operations, Event/customer consistency, authorization, separate Event coordination, and Event confirmation routes.

## 7. Catering-to-Procurement handoff

**Status:** Verified — focused handoff suite passed.

### Rules

1. Catering owns Event Requirements and Catering Purchase Requirements.
2. Procurement owns Procurement Purchase Requirements, Purchase Requests, Purchase Orders, sourcing, approvals, and subsequent procurement transactions.
3. A handoff requires an existing Catering Purchase Requirement and its Event Requirement.
4. The fulfilment classification must be `PROCUREMENT`.
5. The associated Event must satisfy the confirmed-Event boundary.
6. Authorization is checked before source validation.
7. A matching existing Procurement Requirement may be reused; conflicting registrations or references are rejected.
8. The handoff uses the dedicated `CATERING.CATERING_PURCHASE_REQUIREMENT.SUBMIT_TO_PROCUREMENT` permission.
9. The handoff does not create downstream Procurement lifecycle records.
10. The expected traceability chain is:

   `Catering Event → Event Requirement → Catering Purchase Requirement → Procurement Purchase Requirement`

11. The deterministic Procurement reference is `CATERING-PR-<CateringPurchaseRequirement.guid>`. Conflicting source metadata must be rejected.
12. `procurement_reference` is a reference value, not a foreign-key relationship; the integration must not add duplicate downstream lifecycle status fields to Catering.

### Catering Purchase Requirement implementation locations

- `app/modules/procurement/forms/`
- `app/modules/procurement/models/`
- `app/modules/procurement/repositories/`
- `app/modules/procurement/services/`

### Handoff implementation and tests

- `app/modules/catering/` — Catering-side handoff implementation
- `tests/modules/catering/services/test_procurement_handoff.py`
- `docs/architecture/decisions/SSRC-IBMS-PILOT-B1-CATERING-DOMAIN-WORKFLOW-DEFINITION.md`
- `docs/architecture/decisions/PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`
- `docs/architecture/decisions/PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

### Verification evidence

- Procurement handoff tests: **15 passed**.
- Tested areas include eligibility, authorization, matching registration reuse, conflict rejection, and the boundary against creating downstream Procurement records.

## 8. Catering-to-Inventory boundary

**Status:** Verified — limited to the tested Stock Movement and Stock Transfer workflow enforcement.

### Rules

1. Inventory owns physical stock effects, including stock balances, movements, receipts, and transfers.
2. Catering requirements express business needs; they do not replace Inventory stock transactions.
3. Stock Movement and Stock Transfer operations must follow their explicit workflows.
4. Invalid workflow transitions must be rejected.
5. Catering must not directly mutate Inventory balances, movements, or transfers to bypass Inventory ownership and transaction controls.
6. Receipt idempotency and other Inventory transaction rules must be cited to their own implementation and test evidence rather than inferred from movement/transfer transition tests.

### Source locations

- `app/modules/catering/` — Catering-side requirement and fulfilment integration
- Inventory module model, service, and repository implementation
- `tests/modules/catering/services/test_inventory_workflow_enforcement.py`
- `tests/modules/procurement/integration/test_inventory_receipt_idempotency.py`
- `docs/architecture/decisions/ADR-008-catering-inventory-domain-boundary.md`
- `docs/architecture/decisions/ADR-012-inventory-stock-movement-ledger-architecture.md`
- `docs/architecture/decisions/ADR-013-inventory-stock-transfer-architecture.md`
- `docs/architecture/decisions/ADR-015-inventory-transaction-posting-boundary.md`
- `docs/architecture/decisions/PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`

### Verification evidence

- Inventory workflow enforcement tests: **4 passed**.
- Scope: Stock Movement and Stock Transfer workflow transitions only.

## 9. Catering-to-Expense cost association and consumption

**Status:** Verified — focused association and consumption suites passed.

### Rules

1. Expense Management owns Expense records, classifications, and Expense lifecycle.
2. Catering’s cost-association capability links a Catering cost context to an Expense-related reference without taking ownership of the Expense lifecycle.
3. Association creation requires authorization before persistence.
4. Denied association creation must not persist.
5. Creating an association does not itself consume the association or require an Expense lookup.
6. Consumption requires an eligible association.
7. Repeated consumption of an already-consumed association is idempotent.
8. Unknown association statuses are rejected.
9. The consumption service does not directly access the Expense record.

### Source locations

- `app/modules/catering/` — cost association and cost consumption services
- `tests/modules/catering/services/test_expense_cost_association_service.py`
- `tests/modules/catering/services/test_expense_cost_consumption_service.py`
- `docs/architecture/decisions/PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`
- `docs/architecture/decisions/PHASE-2.2.6-EXPENSE-WORKFLOW-HTTP-UI-INTEGRATION-AND-BROWSER-VERIFICATION.md`

### Verification evidence

- Expense association and consumption tests: **14 passed**.
- Scope: authorization, persistence safety, eligibility, idempotency, status rejection, and module separation.

## 10. Finance and reporting boundaries

**Status:** Contract-defined boundaries; full Finance integration is not verified by the focused test runs recorded in this register.

### Rules

1. Finance owns financial transactions and future ledger capabilities.
2. Catering’s financial context and revenue/costing capabilities must not be represented as a full accounting or ERP Finance subsystem.
3. Procurement–Finance integration must follow its approved integration contract, including its commitment registration and idempotency rules.
4. Reporting owns reporting infrastructure and read models; reporting views should not become alternate owners of operational transactions.
5. Catering profitability or revenue reporting must use approved financial and operational sources rather than bypassing their ownership boundaries.

### Source locations

- `docs/architecture/decisions/PHASE-2.2-PROCUREMENT-FINANCE-INTEGRATION-CONTRACT.md`
- `docs/architecture/decisions/PHASE-4-CATERING-REVENUE-CAPABILITY.md`
- `docs/architecture/decisions/PHASE-4-FOCUSED-FINANCE-DOMAIN-AND-CONTRACT.md`
- `docs/architecture/decisions/PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

### Verification note

The focused test runs recorded above do not constitute verification of the full Finance integration, ledger behavior, revenue recognition, or reporting read models. Those require their own scoped evidence.

## 11. Cross-cutting authorization, validation, and integrity rules

**Status:** Verified where explicitly covered by the focused suites; other controls require their own evidence.

1. Services that require authorization must fail closed when their authorization adapter is missing.
2. Authorization must occur before protected repository writes or workflow transitions where covered by the relevant service contract.
3. Authorization denial must not result in unintended writes or lifecycle changes.
4. Workflow operations must use explicit workflow transitions and reject invalid transitions.
5. Validation must precede persistence for the applicable business constraints.
6. Cross-entity relationships must be checked before coordination or persistence. Examples include Request-to-Event, Quotation-to-Event, Customer-to-Event, and Event Requirement-to-Event relationships.
7. An application-level lookup is not equivalent to a database uniqueness constraint.
8. Cross-module references must not silently transfer ownership of a record or its lifecycle.
9. Do not infer that all operations require a generic update permission. Record the specific permission and operation defined by the relevant contract and tests.

## 12. Focused verification ledger

These results were reported from the focused test runs in this review. They are not a full-project regression result.

| Workflow area | Test files | Result |
|---|---|---:|
| Customer | `test_customer_services.py`; `test_customer_routes.py` | 23 passed |
| Catering Event | `test_catering_event_service.py`; `test_catering_event_routes.py` | 62 passed |
| Event Requirement | `test_event_requirement_service.py`; `test_event_requirement_routes.py` | 24 passed |
| Quotation and Event coordination | `test_catering_quotation_service.py`; `test_catering_quotation_event_coordination.py`; `test_quotation_routes.py` | 67 passed |
| Catering → Procurement | `test_procurement_handoff.py` | 15 passed |
| Inventory workflow enforcement | `test_inventory_workflow_enforcement.py` | 4 passed |
| Expense cost association and consumption | `test_expense_cost_association_service.py`; `test_expense_cost_consumption_service.py` | 14 passed |
| **Total** | **7 focused runs** | **209 passed** |

**Evidence limitation:** these totals reflect the reported focused runs only. They do not certify unrelated routes, every integration path, browser UAT, the full test suite, or production deployment readiness.

## 13. Pending decisions and follow-up evidence

| ID | Item | Status | Required treatment |
|---|---|---|---|
| WR-01 | Event Requirement conceptual lifecycle vs implemented lifecycle | Pending decision | Reconcile the B1 vocabulary and implementation state model through an approved decision. |
| WR-02 | Automatic or date-driven Quotation expiry policy | Pending policy decision only if required by the business | Current implementation behavior is verified: expiry does not automatically depend on `valid_until`. Decide separately whether a scheduled or date-driven policy is required. |
| WR-03 | Request-to-Event duplicate prevention under concurrency | Implemented — not independently verified at database level | Confirm whether a database uniqueness constraint or transaction-safe strategy is required. |
| WR-04 | Full Finance, revenue, and reporting workflow verification | Implemented/contract-defined boundaries; not independently verified here | Add focused implementation and test evidence before marking these workflows verified. |
| WR-05 | Browser UAT and workshop execution evidence | Separate evidence stream | Keep workshop scenario and execution log separate; do not overwrite them with this register. |

## 14. Change history

| Version | Date | Change |
|---|---|---|
| Draft 0.1 | 13 October 2026 | Initial register compiled from the approved B1 baseline, relevant architecture/integration contracts, confirmed source locations, and seven reported focused test runs totalling 209 passed. |
| Version 1.0 | 13 October 2026 | Approved register. Confirmed exact Catering Event, Event Requirement, and Quotation service paths; documented Event Requirement and Catering Purchase Requirement implementation directories; clarified the current Quotation expiry behavior and separated any future automatic-expiry policy question. |

## 15. Maintenance rules

1. Update this register when a workflow contract, implementation, or verification result materially changes.
2. Cite the authoritative decision or integration contract for every significant ownership or lifecycle rule.
3. Add test paths and actual results; do not mark a rule verified based only on test names.
4. Keep pending decisions visible until the decision is documented and approved.
5. Do not duplicate full architecture contracts or implementation specifications here.
6. Preserve workshop UAT scenario and execution-log documents as separate artifacts.

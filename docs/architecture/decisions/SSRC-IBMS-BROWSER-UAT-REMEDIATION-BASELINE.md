# SSRC-IBMS Browser UAT Remediation Baseline

**Project:** CDCS-EMP / SSRC Integrated Business Management System (SSRC-IBMS)
**Roadmap:** `SSRC-IBMS-PILOT-READINESS-IMPLEMENTATION-ROADMAP-V1.md`
**Phase:** SSRC Pilot Browser UAT
**Relationship:** Post-C6 Technical Acceptance / Pre-Gate 6 Remediation Baseline
**Status:** **APPROVED / ACTIVE**
**Application-Code Changes:** None authorized by this baseline alone
**Acceptance Position:** Browser UAT remediation implementation R01–R12 committed; controlled-data browser re-UAT and Gate 6 acceptance remain pending

---

## 1. Purpose

This decision record formally establishes the **SSRC-IBMS Browser UAT Remediation Baseline** following completion of the initial browser-based pilot usability and workflow verification.

The purpose of this baseline is to:

- preserve the browser UAT findings as an authoritative implementation reference;
- distinguish existing backend capability from actual browser-accessible pilot capability;
- identify genuine application defects separately from missing or incomplete UI surfaces;
- establish the priority and sequence for pilot-critical remediation;
- preserve the established CDCS-EMP module ownership boundaries;
- prevent premature implementation of capabilities that are already architecturally established;
- define the conditions for browser re-UAT following remediation; and
- provide a controlled bridge between **C6 Technical Acceptance** and **Gate 6 — SSRC Acceptance Ready**.

This record is authoritative for the **Browser UAT remediation queue**. It does not replace the pilot readiness roadmap, the C6 completion decision record, or the underlying module architecture.

---

## 2. Relationship to C6 Technical Acceptance

C6 — End-to-End Business Integration was technically completed and accepted through a real end-to-end pilot business-flow test.

The validated business flow was:

```text
Customer
   ↓
Catering Event
   ↓
Quotation
   ↓
Event Requirements
   ↓
Catering Purchase Requirement
   ↓
Procurement Purchase Request
   ↓
Purchase Order
   ↓
Procurement Receiving
   ↓
Inventory Receipt / Stock Movement
   ↓
Stock Balance
   ↓
Production / Delivery
   ↓
Catering Revenue
   ↓
Finance Revenue Record
   ↓
Approved Expense
   ↓
Catering Cost Association / Consumption
   ↓
Event Profitability
```

C6 technical acceptance demonstrated that the established backend capabilities can compose into the complete pilot business flow without violating module ownership boundaries.

The C6 technical acceptance evidence included:

- full pilot end-to-end scenario: **1 passed**;
- C6 integration regression: **194 passed**;
- full project regression: **3,113 passed**;
- `git diff --check`: clean;
- Git checkpoint: `94398da`;
- working tree clean.

C6 technical acceptance therefore remains complete.

However, the browser UAT demonstrated that several parts of the validated backend business flow are not yet exposed as usable browser workflows.

Accordingly:

> **C6 Technical Acceptance is complete, but browser-level pilot acceptance remains pending.**

---

## 3. Browser UAT Objective

The Browser UAT phase is intended to establish whether the SSRC pilot can be operated through the actual application interface using realistic user workflows.

Browser UAT therefore evaluates more than backend existence.

For each pilot-critical capability, the assessment considers:

1. whether the capability exists in the backend;
2. whether a browser route or user-accessible surface exists;
3. whether the workflow is discoverable;
4. whether the required action can actually be executed;
5. whether the browser operation completes successfully;
6. whether the resulting state is visible and understandable to the user; and
7. whether the workflow respects established module ownership.

A backend capability that cannot be reached or completed through the browser is not considered browser-ready merely because its service, handler, or integration test exists.

---

## 4. UAT Evidence and Limitations

The initial Browser UAT was conducted against the current application routes, navigation, templates, and available browser workflows.

The UAT established that the application already exposes usable browser surfaces for substantial parts of:

- Dashboard;
- Catering master-data/inventory functions;
- Procurement Purchase Requirements;
- Procurement Purchase Requests;
- Procurement Purchase Orders;
- Expense Classifications;
- Expense creation and management;
- Expense submission and approval actions.

The UAT also established that several pilot-critical commercial, operational, and financial capabilities validated at backend level are not currently exposed through complete browser workflows.

This baseline therefore distinguishes:

### 4.1 Confirmed Browser Pass

A capability is a browser pass where the required user-facing workflow was available and successfully usable during UAT.

### 4.2 UI Gap

A UI gap exists where backend capability is established but the required browser entry point, action, workflow, or visibility is missing or incomplete.

### 4.3 Runtime Defect

A runtime defect exists where the required browser action is exposed but execution fails because of an application/runtime problem.

### 4.4 Deferred Capability

A capability is deferred where it is intentionally outside the current pilot scope or is reserved for a later roadmap stage.

---

# 5. Browser UAT Remediation Findings

The following findings constitute the approved Browser UAT remediation queue.

---

## UAT-R01 — Customer Management / Customer Entry

**Priority:** Pilot-Critical
**Wave:** 1 — Commercial Entry
**Current Browser Position:** Not available through the Catering user interface
**Backend Position:** Customer capability exists and was validated through C6
**Classification:** UI / workflow surface gap

### Finding

The browser interface does not currently expose a usable Customer management or Customer entry workflow.

The validated C6 business flow nevertheless depends upon a Catering-owned Customer as the starting point for the commercial process.

### Required Remediation

Expose the existing Customer capability through an appropriate Catering browser workflow.

The remediation should provide the minimum pilot-required capability to:

- access Customers;
- create a Customer where required;
- view Customer information;
- select an existing Customer when initiating a Catering business transaction.

### Architectural Constraint

Customer remains a **Catering-owned business concept**.

No duplicate Customer ownership should be introduced into Procurement, Expense, Finance, or Inventory.

---

## UAT-R02 — Catering Request / Event Entry

**Priority:** Pilot-Critical
**Wave:** 1 — Commercial Entry
**Current Browser Position:** Not available
**Backend Position:** Existing Catering Request/Event capability validated
**Classification:** UI / workflow surface gap

### Finding

The browser interface does not expose the Catering Request and Event workflow required to initiate and manage the commercial lifecycle.

The backend already contains the relevant Catering domain capability.

### Required Remediation

Expose the existing Catering Request/Event workflow through a user-accessible browser surface.

The workflow should allow the pilot user to:

- initiate a Catering request;
- identify the customer;
- create/access the associated event;
- view the event;
- progress the event through supported workflow operations.

### Architectural Constraint

Catering remains authoritative for:

- Customer;
- Catering Request;
- Catering Event;
- event lifecycle.

No separate operational event ownership should be introduced into Procurement, Inventory, Expense, or Finance.

---

## UAT-R03 — Quotation

**Priority:** Pilot-Critical
**Wave:** 1 — Commercial Entry
**Current Browser Position:** Not available
**Backend Position:** Existing quotation capability validated
**Classification:** UI / workflow surface gap

### Finding

The browser interface does not currently expose the quotation workflow required to support the validated commercial flow.

### Required Remediation

Expose the existing Catering quotation capability sufficiently for pilot operation, including:

- quotation access;
- quotation creation where applicable;
- quotation viewing;
- quotation association with the appropriate Catering Event;
- quotation acceptance/confirmation entry where required by the workflow.

### Architectural Constraint

Quotation remains a **Catering-owned business concept**.

Do not introduce quotation ownership into Finance or Procurement.

---

## UAT-R04 — Quotation Confirmation / Event Progression

**Priority:** Pilot-Critical
**Wave:** 1 — Commercial Entry
**Current Browser Position:** Not available because Event/Quotation UI is absent
**Backend Position:** Existing event and quotation coordination capability validated
**Classification:** UI / workflow surface gap

### Finding

The existing backend supports quotation-to-event coordination and event lifecycle progression, but the browser does not expose the required workflow.

Existing validated services include the quotation/event coordination required to move an event through the established lifecycle.

### Required Remediation

Expose the existing workflow through the browser rather than creating a new parallel lifecycle.

The pilot user must be able to discover and execute the supported confirmation/progression actions necessary to move the event from quotation through the established operational states.

### Architectural Constraint

The established Catering Event lifecycle remains authoritative:

```text
REQUESTED
   ↓
QUOTED
   ↓
PENDING_CONFIRMATION
   ↓
CONFIRMED
   ↓
PLANNING
   ↓
READY
   ↓
IN_PRODUCTION
   ↓
DELIVERED
   ↓
COMPLETED
```

No separate Production or Delivery workflow should be created merely to satisfy browser UAT.

---

## UAT-R05 — Event Requirements

**Priority:** Pilot-Critical
**Wave:** 1 — Commercial Entry
**Current Browser Position:** Not available
**Backend Position:** Existing Event Requirement / Catering Purchase Requirement capability validated
**Classification:** UI / workflow surface gap

### Finding

The browser does not currently expose Event Requirements or the Catering-side requirements workflow.

### Required Remediation

Expose the existing requirement workflow sufficiently for pilot operation, including:

- viewing Event Requirements;
- creating or maintaining requirements where supported;
- distinguishing Event Requirements from Catering Purchase Requirements;
- making the requirements available for procurement handoff.

### Architectural Constraint

Catering owns:

- Event Requirement;
- Catering Purchase Requirement.

Procurement owns the subsequent procurement lifecycle.

The remediation must not collapse these concepts into a single procurement-owned object.

---

## UAT-R06 — Purchase Order Approval

**Priority:** Pilot-Critical
**Wave:** 2 — Procurement
**Current Browser Position:** Purchase Order CRUD available; browser approval action missing
**Backend Position:** Approval capability exists
**Classification:** UI workflow gap

### Finding

Purchase Orders can be created, viewed, and edited through the browser.

However, the browser does not expose the required Approve action.

Backend capability already exists through the established command/service/handler path, including the required `approved_at` behavior.

### Required Remediation

Expose the existing Purchase Order approval operation through the browser.

The browser workflow must:

- make approval discoverable to authorized users;
- execute the existing approval command;
- display the resulting status;
- preserve the existing approval timestamp;
- respect existing authorization and execution boundaries.

### Architectural Constraint

Do not introduce a browser-only approval mechanism that bypasses the enterprise execution framework.

---

## UAT-R07 — Procurement Receiving

**Priority:** Pilot-Critical
**Wave:** 2 — Procurement
**Current Browser Position:** Generic Stock Movement UI exists; complete procurement receiving workflow is not exposed
**Backend Position:** C6.4 Procurement Receiving → Inventory Receipt integration validated
**Classification:** UI / business workflow gap

### Finding

The browser exposes generic Stock Movement functionality and allows the user to select a receipt movement type.

However, UAT did not establish a complete procurement receiving workflow linked to a Purchase Order.

The generic Stock Movement form does not constitute the complete pilot Procurement Receiving business process.

### Required Remediation

Expose the established Procurement Receiving workflow in a way that allows an authorized user to:

1. identify the Purchase Order;
2. initiate receiving against the appropriate PO;
3. provide the required receiving information;
4. execute the established receiving integration;
5. create the Inventory receipt effect;
6. expose the resulting stock movement/balance state.

### Architectural Constraint

The remediation target is **Procurement Receiving**, not an increasingly elaborate generic Stock Movement form.

Ownership remains:

- Procurement — receiving business workflow;
- Inventory — physical stock receipt, movement, balance, and idempotency effects.

Do not duplicate Inventory stock ownership inside Procurement.

---

## UAT-R08 — Production / Delivery

**Priority:** Pilot-Critical
**Wave:** 3 — Operational
**Current Browser Position:** No dedicated production/delivery workflow visible
**Backend Position:** Existing Catering Event lifecycle represents production/delivery states
**Classification:** UI / workflow surface gap

### Finding

The browser does not expose the Catering Event lifecycle states necessary to represent the production and delivery portion of the pilot flow.

No separate Production/Delivery module is required by the current architecture.

### Required Remediation

Expose the existing Catering Event lifecycle operations and state visibility needed for pilot operation.

### Architectural Constraint

Production and Delivery remain represented through the **Catering Event lifecycle**.

Do not create a new Production module merely to create a browser route.

---

## UAT-R09 — Catering Revenue

**Priority:** Pilot-Critical
**Wave:** 4 — Financial
**Current Browser Position:** No revenue workflow visible
**Backend Position:** C5/C6 Catering Revenue capability validated
**Classification:** UI / business workflow gap

### Finding

The browser does not currently expose the Catering revenue workflow.

The backend already supports the established Catering Revenue → Finance integration.

### Required Remediation

Expose the existing Catering revenue capability through an appropriate user-facing workflow.

The browser should provide the pilot-required ability to:

- access the Catering revenue transaction;
- view its relevant business context;
- execute the supported revenue recognition workflow where required;
- make the resulting financial integration state understandable.

### Architectural Constraint

Catering remains authoritative for the **revenue fact**.

Finance remains authoritative for the resulting **financial record**.

The remediation must not duplicate revenue ownership or introduce direct cross-module persistence outside the established integration contract.

No invoice, payment, receipt, or full accounting subsystem is authorized merely by this finding.

---

## UAT-R10 — Expense Approval Runtime Transaction Defect

**Priority:** Pilot-Critical
**Wave:** 4 — Financial
**Current Browser Position:** Approve action visible; execution fails
**Backend Position:** Expense approval capability exists
**Classification:** Genuine runtime application defect

### Finding

The Expense browser exposes the approval action, but approval execution fails with:

```text
RuntimeError: A SQLAlchemy transaction is already active.
```

The failure is associated with the shared enterprise transaction boundary rather than with an Expense-specific approval rule.

The relevant execution architecture establishes that:

- `CommandDispatcher` owns the configured transaction boundary;
- `ExecutionTransactionBoundary` delegates to the transaction manager;
- `SQLAlchemyTransactionManager` adopts incidental SQLAlchemy AUTOBEGIN transactions;
- explicitly active non-AUTOBEGIN transactions are rejected.

The current failure therefore requires validation of transaction ownership and application wiring before any Expense-specific workaround is introduced.

### Required Remediation

Investigate and correct the shared transaction ownership/wiring model so that browser command execution can enter the enterprise transaction boundary correctly.

The remediation must preserve:

- dispatcher transaction ownership;
- repository non-commit behavior;
- post-commit execution semantics;
- rollback behavior;
- authorization-before-handler execution;
- consistent transaction semantics across modules.

### Architectural Constraint

Do **not** add an Expense-specific commit, rollback, `session.begin()`, or transaction workaround merely to make the browser action pass.

This is a shared execution-framework concern and must be resolved at the correct architectural boundary.

---

## UAT-R11 — Catering Cost Integration

**Priority:** Pilot-Critical
**Wave:** 4 — Financial
**Current Browser Position:** Expense workflow exists; Catering cost association/consumption is not visible
**Backend Position:** C4 capability validated
**Classification:** UI / business workflow surface gap

### Finding

Expense creation, viewing, submission, and approval are available through the browser.

However, the browser does not expose the Catering-side cost association/consumption workflow required to connect approved expenses to the relevant Catering Event.

The C4 backend capability already establishes the required integration behavior.

### Required Remediation

Expose the existing Catering cost association/consumption capability sufficiently for pilot operation.

The browser should allow the appropriate user to understand:

- which approved Expense is associated with the event;
- the relevant Catering Event context;
- whether the contribution is eligible or consumed;
- the resulting cost contribution.

### Architectural Constraint

Ownership remains:

- Expense — Expense record and lifecycle;
- Catering — association and consumption state;
- Finance — financial record where applicable.

Do not introduce a direct Expense → Catering foreign-key ownership model merely to support the UI.

Do not introduce profitability, allocation, costing, or accounting logic into the remediation.

---

## UAT-R12 — Event Profitability

**Priority:** Pilot-Critical
**Wave:** 4 — Financial
**Current Browser Position:** No profitability page or workflow visible
**Backend Position:** Existing read-only `EventProfitabilityService` validated in C6.7
**Classification:** UI / read-model surface gap

### Finding

The backend already provides read-only event profitability composition using the established revenue and consumed-cost capabilities.

The browser currently provides no user-facing profitability view.

### Required Remediation

Expose the existing profitability capability through an appropriate read-only browser surface.

The browser view should present, at minimum, the pilot-required:

- event;
- recognized revenue;
- consumed costs;
- total cost;
- resulting profit.

### Architectural Constraint

The existing `EventProfitabilityService` remains authoritative for the current pilot profitability composition.

Do not create:

- a second profitability calculation;
- a duplicate accounting ledger;
- a new Finance profitability ownership model;
- persistent profitability facts where a read-only composition is sufficient.

The reporting framework may be used later where appropriate, but this remediation does not require creation of a new reporting architecture.

---

# 6. Confirmed Browser Pass Areas

The following capabilities were successfully established during Browser UAT and are **not** remediation targets unless a later test identifies a new defect.

## 6.1 Dashboard

The Dashboard is browser-accessible.

## 6.2 Catering Entry and Existing Master-Data / Inventory Surface

The Catering area is accessible.

The following existing browser areas were confirmed:

- Categories;
- Products;
- Inventory.

## 6.3 Procurement

The following Procurement workflows were confirmed as browser-accessible:

- Purchase Requirements;
- Purchase Requests;
- Purchase Orders.

Purchase Requirement, Purchase Request, and Purchase Order CRUD therefore remain outside the current remediation queue.

## 6.4 Expense Management

The following Expense capabilities were confirmed:

- Expense Classifications;
- Expense creation;
- Expense viewing;
- Expense editing;
- Expense submission;
- Expense approval action visibility.

Expense approval execution remains in UAT-R10 because the exposed approval action currently fails at runtime.

## 6.5 Navigation

The browser navigation exposes:

- Dashboard;
- Catering;
- Procurement;
- Expense Management;
- Finance as a future/deferred area.

The absence of a Finance implementation area is not itself a defect because the current remediation target is the specific pilot-required Finance integration surface rather than a full Finance module.

---

# 7. Remediation Priority and Implementation Waves

The approved remediation sequence is:

```text
Wave 1 — Commercial Entry
    R01 Customer
      ↓
    R02 Catering Request / Event
      ↓
    R03 Quotation
      ↓
    R04 Confirmation / Event Progression
      ↓
    R05 Event Requirements

Wave 2 — Procurement
    R06 Purchase Order Approval
      ↓
    R07 Procurement Receiving

Wave 3 — Operational
    R08 Production / Delivery

Wave 4 — Financial
    R09 Catering Revenue
      ↓
    R10 Expense Approval Runtime Defect
      ↓
    R11 Catering Cost Integration
      ↓
    R12 Event Profitability
```

This order is intentional.

The commercial workflow must be made usable before downstream procurement and financial workflows can be meaningfully exercised by a browser user.

---

# 8. Ownership Boundaries

All remediation work must preserve the established CDCS-EMP ownership model.

| Capability | Authoritative Owner |
|---|---|
| Customer | Catering |
| Catering Request | Catering |
| Catering Event | Catering |
| Quotation | Catering |
| Event Requirement | Catering |
| Catering Purchase Requirement | Catering |
| Purchase Requirement | Procurement |
| Purchase Request | Procurement |
| Purchase Order | Procurement |
| Purchase Order Approval | Procurement |
| Procurement Receiving | Procurement |
| Stock Item | Inventory |
| Inventory Location | Inventory |
| Stock Movement | Inventory |
| Stock Balance | Inventory |
| Production / Delivery state | Catering Event lifecycle |
| Catering Revenue Fact | Catering |
| Finance Revenue Record | Finance |
| Expense Record | Expense |
| Catering Expense Association / Consumption | Catering |
| Event Profitability Composition | Catering/read-only service using established module capabilities |

The remediation baseline does not authorize ownership transfers.

---

# 9. Explicit Architectural Protections

The following protections are mandatory throughout remediation.

## 9.1 No Duplicate Business Ownership

Existing business concepts must not be recreated in another module simply because their current browser surface is missing.

## 9.2 No Cross-Module Repository Coupling

Module integrations must continue to use established contracts, services, providers, and execution mechanisms.

## 9.3 No Browser-Only Business Logic

Browser routes should compose existing business capabilities rather than implement parallel business rules.

## 9.4 No Premature ERP Expansion

This baseline does not authorize creation of:

- a full accounting ledger;
- a full invoicing system;
- payment processing;
- a standalone Production module;
- a standalone Delivery module;
- a new Inventory ownership model;
- a new profitability persistence model;
- a replacement reporting framework.

## 9.5 Preserve Enterprise Execution

Where an existing command/handler/dispatcher/execution framework is established, browser actions must use that architecture rather than bypassing it.

## 9.6 Transaction Ownership Must Remain Centralized

UAT-R10 must be resolved at the correct shared transaction boundary.

No module-specific transaction workaround should be introduced until the transaction ownership model has been validated.

---

# 10. What This Baseline Does Not Mean

Approval of this baseline does **not** mean that all twelve remediation items should be implemented immediately or blindly.

Each item remains subject to the controlled CDCS-EMP workflow:

```text
Identify exact remediation item
        ↓
Inspect only the required existing capability
        ↓
Confirm smallest correct implementation
        ↓
Implement one focused change
        ↓
Run targeted tests
        ↓
Run relevant regression
        ↓
Browser verify
        ↓
Document result
        ↓
Git checkpoint
```

A remediation item may be reclassified if focused inspection establishes that:

- the capability is already browser-accessible;
- the requirement is intentionally outside pilot scope;
- the problem is configuration rather than application code;
- the problem is shared infrastructure rather than a module defect; or
- the existing architecture requires a different implementation boundary.

---

# 11. Remediation Acceptance Principles

A remediation item is considered complete only when the relevant browser workflow is demonstrably usable and the implementation remains architecturally compliant.

Acceptance should establish, where applicable:

1. authorized user can discover the workflow;
2. required browser action is available;
3. authorization is enforced;
4. command/service execution uses the established architecture;
5. business state changes correctly;
6. resulting state is visible;
7. integration effects occur exactly once where idempotency applies;
8. ownership boundaries remain intact;
9. targeted automated tests pass;
10. relevant regression passes;
11. browser verification succeeds.

Backend test success alone is insufficient for browser remediation closure.

---

# 12. Browser Re-UAT Requirements

After remediation, Browser UAT must be repeated against the pilot-critical business flow.

At minimum, re-UAT must verify:

```text
Customer
   ↓
Catering Request
   ↓
Catering Event
   ↓
Quotation
   ↓
Quotation Confirmation
   ↓
Event Requirements
   ↓
Catering Purchase Requirement
   ↓
Procurement Purchase Requirement
   ↓
Purchase Request
   ↓
Purchase Order
   ↓
Purchase Order Approval
   ↓
Procurement Receiving
   ↓
Inventory Receipt / Stock Movement
   ↓
Stock Balance
   ↓
Production / Delivery Event State
   ↓
Catering Revenue
   ↓
Finance Revenue Record
   ↓
Approved Expense
   ↓
Catering Cost Association / Consumption
   ↓
Event Profitability
```

The browser re-UAT must verify not only navigation but actual execution and resulting state.

---

# 13. Gate 6 Position

This baseline does **not** claim:

> **Gate 6 — SSRC Acceptance Ready**

Gate 6 remains pending.

The current position is:

| Milestone | Position |
|---|---|
| C6 technical acceptance | **Complete** |
| Initial browser UAT inventory | **Complete** |
| Browser UAT remediation baseline | **Approved / Active** |
| Pilot-critical browser remediation | **Pending** |
| Browser re-UAT | **Pending** |
| Configuration readiness | Pending final validation |
| Users / permissions readiness | Pending final validation |
| Master-data readiness | Pending final validation |
| End-to-end browser scenario | Pending remediation and re-UAT |
| Gate 6 — SSRC Acceptance Ready | **Not yet achieved** |
| Final SSRC pilot acceptance | **Not claimed** |

---

# 14. Relationship to Stream D

The remediation queue is limited to pilot-critical browser capability and identified application/runtime defects.

Capabilities intentionally reserved for later roadmap work remain deferred.

Stream D or subsequent phases may address broader:

- reporting;
- dashboards;
- KPI presentation;
- management reporting;
- expanded Finance;
- broader operational capabilities;
- non-pilot workflow enhancements;
- additional usability improvements.

Such future work must not be pulled into the current remediation effort merely because a related concept is visible during UAT.

---

# 15. Approval Decision

The **SSRC-IBMS Browser UAT Remediation Baseline** is hereby established as:

> **APPROVED / ACTIVE**

The baseline is the authoritative reference for the Browser UAT remediation queue following C6 Technical Acceptance.

The approved remediation sequence is:

```text
R01 → R02 → R03 → R04 → R05
             ↓
R06 → R07
             ↓
R08
             ↓
R09 → R10 → R11 → R12
```

No application-code implementation is authorized by this document as a blanket change.

Each remediation item must proceed through the controlled implementation workflow and receive its own focused technical validation before closure.

---

## 16. Decision Summary

The decision is:

1. **C6 remains technically complete.**
2. **Browser UAT findings are formally recorded.**
3. **The twelve identified remediation items constitute the approved pilot-critical remediation queue.**
4. **Existing backend capabilities must be reused wherever technically sufficient.**
5. **Missing browser surfaces must be implemented at the correct application boundary.**
6. **UAT-R10 is treated as a shared transaction-boundary defect, not an Expense-specific transaction workaround.**
7. **UAT-R07 targets Procurement Receiving, not an expanded generic Stock Movement workflow.**
8. **UAT-R08 uses the existing Catering Event lifecycle rather than introducing a Production/Delivery module.**
9. **UAT-R09 preserves Catering revenue ownership and Finance financial-record ownership.**
10. **UAT-R11 exposes the existing Catering cost association/consumption capability without moving Expense ownership.**
11. **UAT-R12 exposes the existing read-only profitability composition without duplicating accounting or reporting ownership.**
12. **Gate 6 remains pending until remediation and browser re-UAT establish pilot readiness.**
13. **Final SSRC pilot acceptance is not claimed by this baseline.**

---

## 17. Status

**Decision:** Approved
**Status:** **APPROVED / ACTIVE**
**Scope:** SSRC-IBMS Browser UAT remediation following C6 technical acceptance
**Code Changes:** None authorized by approval of this baseline alone
**Gate 6:** Pending
**Final Pilot Acceptance:** Not claimed

---

# 18. UAT-R12 Implementation Checkpoint

## 18.1 Implementation Record

**Finding:** UAT-R12 — Event Profitability
**Implementation Status:** Implemented and committed
**Commit:** `8df8a26` — `feat(catering): expose event profitability`
**Branch:** `master`
**Automated Regression:** 3,216 tests passed
**Working Tree at Checkpoint:** Clean

The implementation exposes the existing read-only `EventProfitabilityService` through the Catering event-detail browser surface. The view presents the event context, recognized revenue, consumed costs, total cost, resulting profit, and cost contributions where the underlying service can provide them.

The implementation preserves the established business ownership boundaries and does not introduce a second profitability calculation, a duplicate accounting ledger, or persisted profitability facts.

The focused route tests and expense-cost association tests passed during implementation validation. Python compilation and Git whitespace checks also passed.

## 18.2 Browser Verification Limitation

Initial browser verification confirmed that:

- the event-detail page loads;
- the profitability view is exposed;
- the expense-cost association form opens; and
- successful expense-cost association submission redirects to the event detail and displays a success message.

However, the event-detail page displayed a warning that multiple recognized Catering revenue records were found. Successful profitability figures have therefore **not yet been accepted as browser-verified against a controlled dataset**.

The revenue retrieval path currently expects a single recognized revenue result for the event. The multiple-result condition must be investigated through read-only inspection and controlled UAT preparation.

Do not arbitrarily select one revenue record, aggregate records, alter existing business data, or change the revenue domain contract as part of dataset preparation. Any required business-rule change must be assessed and approved separately.

## 18.3 Checkpoint Decision

UAT-R12 is implementation-complete for code-checkpoint purposes, but its browser acceptance evidence remains incomplete.

The R12 implementation checkpoint does not establish Gate 6 readiness. Controlled-data browser re-UAT remains required.

# 19. Controlled UAT Dataset Preparation and Recovery Gate

## 19.1 Objective

Prepare a controlled, reproducible dataset for end-to-end browser re-UAT after completion of the R01–R12 remediation implementation.

The dataset must support verification of the pilot business flow across Catering, Procurement, Inventory, Expense, and the established financial integration boundaries. It must also allow the R12 profitability view to be evaluated using unambiguous recognized-revenue and consumed-cost data.

## 19.2 Mandatory Preparation Sequence

Dataset preparation must follow these gated stages:

1. **Read-only environment and database discovery.** Identify the active application configuration, database target, migration state, relevant tables, record counts, foreign-key relationships, and dependencies. Do not expose passwords, connection strings, or other secrets in the evidence.
2. **Data and dependency assessment.** Determine which existing records are production-like, operational, reference, test, or otherwise protected. Identify dependencies across Catering, Procurement, Inventory, Expense, users, permissions, and financial integration records.
3. **Backup and recovery verification.** Create a backup using the approved database-specific procedure. Record the database identity, backup timestamp, artifact location, verification result, and recovery instructions. Establish that the backup is usable and that the restoration procedure is available before any destructive operation is considered.
4. **Proposed reset and seed plan.** Prepare a dependency-aware plan identifying the exact records or tables proposed for reset, the deletion or cleanup order, the records to preserve, the seed sequence, and the verification criteria.
5. **Explicit review and approval.** Review the proposed plan and backup evidence before authorizing any reset or data modification.
6. **Controlled execution.** Only after approval, execute the approved reset and seed operations, verify referential integrity and expected records, and capture the resulting evidence.
7. **Browser re-UAT.** Execute the agreed end-to-end pilot scenarios against the controlled dataset and record pass, fail, or blocked results with supporting evidence.

Progression through a stage does not automatically authorize the next stage.

## 19.3 Data Protection Rules

Until the reset and seed plan has been explicitly approved:

- perform read-only inspection only;
- do not delete, truncate, overwrite, or bulk-update database records;
- do not reset the database or rerun migrations against an unverified target;
- do not modify users, roles, permissions, application configuration, reference data, or migration history;
- do not alter existing business records merely to remove the R12 multiple-revenue warning; and
- do not assume that a development or UAT database is disposable until its identity and purpose are verified.

Any proposed exception must be documented and approved before execution.

## 19.4 Dataset Design Requirements

The proposed controlled dataset should include only the records required to execute and verify the approved pilot scenarios.

The plan must account for the relevant relationships among:

- Catering customers, requests, events, quotations, and event requirements;
- Catering purchase requirements and Procurement purchase requests and purchase orders;
- approved purchase orders and receiving operations;
- Inventory movements, balances, and stock effects;
- Expense records, approval state, and Catering cost associations;
- recognized Catering revenue and the associated financial integration records; and
- user identities, roles, permissions, and audit or idempotency records required by the tested workflows.

The exact table list, dependency order, reset scope, and seed values must be derived from read-only repository and database inspection. They must not be guessed from this conceptual list.

## 19.5 R12 Profitability Acceptance Data

The controlled R12 scenario must make the expected profitability result independently verifiable.

Before execution, document:

- the selected test event;
- the expected recognized-revenue record or records under the approved domain contract;
- the expected consumed-cost contributions;
- the expected total cost and resulting profit;
- the source records used to establish those expectations; and
- the browser evidence required to confirm that the displayed values match the expected result.

The dataset must not conceal or work around an unresolved business rule concerning multiple recognized revenue records. If the supported domain contract requires exactly one recognized revenue record per event, the controlled scenario should satisfy that rule. If multiple records are valid, their expected handling must be clarified and approved separately.

## 19.6 Backup and Recovery Evidence

Before any approved reset, retain a record of:

- database identity and environment;
- backup timestamp and artifact location;
- backup verification or integrity-check result;
- the applicable restoration procedure;
- restoration prerequisites and access requirements; and
- the person responsible for confirming recovery readiness.

Do not include credentials or secret configuration values in the decision record. Do not claim that recovery has been verified until the relevant evidence exists.

## 19.7 Current Authorization Boundary

**Current status:** Planning approved; database inspection, backup execution, reset, and seeding are separate pending activities.

This section authorizes planning and read-only discovery only. It does not authorize database mutation, cleanup, deletion, reset, or seeding.

The controlled dataset may be executed only after the target database is identified, the backup and recovery evidence is reviewed, and the exact reset and seed plan is explicitly approved.

## 19.8 Acceptance Gate

Controlled-data browser re-UAT may begin only when:

1. the target environment and database are verified;
2. the backup and recovery procedure are documented and verified;
3. the dependency-aware reset and seed plan is approved;
4. the approved dataset has been created and validated; and
5. expected outcomes for the pilot scenarios, including R12 profitability, are documented.

Gate 6 remains pending until the required browser scenarios pass and the pilot readiness evidence is reviewed.

---

# 20. Completed Read-Only Browser Walkthrough and Navigation Findings

## 20.1 Purpose and Evidence Boundary

The read-only browser walkthrough reviewed the accessible Catering, Procurement, Inventory, and Expense Management pages in the configured UAT environment.

**Walkthrough status:** Completed
**Data mutation during walkthrough:** None
**Controlled ICRC scenario entered:** No
**Gate 6:** Pending

The walkthrough verified page accessibility, visible empty states, available create actions, and form presentation. It did not establish successful end-to-end business transactions, controlled-data financial results, or final pilot acceptance.

A page loading successfully is evidence of browser accessibility only. It does not prove that every underlying business capability is complete or that the full workflow has passed acceptance testing.

## 20.2 Verified Browser Observations

### Catering

The following pages opened without visible browser errors and presented sensible empty states:

- Customers
- Catering Requests
- Catering Events
- Catering Revenue
- Product Categories
- Products

Create actions were available on the reviewed list pages. Forms were opened for inspection only; no records were submitted or created.

The Catering Events page directs the user to **View Catering Requests** to access the request-led event workflow. This is consistent with the established B1 workflow and is not classified as a defect merely because event creation is not presented as an independent create action.

The current Catering navigation did not expose a visible Quotations page. Event Requirements, Catering Purchase Requirements, and Production/Delivery were also not visible as separate entries in the reviewed navigation. These observations establish a navigation/accessibility gap for further investigation; they do not prove that the underlying capabilities or routes are absent.

### Procurement

The Suppliers, Purchase Requirements, Purchase Requests, and Purchase Orders pages opened without visible browser errors and displayed sensible empty states.

Create actions and forms were accessible for the reviewed Purchase Requirements, Purchase Requests, and Purchase Orders workflows. No forms were submitted and no records were changed.

No Create Supplier action was visible during the Suppliers list review. This is recorded as an observation pending permission and workflow verification, not as a confirmed defect.

### Inventory

The Stock Items, Inventory Locations, Stock Balances, Stock Movements, and Stock Transfers pages opened without visible browser errors and displayed sensible empty states.

Create actions were available on the reviewed Stock Items, Inventory Locations, Stock Movements, and Stock Transfers pages. Forms were inspected without submission.

### Expense Management

The Expenses and Expense Classifications pages opened without visible browser errors and displayed sensible empty states. Create actions and forms were accessible. No records were submitted or changed.

## 20.3 Navigation Information-Architecture Finding

The current Catering navigation places Inventory and its five operational pages within the same navigation list as Catering's customer, request, event, revenue, product-category, and product pages.

This arrangement makes the Catering business workflow and physical stock-management functions appear as one undifferentiated navigation group. It is a navigation and information-architecture concern; the walkthrough does not establish that the underlying module ownership or permissions are incorrect.

**Proposed navigation structure for review:**

**Catering**
- Customers
- Catering Requests
- Catering Events
- Catering Revenue
- Product Categories
- Products

**Inventory Management — separate top-level navigation section**
- Stock Items
- Inventory Locations
- Stock Balances
- Stock Movements
- Stock Transfers

The proposal is intended to make the distinction between Catering's business workflow and Inventory's physical stock responsibilities clearer to users. It does not authorize changes to routes, permissions, module registration, database structures, or business logic.

Before implementation, verify the existing module-registration and navigation architecture, permission requirements, and cross-module links. The proposed arrangement must preserve authorized access and the established ownership boundary: Inventory remains responsible for physical stock effects, while Catering owns its business-layer concepts.

## 20.4 Deferred Form Usability Observations

Across several reviewed Catering, Procurement, and Expense Management forms, required fields were not consistently obvious to users. Some forms displayed Cancel but did not expose a separate return-to-list action.

The walkthrough also observed inconsistent visible browser-native validation behavior between forms. These are recorded as usability observations for later assessment. They do not, by themselves, establish that server-side validation is absent or that the forms are functionally invalid.

No form was submitted to test or alter application data during this walkthrough. No code changes are authorized by these observations.

## 20.5 Interpretation and Follow-Up Classification

The findings are classified as follows:

1. **Browser-accessible:** Reviewed list pages and forms loaded without visible browser errors.
2. **Navigation proposal:** Separate Inventory Management from the Catering navigation list, subject to architecture and permission review.
3. **Further verification required:** Access paths for Quotations, Event Requirements, Catering Purchase Requirements, and Production/Delivery; the absence of a visible Create Supplier action; and any related permission or workflow constraints.
4. **Deferred usability assessment:** Required-field clarity, form return navigation, and consistent browser validation feedback.
5. **Not yet accepted:** End-to-end workflow execution against a controlled dataset, R12 profitability acceptance against unambiguous test data, and Gate 6 readiness.

These results supplement the historical R01–R12 findings. They do not erase the original findings, replace the R12 controlled-data acceptance requirement, or establish that unverified capabilities are complete.

## 20.6 Data Protection and Authorization Boundary

The browser walkthrough was read-only. No customer, request, event, revenue, product, supplier, inventory, purchase, or expense records were created or modified, and the approved ICRC scenario was not entered.

The database preparation, backup and recovery, reset and seed authorization gates in Section 19 remain in force. Any future scenario execution must follow those gates and receive the required explicit approval.

**Decision:** Record the completed read-only walkthrough and the proposed navigation improvement. Defer application changes until the relevant architecture and permission boundaries are reviewed. Controlled-data browser re-UAT and Gate 6 acceptance remain pending.

# SSRC-IBMS Browser UAT Remediation Baseline

**Project:** CDCS-EMP / SSRC Integrated Business Management System (SSRC-IBMS)
**Roadmap:** `SSRC-IBMS-PILOT-READINESS-IMPLEMENTATION-ROADMAP-V1.md`
**Phase:** SSRC Pilot Browser UAT
**Relationship:** Post-C6 Technical Acceptance / Pre-Gate 6 Remediation Baseline
**Status:** **APPROVED / ACTIVE**
**Application-Code Changes:** None authorized by this baseline alone
**Acceptance Position:** Browser UAT inventory completed; remediation baseline approved; Gate 6 not yet achieved

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

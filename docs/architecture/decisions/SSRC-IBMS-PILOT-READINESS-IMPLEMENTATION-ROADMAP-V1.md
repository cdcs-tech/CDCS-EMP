# SSRC-IBMS Pilot Readiness Implementation Roadmap — Version 1

**Project:** CDCS-EMP / SSRC Integrated Business Management System (SSRC-IBMS)
**Roadmap Status:** Approved
**Version:** 1.0
**Purpose:** Pilot Readiness Implementation Roadmap
**Authoritative Location:** `docs/architecture/decisions/SSRC-IBMS-PILOT-READINESS-IMPLEMENTATION-ROADMAP-V1.md`

---

## 1. Purpose

This roadmap defines the implementation path required to transform the current CDCS-EMP platform into a pilot-ready **SSRC Integrated Business Management System (SSRC-IBMS)**.

The roadmap is derived from:

- the approved SSRC-IBMS Phase One scope;
- the current CDCS-EMP capability baseline;
- the completed Phase 2.2 Procurement & Finance Integration work;
- the consolidated SSRC-IBMS Pilot Scope & Readiness Assessment;
- the approved decision to build a focused Finance capability supporting the Catering business initially;
- the approved decision that Catering is the principal business capability required for the SSRC pilot.

This roadmap is intended to guide implementation sequencing, architecture decisions, verification, acceptance, and eventual pilot deployment.

It does **not** create a separate SSRC software branch or architecture. New capabilities must remain reusable components of CDCS-EMP.

---

# 2. Roadmap Objectives

The roadmap has six primary objectives:

1. Establish the core Catering business capability required by SSRC.
2. Establish a focused Finance capability supporting Catering operations.
3. Integrate Catering, Procurement, Inventory, Expense, and Finance while preserving ownership boundaries.
4. Connect business data to the existing Reporting & Analytics framework and deliver SSRC management reporting and dashboards.
5. Configure and validate the platform against the actual SSRC pilot operating environment.
6. Operationalize the platform for secure, supportable, recoverable deployment.

---

# 3. Guiding Principles

## 3.1 Reusable Platform Principle

All capabilities must be implemented as reusable CDCS-EMP capabilities.

SSRC-specific configuration belongs in configuration, master data, permissions, workflows, report definitions, and deployment settings rather than in permanent SSRC-specific code forks.

---

## 3.2 Pilot-First Principle

Implementation will prioritize capabilities required for the SSRC pilot.

Capabilities that are not required for the pilot will not automatically be implemented merely because they appear in the broader conceptual scope.

---

## 3.3 Business-First Principle

The implementation must follow actual business workflows rather than isolated technical modules.

The primary pilot business flow is:

**Customer → Catering Request/Event → Quotation → Approval/Confirmation → Purchase Requirements → Procurement → Purchase Order → Inventory Receipt → Catering Production/Delivery → Catering Revenue → Catering Expenses/Costs → Profitability → Management Reporting/Dashboard**

---

## 3.4 Ownership Principle

Each business capability remains responsible for its own domain.

- Catering owns catering customers, events, quotations, event requirements, production/delivery context, costing context, and catering revenue context.
- Procurement owns suppliers, sourcing, purchase requirements, purchase requests, purchase orders, procurement approvals, and procurement lifecycle.
- Inventory owns stock items, locations, balances, movements, transfers, and physical stock effects.
- Expense Management owns operational expense records, classifications, and expense lifecycle.
- Finance owns financial records and financial processing introduced by the focused Finance capability.
- Reporting consumes approved business data through reporting contracts and providers.

No module should directly assume ownership of another module's domain.

---

## 3.5 Integration Boundary Principle

Cross-module integration must use established application contracts, services, commands, events, read models, or other approved integration mechanisms.

The implementation must not introduce:

- cross-module repository access;
- inappropriate cross-module foreign keys;
- duplicate ownership;
- distributed transactions;
- hidden synchronization logic.

---

# 4. Approved Pilot Capability Model

The SSRC pilot implementation is organized into six implementation streams.

| Stream | Capability | Role in Pilot |
|---|---|---|
| A | Catering-Support Finance Capability | Supporting financial capability |
| B | Catering Business Layer | **Primary business capability** |
| C | Finance / Procurement / Expense Integration | Cross-module operational integration |
| D | SSRC Reporting & Dashboards | Management and decision-support capability |
| E | Pilot Configuration & Acceptance | SSRC operational readiness |
| F | Deployment & Operations | Production readiness |

---

# 5. Stream A — Catering-Support Finance Capability

## 5.1 Objective

Implement a focused financial capability sufficient to support the SSRC Catering business during the pilot.

This is **not** a general-purpose accounting or ERP Finance system.

The initial capability must provide a clean expansion path for future financial requirements.

---

## 5.2 Initial Scope

The initial Finance capability will support, where required by the Catering workflow:

- income/revenue registration;
- expenditure and cost recording;
- invoice generation;
- receipt generation where required;
- financial transaction history relevant to the pilot;
- basic financial summaries;
- financial information required for catering profitability;
- financial information required by SSRC management reporting.

---

## 5.3 Explicit Initial Exclusions

The initial Finance capability will not attempt to implement a full accounting ERP.

The following remain outside the initial scope unless a later approved requirement requires them:

- full general ledger;
- comprehensive accounts payable;
- comprehensive accounts receivable;
- payroll accounting;
- tax accounting;
- complex financial statements;
- banking and bank reconciliation;
- comprehensive budgeting;
- treasury management;
- enterprise-wide accounting;
- private or parallel accounting infrastructure.

---

## 5.4 Stream A Stages

### A1 — Finance Domain & Contract Definition

Define:

- Finance entities;
- financial transaction concepts;
- revenue concepts;
- expenditure/cost concepts;
- invoice concepts;
- receipt concepts;
- financial statuses;
- required relationships;
- ownership boundaries;
- integration contracts;
- audit requirements.

**Acceptance gate:** Finance domain boundaries are documented and approved before implementation.

---

### A2 — Catering Revenue Capability

Implement the minimum reusable capability for recording Catering revenue.

Expected capability includes:

- revenue records;
- revenue classification;
- source/reference information;
- amount;
- date;
- status;
- customer/event relationship where appropriate;
- audit information.

**Acceptance gate:** Catering revenue can be represented without creating duplicate financial ownership inside Catering.

---

### A3 — Invoice & Receipt Capability

Implement the minimum invoice/receipt capability required by the pilot.

This should support the operational Catering workflow rather than attempt to become a complete enterprise billing platform.

**Acceptance gate:** A valid Catering financial transaction can produce the required invoice/receipt information.

---

### A4 — Catering Financial History & Summaries

Provide basic financial history and summary capabilities required for:

- revenue monitoring;
- expenditure monitoring;
- event financial review;
- management summaries;
- profitability calculations.

**Acceptance gate:** Pilot users can obtain the financial information required for operational and management decisions.

---

# 6. Stream B — Catering Business Layer

## 6.1 Objective

Expand the existing Catering module from its current inventory-oriented foundation into the principal SSRC operational business capability.

This is the **main business module required by the SSRC pilot**.

---

## 6.2 Existing Foundation

The existing Catering capability already provides a reusable inventory foundation including:

- product categories;
- products;
- stock items;
- locations;
- stock balances;
- stock movements;
- stock transfers;
- inventory controls.

This foundation must be retained and extended rather than replaced.

---

## 6.3 Initial Business Scope

The Catering business layer will establish:

- customer registration;
- catering requests;
- event management;
- quotation management;
- quotation approval/confirmation;
- event requirements;
- procurement requirements;
- production/delivery context;
- catering costing;
- catering revenue context;
- profitability analysis;
- operational reporting inputs.

---

## 6.4 Stream B Stages

### B1 — Catering Domain & Workflow Definition

Define the Catering business domain and lifecycle.

Expected lifecycle concepts include:

**Customer → Request → Event → Quotation → Confirmation → Requirements → Fulfilment → Delivery/Completion → Financial Outcome**

Acceptance criteria must be defined for each major business state.

**Acceptance gate:** Catering business lifecycle and ownership boundaries are approved.

---

### B2 — Customer Management

Implement:

- customer records;
- customer identification;
- contact information;
- customer status;
- customer history/reference relationships.

**Acceptance gate:** A Catering customer can be registered and reused across Catering transactions.

---

### B3 — Catering Request & Event Management

Implement:

- catering requests;
- event records;
- event dates;
- customer linkage;
- service details;
- event status;
- operational information.

**Acceptance gate:** A complete Catering event can be created and managed from request through operational fulfilment.

---

### B4 — Quotation Management

Implement:

- quotation creation;
- quotation lines;
- pricing;
- totals;
- quotation status;
- approval/confirmation;
- customer/event relationship.

**Acceptance gate:** A Catering event can progress through quotation and confirmation.

---

### B5 — Event Requirements & Procurement Integration

Establish the mechanism through which Catering identifies required goods/services and creates Procurement-side requirements.

The ownership boundary is:

**Catering identifies the business requirement. Procurement owns the procurement lifecycle.**

The implementation must not create a second procurement system inside Catering.

**Acceptance gate:** A Catering requirement can enter the existing Procurement workflow without ownership duplication.

---

### B6 — Catering Costing

Implement reusable costing structures sufficient to determine the cost associated with a Catering event.

Cost inputs may include:

- inventory consumption;
- procurement costs;
- operational expenses;
- other approved pilot cost categories.

**Acceptance gate:** Event cost can be calculated from defined and traceable inputs.

---

### B7 — Revenue & Profitability

Connect Catering revenue and costing information to provide event-level profitability information.

At minimum:

**Revenue − Recognized Cost = Operational Profitability**

The implementation must define clearly which financial and operational records are included in the calculation.

**Acceptance gate:** A completed Catering event can produce an auditable profitability result.

---

# 7. Stream C — Finance / Procurement / Expense Integration

## 7.1 Objective

Connect the new Catering and Finance capabilities to the existing Procurement and Expense capabilities while preserving the approved ownership model.

The completed Phase 2.2 Procurement ↔ Finance integration provides the architectural foundation for this work.

---

## 7.2 Integration Areas

Integration will address:

- Catering → Procurement;
- Procurement → Finance;
- Catering → Inventory;
- Inventory → Catering costing;
- Catering → Finance revenue;
- Expense → Catering costing;
- Finance → Reporting;
- Procurement → Reporting;
- Expense → Reporting;
- Inventory → Reporting.

---

## 7.3 Stream C Stages

### C1 — Integration Contract Reconciliation

Reconcile new Catering and Finance requirements with the existing enterprise integration architecture.

**Acceptance gate:** No new integration violates established Phase 2.2 boundaries.

---

### C2 — Catering → Procurement

Implement the business flow:

**Catering Requirement → Procurement Requirement → Procurement Request → Purchase Order**

**Acceptance gate:** Procurement remains the owner of procurement execution.

---

### C3 — Procurement / Inventory Receiving Integration

Connect approved Purchase Order receiving execution to Inventory physical stock effects through the existing enterprise integration boundary.

The implemented flow is:

**Approved Purchase Order → Receive Purchase Order Command → Receiving Handler → Purchase Order Receipt Contract → Integration Lifecycle → Inventory Receipt Provider → StockMovementService**

Procurement owns the Purchase Order receiving context and initiates the receiving integration. Inventory remains responsible for resolving Inventory references and applying physical stock effects.

The Inventory receiving boundary owns:

- receipt idempotency;
- Stock Movement creation and posting;
- Stock Balance effects;
- atomic receipt posting and duplicate-receipt protection.

Receiving does not constitute a Purchase Order workflow transition. The Purchase Order remains in its existing workflow state after the receiving integration is executed. Partial receipts are supported without requiring the received quantity to equal the ordered quantity.

The integration boundary must prevent Procurement from directly manipulating Inventory persistence. Procurement must communicate receiving outcomes through the established integration contracts and lifecycle, while Inventory owns the authoritative physical inventory mutation.

The ownership boundary remains:

**Procurement owns procurement receiving context; Inventory owns physical inventory state.**

**Acceptance gate:** Stock cannot be changed through an inappropriate Procurement-owned persistence path, and Purchase Order receiving must delegate physical inventory effects through the established Inventory integration boundary.

---

### C4 — Expense → Catering Cost Integration

Allow approved Expense records to contribute to Catering costing where an explicit Catering-owned association identifies the Expense as eligible.

Expense Management remains authoritative for the Expense record and its lifecycle. Catering owns the association between an Expense and its Catering business context, including the Catering-side eligibility and consumption state.

The C4 integration uses the established enterprise integration boundary:

**Expense Approval → Post-Commit Execution → Catering Integration Provider → Catering Expense Cost Consumption**

The originating Expense approval transaction is not dependent on successful Catering consumption. Catering consumption is therefore performed after the Expense transaction has committed through the enterprise post-commit execution mechanism.

C4 establishes the following boundaries:

- Expense remains the authoritative owner of the Expense record, classification, amount, description, expense date, approval state, and approval timestamp.
- Approval alone does not make an Expense eligible for Catering costing.
- Catering eligibility is established only through an explicit Catering Expense Cost Association.
- The association identifies the originating Expense and the Catering context using external identifiers rather than a direct Expense-to-Catering database foreign key.
- Catering owns the association lifecycle and consumption state.
- The integration communicates an immutable approved Expense contribution contract containing only the Expense facts required by the approved C4 boundary together with the Catering context and stable contribution identity.
- The Catering integration provider consumes the approved contribution through the enterprise IntegrationService.
- Successful consumption changes the Catering association from `ELIGIBLE` to `CONSUMED`.
- Failed consumption does not mark the association as consumed, allowing the integration to remain retryable.
- Multiple eligible Catering associations for the same Expense are processed independently.
- Catering consumption does not modify the originating Expense record.
- C4 does not implement Catering costing calculations, cost allocation, profitability calculation, accounting, ledger processing, payments, or other Finance processing.

The implementation reuses the enterprise post-commit execution and integration infrastructure rather than introducing a Catering-specific execution mechanism.

**Acceptance gate:** An approved Expense contributes to Catering only when an explicit Catering association identifies it as eligible. Expense remains authoritative for the Expense record and lifecycle. Catering owns the association and consumption state, while the enterprise integration boundary communicates the approved Expense business fact. No direct Expense-to-Catering database foreign key is introduced, and C4 does not implement Catering costing or allocation logic.

**Verification:** The complete approved Expense → enterprise post-commit → Catering integration provider → Catering consumption path has been verified through the real CommandDispatcher and authorization boundary, with the Expense reaching `APPROVED` and the associated Catering record reaching `CONSUMED`.

---

### C5 — Catering → Finance Revenue Integration

Connect an already-established Catering revenue fact to the focused Finance capability through the enterprise integration boundary.

C5 depends on **A1 — Finance Domain & Contract Definition** and **A2 — Catering Revenue Capability**. A1 defines the Finance-side revenue record, lifecycle, classification, source/reference, ownership, audit, idempotency, and integration contract. A2 establishes the authoritative Catering revenue fact, including its recognition/eligibility rules, amount, date, source identity, and applicable customer/event relationship.

C5 shall:

- deliver an immutable Catering revenue contribution to Finance after the originating Catering transaction has successfully committed;
- use the existing enterprise `IntegrationRequest` → `IntegrationService` → registered provider architecture;
- use the existing `PostCommitExecutor` boundary rather than performing Finance delivery inside the originating Catering transaction;
- provide a stable contribution identity so repeated delivery cannot create duplicate Finance revenue representation;
- preserve traceability from the Finance financial record back to its authoritative Catering revenue source;
- keep Catering authoritative for the originating revenue business fact;
- keep Finance authoritative for the resulting financial record.

C5 shall **not**:

- define Catering revenue recognition rules;
- infer recognized revenue solely from a Catering Event status;
- create duplicate financial ownership inside Catering;
- create invoices, receipts, payments, accounting/ledger postings, or profitability calculations;
- calculate or independently redefine the authoritative Catering revenue amount;
- directly access Finance repositories from Catering or Catering repositories from the Finance provider;
- roll back, reject, or invalidate an already-committed Catering transaction when post-commit Finance delivery fails.

The exact revenue contribution fields, Finance operation name, and Finance persistence/idempotency mechanism shall be established through A1/A2 before C5 implementation begins.

**Acceptance gate:** Revenue is represented once, with a clear source and ownership path.

---

### C6 — End-to-End Business Integration

Validate the complete business flow:

**Customer → Event → Quotation → Requirements → Procurement → Inventory → Production/Delivery → Revenue → Costs → Profitability**

**Acceptance gate:** The complete pilot business flow executes without violating module boundaries.

## 7.4 Stream C Completion Status

**Status:** Technically Complete

Stream C — Finance / Procurement / Expense Integration has completed its planned implementation and end-to-end technical validation through **C6 — End-to-End Business Integration**.

C6.1 through C6.8 have been completed. The C6.8 acceptance scenario validated the complete pilot business flow through event profitability:

**Customer → Event → Quotation → Requirements → Procurement → Inventory → Production/Delivery → Revenue → Costs → Profitability**

The completed C6.8 validation established that the flow can be composed across the existing CDCS-EMP business capabilities while preserving the defined module ownership and integration boundaries.

### C6 Technical Acceptance Evidence

- **C6.8 full pilot E2E acceptance:** 1 passed;
- **C6 integration regression:** 194 passed;
- **Full CDCS-EMP regression:** 3,113 passed;
- **Final Git checkpoint:** `94398da` — `test(ssrc): validate full pilot business flow`;
- **Working tree:** clean at the C6 checkpoint.

### C6 Acceptance Position

The C6 technical acceptance gate is satisfied:

> The complete pilot business flow executes without violating module boundaries.

C6 technical acceptance does **not** constitute SSRC user acceptance or final pilot acceptance.

The roadmap's **Gate 6 — SSRC Acceptance Ready** separately requires configuration, users, permissions, master data, workflows, end-to-end scenarios, and **UAT**. Browser-based user verification of the pilot-critical scenario therefore remains a required pilot-readiness activity.

The C6.8 technical validation also ends at **Profitability**. The subsequent **Management Report** and **KPI / Dashboard** steps defined in the pilot-critical end-to-end scenario remain associated with **Stream D — SSRC Reporting & Dashboards** and have not been treated as completed by C6.

Accordingly:

- **Stream C / C6 technical acceptance:** Complete;
- **C6 browser / UAT validation:** Pending;
- **Gate 6 — SSRC Acceptance Ready:** Not yet claimed;
- **Stream D reporting, KPI, and dashboard validation:** Pending.

---

# 8. Stream D — SSRC Reporting & Dashboards

## 8.1 Objective

Use the existing CDCS-EMP Reporting & Analytics framework to deliver actual SSRC management reporting and dashboards.

The reporting framework itself is already established.

The remaining work is to connect it to business data and implement SSRC-specific outputs.

---

## 8.2 Initial Reporting Scope

The pilot reporting capability should address:

- revenue performance;
- expenditure trends;
- Catering profitability;
- procurement activity;
- inventory activity;
- operational activity;
- department performance indicators where meaningful;
- management summaries;
- system-wide pilot KPIs.

Future Asset and Membership reporting should not be implemented prematurely.

---

## 8.3 Stream D Stages

### D1 — SSRC KPI Definition

Define the pilot KPI catalogue.

Each KPI must specify:

- name;
- business meaning;
- source;
- calculation;
- period;
- filters;
- ownership;
- authorization;
- reporting frequency.

**Acceptance gate:** KPI definitions are approved before implementation.

---

### D2 — Business Data Providers

Implement concrete Reporting data providers for the required business domains.

Potential providers include:

- Catering;
- Procurement;
- Inventory;
- Expense;
- Finance.

Providers must use the existing Reporting contracts and registry architecture.

**Acceptance gate:** Reporting retrieves business data through approved providers rather than direct presentation-layer database access.

---

### D3 — Operational Reports

Implement the initial report set required for pilot operations.

Examples:

- Catering event report;
- quotation report;
- procurement activity report;
- inventory activity report;
- expense report;
- revenue report;
- profitability report.

---

### D4 — Management Dashboards

Implement dashboards for:

- revenue performance;
- Catering activity;
- expenditure/cost trends;
- procurement activity;
- inventory status;
- profitability;
- agreed management KPIs.

---

### D5 — Reporting Verification

Validate:

- calculations;
- filters;
- permissions;
- data freshness;
- aggregation;
- export behaviour where required;
- auditability.

**Acceptance gate:** SSRC pilot reports and dashboards produce trusted results against approved test scenarios.

---

# 9. Stream E — Pilot Configuration & Acceptance

## 9.1 Objective

Configure the reusable CDCS-EMP platform for the actual SSRC pilot environment and validate it with representative users and business scenarios.

Configuration must remain separate from core reusable architecture.

---

## 9.2 Configuration Scope

The pilot configuration will include:

- organization information;
- departments/units;
- user accounts;
- roles;
- permissions;
- approval responsibilities;
- supplier master data;
- customer master data;
- product categories;
- products;
- stock locations;
- expense classifications;
- Finance classifications;
- report parameters;
- workflow configuration;
- required system settings.

---

## 9.3 Stream E Stages

### E1 — SSRC Master Data Definition

Define and approve pilot master data.

**Acceptance gate:** SSRC confirms master-data structures before loading production data.

---

### E2 — User / Role / Permission Configuration

Configure users and role-based access according to SSRC operational responsibilities.

**Acceptance gate:** Each pilot user can perform only the operations appropriate to their role.

---

### E3 — Workflow Configuration

Configure and validate:

- Catering approval;
- quotation approval;
- Procurement approval;
- Expense approval;
- Finance-related approvals where required.

---

### E4 — Business Scenario Testing

Create representative end-to-end scenarios covering:

1. customer registration;
2. catering event;
3. quotation;
4. quotation approval;
5. purchase requirement;
6. procurement;
7. purchase order;
8. inventory receipt;
9. catering fulfilment;
10. revenue recording;
11. expense/cost recording;
12. profitability;
13. management reporting.

---

### E5 — User Acceptance Testing

Conduct structured SSRC acceptance testing.

Each scenario must have:

- expected result;
- actual result;
- tester;
- date;
- pass/fail result;
- defect reference where applicable;
- acceptance decision.

**Acceptance gate:** Pilot-critical scenarios are accepted by SSRC.

---

### E6 — Pilot Readiness Gate

The pilot may proceed only when:

- critical business workflows pass;
- required users and permissions are configured;
- required master data is loaded;
- critical reports are validated;
- known critical defects are resolved;
- operational recovery procedures are validated;
- deployment environment is ready.

---

# 10. Stream F — Deployment & Operations

## 10.1 Objective

Convert the development-ready CDCS-EMP platform into a supportable production deployment for SSRC.

---

## 10.2 Stream F Stages

### F1 — Production Deployment Procedure

Document the repeatable deployment procedure covering:

- server preparation;
- Python environment;
- dependencies;
- environment variables;
- application startup;
- WSGI deployment;
- SQL Server configuration;
- migration execution;
- initial configuration;
- verification.

---

### F2 — Production Security Hardening

Complete production hardening including validation of:

- production SECRET_KEY;
- secure cookies;
- CSRF;
- authentication;
- authorization;
- error handling;
- security headers;
- HTTPS/TLS deployment;
- database credentials/configuration;
- logging;
- administrative access.

---

### F3 — Database Migration Runbook

Document:

- pre-migration checks;
- backup requirement;
- migration execution;
- migration verification;
- rollback/recovery considerations;
- post-migration validation.

---

### F4 — Backup & Restore

Establish a production backup strategy for the SQL Server database.

The procedure must define:

- backup frequency;
- backup type;
- backup location;
- retention;
- access control;
- verification;
- restore procedure.

---

### F5 — Recovery Validation

Perform a controlled restore/recovery test.

A backup strategy is not considered operationally complete until restoration has been demonstrated.

**Acceptance gate:** A recoverable database backup has been successfully restored and validated.

---

### F6 — Operational Monitoring & Logging

Establish:

- log destination;
- log retention;
- monitoring responsibility;
- error review;
- application health checks;
- database health checks;
- operational escalation process.

---

### F7 — Support & Administration Runbook

Document:

- user administration;
- role administration;
- master-data administration;
- deployment;
- migrations;
- backups;
- restore;
- troubleshooting;
- monitoring;
- incident handling;
- upgrade procedure.

---

# 11. Implementation Dependency Architecture

The approved dependency structure is:

```text
                    ┌─────────────────────────┐
                    │     Stream B             │
                    │  Catering Business Layer │
                    │       PRIMARY            │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
       │ Procurement │   │  Inventory  │   │   Finance   │
       │  Existing   │   │  Existing   │   │ Stream A    │
       └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │       Stream C           │
                    │ Integration & Reconcile  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │       Stream D           │
                    │ Reporting & Dashboards   │
                    └───────────┬─────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       ┌───────────────────┐         ┌───────────────────┐
       │     Stream E      │         │     Stream F      │
       │ Configuration &   │         │ Deployment &      │
       │ Acceptance        │         │ Operations        │
       └─────────┬─────────┘         └─────────┬─────────┘
                 └──────────────┬──────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │    SSRC Pilot Ready     │
                    └─────────────────────────┘
```

---

# 12. Recommended Implementation Sequence

The six streams should not be implemented as six completely independent projects.

The implementation sequence is:

## Phase 1 — Domain Foundations

1. **B1 — Catering Domain & Workflow Definition**
2. **A1 — Finance Domain & Contract Definition**
3. **C1 — Integration Contract Reconciliation**
4. **D1 — SSRC KPI Definition**

These establish the business and architectural contracts before substantial implementation.

---

## Phase 2 — Core Catering Capability

5. **B2 — Customer Management**
6. **B3 — Catering Request & Event Management**
7. **B4 — Quotation Management**

This establishes the primary user-facing Catering workflow.

---

## Phase 3 — Operational Fulfilment

8. **B5 — Event Requirements & Procurement Integration**
9. **C2 — Catering → Procurement**
10. **C3 — Procurement / Inventory Receiving Integration**
11. **B6 — Catering Costing**

This connects the Catering business process to existing operational capabilities.

---

## Phase 4 — Focused Finance

12. **A2 — Catering Revenue Capability**
13. **A3 — Invoice & Receipt Capability**
14. **A4 — Catering Financial History & Summaries**
15. **C4 — Expense → Catering Cost Integration**
16. **C5 — Catering → Finance Revenue Integration**

This establishes the minimum financial capability needed to complete the Catering business cycle.

---

## Phase 5 — Profitability & Reporting

17. **B7 — Revenue & Profitability**
18. **D2 — Business Data Providers**
19. **D3 — Operational Reports**
20. **D4 — Management Dashboards**
21. **D5 — Reporting Verification**

This converts operational data into management information.

---

## Phase 6 — Pilot Configuration & Acceptance

22. **E1 — SSRC Master Data Definition**
23. **E2 — User / Role / Permission Configuration**
24. **E3 — Workflow Configuration**
25. **E4 — Business Scenario Testing**
26. **E5 — User Acceptance Testing**
27. **E6 — Pilot Readiness Gate**

---

## Phase 7 — Production Operationalization

28. **F1 — Production Deployment Procedure**
29. **F2 — Production Security Hardening**
30. **F3 — Database Migration Runbook**
31. **F4 — Backup & Restore**
32. **F5 — Recovery Validation**
33. **F6 — Operational Monitoring & Logging**
34. **F7 — Support & Administration Runbook**

---

# 13. Major Acceptance Gates

Implementation must use explicit gates rather than treating the entire roadmap as one continuous development effort.

## Gate 1 — Architecture Ready

Required:

- Catering domain defined;
- Finance domain defined;
- integration boundaries reconciled;
- KPI definitions established.

---

## Gate 2 — Catering Core Ready

Required:

- customer management;
- event/request management;
- quotation management;
- core workflows verified.

---

## Gate 3 — Operational Flow Ready

Required:

- Catering → Procurement;
- Procurement → Inventory;
- costing inputs;
- operational fulfilment flow.

---

## Gate 4 — Financial Flow Ready

Required:

- revenue;
- invoices/receipts where required;
- expenses/costs;
- financial history;
- basic financial summaries.

---

## Gate 5 — Management Information Ready

Required:

- reporting providers;
- validated reports;
- dashboards;
- KPI calculations;
- permissions;
- reporting verification.

---

## Gate 6 — SSRC Acceptance Ready

Required:

- configuration;
- users;
- permissions;
- master data;
- workflows;
- end-to-end scenarios;
- UAT.

---

## Gate 7 — Production Ready

Required:

- deployment procedure;
- production security;
- migration runbook;
- backup;
- restore test;
- monitoring;
- support procedures.

---

# 14. Pilot-Critical End-to-End Scenario

The principal acceptance scenario is:

```text
1. Register Customer
        ↓
2. Create Catering Request/Event
        ↓
3. Create Quotation
        ↓
4. Approve/Confirm Quotation
        ↓
5. Identify Event Requirements
        ↓
6. Create Procurement Requirement
        ↓
7. Process Procurement Request
        ↓
8. Create / Approve Purchase Order
        ↓
9. Receive Required Inventory
        ↓
10. Record Catering Production / Delivery
        ↓
11. Record Catering Revenue
        ↓
12. Record Catering Costs / Expenses
        ↓
13. Calculate Event Profitability
        ↓
14. Generate Management Report
        ↓
15. Display KPI / Dashboard Result
```

The scenario must be testable using representative SSRC pilot data.

---

# 15. Reuse of Existing CDCS-EMP Capabilities

The roadmap deliberately reuses existing platform foundations.

Existing capabilities to be reused include:

- authentication;
- RBAC;
- authorization;
- command execution;
- workflows;
- transaction boundaries;
- audit/governance;
- event architecture;
- integration framework;
- Procurement;
- Inventory foundation;
- Expense Management;
- Reporting & Analytics framework;
- SQL Server persistence;
- Flask-Migrate/Alembic;
- structured application logging.

New implementation should extend these capabilities rather than introduce competing infrastructure.

---

# 16. Explicitly Deferred Capabilities

The following SSRC proposal areas are acknowledged but are **not immediate pilot implementation defects**.

## 16.1 Hall Hire Management

Deferred capability including:

- venue registration;
- booking;
- scheduling;
- customer records;
- invoicing;
- payment management;
- utilization reporting.

It may be implemented later as a reusable CDCS-EMP business module.

---

## 16.2 Asset Management

Deferred capability including:

- asset register;
- acquisitions;
- categorization;
- assignments;
- movement;
- maintenance;
- verification;
- disposal.

It may be implemented later as a reusable CDCS-EMP business module.

---

## 16.3 Membership Management

Deferred capability including:

- registration;
- categorization;
- subscriptions;
- renewals;
- analytics;
- reporting.

It may be implemented later as a reusable CDCS-EMP business module.

---

# 17. Explicitly Deferred Finance Expansion

The Finance capability may expand after the pilot according to demonstrated business need.

Potential future expansion may include:

- broader financial transaction management;
- accounts receivable;
- accounts payable;
- budgeting;
- broader financial reporting;
- additional payment capabilities;
- broader accounting integrations.

Such expansion requires a separate approved scope and architecture decision.

The initial pilot must not be delayed by attempting to build a complete accounting ERP.

---

# 18. Operational Readiness Requirements

Before SSRC production go-live, the following must be demonstrated:

### Application

- production configuration;
- production WSGI deployment;
- DEBUG disabled;
- secure session configuration;
- CSRF protection;
- authentication;
- authorization;
- appropriate error handling;
- production security hardening.

### Database

- SQL Server production database;
- migration history;
- migration procedure;
- backup procedure;
- restore procedure;
- successful recovery test.

### Operations

- logging;
- monitoring;
- health checks;
- administration procedure;
- support procedure;
- incident handling.

### Data

- approved master data;
- approved users;
- approved permissions;
- approved opening/initial records where required.

---

# 19. Verification Strategy

Each implementation stage must follow the CDCS-EMP controlled development workflow:

1. Identify the exact stage/component.
2. Inspect only the information required for that stage.
3. Define the smallest correct implementation.
4. Implement one focused change.
5. Run targeted tests.
6. Run relevant module/regression tests.
7. Run the full suite at the appropriate stage/checkpoint.
8. Verify the working tree.
9. Create a Git checkpoint.
10. Document the approved architectural outcome where required.

No stage should expand into unrelated functionality without an explicit scope decision.

---

# 20. Definition of Pilot Ready

SSRC-IBMS will be considered **Pilot Ready** when all of the following are true:

### Business

- Core Catering workflow is operational.
- Procurement supports Catering requirements.
- Inventory supports physical stock effects.
- Expenses support relevant Catering costs.
- Focused Finance supports required Catering revenue and financial records.
- Profitability can be determined for the agreed pilot scenarios.

### Reporting

- Required SSRC KPIs are defined.
- Required reports are implemented.
- Required dashboards are implemented.
- Reporting results are validated.

### Security & Governance

- Users are configured.
- Roles and permissions are configured.
- Approval responsibilities are validated.
- Audit/governance mechanisms operate as expected.

### Operations

- Production deployment procedure exists.
- Database migration procedure exists.
- Backup procedure exists.
- Restore/recovery procedure exists.
- Recovery has been tested.
- Logging and monitoring are operational.
- Support procedures exist.

### Acceptance

- Pilot scenarios pass.
- SSRC UAT is completed.
- Critical defects are resolved.
- SSRC accepts the pilot capability.

---

# 21. Post-Pilot Expansion Model

After pilot acceptance, future development should be driven by:

1. actual SSRC operational experience;
2. measured user requirements;
3. business gaps discovered during pilot operation;
4. support and operational findings;
5. additional customer requirements applicable to reusable CDCS-EMP;
6. approved architectural decisions.

Potential future capability streams include:

- Hall Hire;
- Asset Management;
- Membership Management;
- expanded Finance;
- broader enterprise reporting;
- additional operational modules.

Future capabilities must continue to follow the reusable CDCS-EMP architecture.

---

# 22. Roadmap Governance

This document is the authoritative **Version 1 SSRC-IBMS Pilot Readiness Implementation Roadmap**.

Changes to:

- stream scope;
- implementation sequence;
- ownership boundaries;
- major exclusions;
- acceptance gates;
- pilot-readiness criteria

must be explicitly reviewed and documented.

Individual implementation stages may create or update subordinate technical decision records where necessary, but they must remain consistent with this roadmap and the existing CDCS-EMP architecture decision records.

The roadmap does not override existing approved architecture decisions. Where a conflict appears, the conflict must be resolved through an explicit architecture decision before implementation proceeds.

---

# 23. Final Approved Direction

The SSRC-IBMS pilot will proceed as a **Catering-centered implementation of the reusable CDCS-EMP platform**.

The approved structure is:

**Primary Business Capability**

> Catering

**Supporting Capabilities**

> Procurement
> Inventory
> Expense Management
> Focused Finance

**Management Capability**

> Reporting & Dashboards

**Readiness Capabilities**

> Pilot Configuration & Acceptance
> Deployment & Operations

The implementation will therefore prioritize completing the operational Catering business cycle rather than expanding immediately into a large collection of independent enterprise modules.

The initial Finance capability will remain deliberately focused on supporting Catering and will provide an expansion path for future requirements.

Hall Hire, Asset Management, and Membership Management remain future capabilities and are not immediate pilot blockers.

The objective of the roadmap is not simply to add modules. It is to establish a coherent, reusable, operationally supportable business platform capable of taking SSRC's core Catering operation from customer engagement through fulfilment, financial outcome, profitability, and management reporting.

---

# 24. Roadmap Status

**Version:** 1.0
**Status:** Approved
**Implementation Direction:** Approved
**Primary Pilot Capability:** Catering
**Focused Finance Direction:** Approved
**Integration Direction:** Approved
**Reporting Direction:** Approved
**Pilot Configuration & Acceptance:** Approved
**Deployment & Operations:** Approved
**Hall Hire:** Future
**Asset Management:** Future
**Membership Management:** Future

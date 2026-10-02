# Phase 4 — Catering Revenue Capability

**Document:** `PHASE-4-CATERING-REVENUE-CAPABILITY.md`
**Status:** Approved
**Capability:** A2 — Catering Revenue Capability
**Phase:** Phase 4 — Focused Finance
**System:** CDCS-EMP / SSRC-IBMS Pilot
**Owner:** Catering Business Module
**Related Architecture:** A1 — Finance Domain & Contract Definition; C5 — Catering → Finance Revenue Integration

---

## 1. Purpose

This architecture establishes the minimum reusable **Catering Revenue Capability** required for the SSRC-IBMS pilot.

The capability provides Catering with an explicit, authoritative business representation of revenue arising from Catering business activity.

A2 establishes the Catering-side revenue fact that will subsequently be communicated to Finance through **C5 — Catering → Finance Revenue Integration**.

The capability is intentionally focused on revenue representation and recognition within the Catering business domain. It does not establish a general accounting, invoicing, receivables, payments, or ledger subsystem.

The architectural objective is:

> **Catering establishes the authoritative revenue business fact; Finance establishes the authoritative financial record.**

---

## 2. Scope

A2 establishes:

- Catering revenue ownership;
- the Catering Revenue business record;
- explicit revenue recognition and eligibility;
- revenue amount, date, currency, and source;
- applicable customer and event references;
- revenue classification/context required by Catering;
- revenue lifecycle and controlled state changes;
- auditability and traceability;
- stable Catering revenue identity;
- the boundary between Catering revenue and Finance financial records;
- the source fact consumed by C5.

A2 does not implement the Finance module itself.

---

## 3. Architectural Context

The approved SSRC-IBMS business flow is:

```text
Customer
    ↓
Catering Request / Event
    ↓
Quotation
    ↓
Approval / Confirmation
    ↓
Purchase Requirements
    ↓
Procurement
    ↓
Purchase Order
    ↓
Inventory Receipt
    ↓
Catering Production / Delivery
    ↓
Catering Revenue
    ↓
Catering Costs / Expenses
    ↓
Profitability
    ↓
Management Reporting
```

A2 establishes the **Catering Revenue** business fact in this flow.

C5 subsequently communicates that fact to Finance:

```text
Catering Revenue Capability
        ↓
Authoritative Catering Revenue
        ↓
Catering Revenue Contribution
        ↓
Post-Commit Delivery
        ↓
Enterprise Integration Framework
        ↓
Finance Provider
        ↓
Finance Revenue Capability
        ↓
Finance-owned Financial Record
```

The Catering Revenue record and Finance Revenue Record are therefore distinct business records with distinct ownership.

---

## 4. Ownership

### 4.1 Catering Ownership

Catering remains authoritative for:

- Catering customers;
- Catering requests;
- Catering events;
- Catering quotations;
- Catering operational delivery context;
- the originating Catering revenue business fact;
- Catering revenue recognition/eligibility within the approved Catering business rules;
- Catering revenue amount as established by the authoritative revenue fact;
- Catering revenue source context;
- Catering costing context;
- event-level operational profitability.

### 4.2 Finance Ownership

Finance remains authoritative for:

- Finance financial records;
- Finance revenue records;
- Finance financial classification;
- financial treatment;
- financial lifecycle;
- financial history;
- financial summaries;
- invoices;
- receipts;
- payments;
- settlement;
- accounting;
- ledger treatment;
- other Finance-owned financial processing introduced by subsequent approved capabilities.

### 4.3 Other Module Ownership

Procurement remains authoritative for procurement activity.

Inventory remains authoritative for physical stock and inventory effects.

Expense Management remains authoritative for operational expense records and their lifecycle.

Reporting consumes approved business and financial data without becoming authoritative for the underlying records.

---

## 5. Catering Revenue Record

A2 introduces a distinct Catering-owned revenue business record.

The revenue record represents an **established Catering revenue fact**, rather than a quotation, event status, invoice, payment, or accounting entry.

Conceptually, the record contains:

- a stable Catering revenue identity;
- revenue amount;
- currency;
- revenue date / recognition date as applicable;
- revenue classification or business context;
- source/reference information;
- applicable Catering Event reference;
- applicable Customer reference;
- recognition/eligibility information;
- lifecycle state;
- audit information.

The precise implementation field names and database representation shall follow the existing CDCS-EMP model, repository, service, workflow, audit, and migration conventions.

The architecture does not require a new enterprise-wide financial entity outside the Finance module.

---

## 6. Revenue Recognition and Eligibility

Revenue recognition is an explicit business decision within the Catering Revenue Capability.

A2 shall not infer recognized revenue solely from the status of a `CateringEvent`.

Operational event states such as:

- `DELIVERED`;
- `COMPLETED`;

are evidence or inputs that may participate in a revenue-recognition decision, but they do not independently constitute the revenue record.

Likewise:

- quotation issuance does not constitute revenue recognition;
- quotation acceptance does not automatically constitute revenue recognition;
- event confirmation does not automatically constitute revenue recognition.

The revenue capability shall provide an explicit and auditable recognition/eligibility boundary.

The resulting business fact must identify:

1. what revenue is being recognized;
2. the authoritative amount;
3. the applicable revenue date;
4. the source business context;
5. the reason or controlled business transition by which the revenue became recognized/eligible.

The concrete recognition rule shall be implemented according to the approved Catering business requirement rather than being inferred from an existing Event or Quotation workflow merely for implementation convenience.

---

## 7. Relationship to Catering Quotations

`CateringQuotation` remains the authoritative Catering commercial quotation.

A quotation provides commercial monetary information including:

- subtotal;
- adjustment;
- total amount;
- quotation date;
- customer;
- event;
- quotation lifecycle.

However:

> **Quotation total ≠ automatically recognized Catering revenue.**

Quotation acceptance is a commercial decision between Catering and the customer.

A2 must therefore not create revenue merely because a quotation transitions to `ACCEPTED`.

The authoritative revenue amount must instead come from the explicit Catering Revenue recognition capability.

Where a revenue record references a quotation, the quotation reference is source/business context and does not transfer ownership of the quotation to Revenue or Finance.

---

## 8. Relationship to Catering Events

`CateringEvent` remains authoritative for Catering operational event context.

The event provides important business context for revenue, including where applicable:

- event identity;
- customer;
- event date;
- service context;
- operational lifecycle;
- delivery/completion context.

However:

> **Catering Event status ≠ automatically recognized revenue.**

A2 may use event lifecycle information as part of its recognition decision, but the Revenue capability owns the explicit recognition/eligibility decision.

The Revenue record may reference the Catering Event through its business identity.

No additional Finance-specific fields shall be introduced into `CateringEvent` merely to support A2.

---

## 9. Amount and Monetary Representation

The authoritative Catering revenue amount shall be explicitly represented.

The amount must not be independently recalculated by C5 or by Finance during integration.

The A2 implementation shall follow the platform's established monetary representation:

- persisted monetary amounts use fixed precision compatible with the existing platform, including `Numeric(18,2)` where applicable;
- domain/integration contracts use `Decimal`;
- currency is explicit.

A2 shall not introduce hidden floating-point monetary calculations.

The revenue amount communicated to Finance through C5 represents the amount established by the authoritative Catering Revenue record.

Finance remains responsible for determining the financial treatment of that communicated amount.

---

## 10. Revenue Date

Revenue date and recognition date must not be confused with:

- Catering Event date;
- quotation date;
- transaction creation timestamp;
- integration delivery timestamp.

A2 shall represent the business date associated with the recognized revenue fact.

Where the business requirement distinguishes the date of revenue recognition from the underlying event date, both concepts shall remain semantically distinct.

Integration delivery time belongs to the enterprise integration lifecycle and must not replace the authoritative Catering revenue date.

---

## 11. Customer and Event References

Where applicable, the Catering Revenue record may reference:

- Customer identity;
- Catering Event identity;
- other authoritative Catering source identifiers.

These references are business references.

A2 shall not introduce cross-module foreign keys to Finance entities.

The following identities remain distinct:

```text
Customer Identity
        ≠
Catering Event Identity
        ≠
Catering Revenue Identity
        ≠
Finance Revenue Identity
        ≠
Integration Request Identity
```

This separation preserves bounded ownership and prevents duplicate enterprise identity.

---

## 12. Revenue Classification

A2 may require a Catering revenue classification or business context to distinguish different categories of Catering revenue.

Examples may include business-purpose categories or Catering-specific revenue context required for operational reporting.

Such classification must not be confused with Finance accounting classification.

### Catering classification

Owned by Catering and used to describe the originating Catering business fact.

### Finance classification

Owned by Finance and used for Finance-side financial treatment.

Catering shall not assign:

- general-ledger accounts;
- debit/credit instructions;
- journal entries;
- accounting classifications;
- ledger posting instructions;

as part of A2.

Those remain Finance-owned concerns.

---

## 13. Revenue Lifecycle

Revenue shall have an explicit controlled lifecycle appropriate to the business capability.

The lifecycle must distinguish at minimum between:

- a revenue fact that has not yet been recognized/eligible;
- a revenue fact that has been explicitly recognized/eligible;
- any subsequent state required to prevent duplicate recognition or communicate its integration eligibility.

The exact workflow state names shall be established during implementation according to the approved business requirement and existing CDCS-EMP workflow conventions.

The A2 workflow shall:

- validate permitted state transitions;
- prevent invalid recognition transitions;
- preserve auditability;
- avoid embedding Finance processing;
- avoid treating integration delivery as ownership of the revenue fact.

Revenue lifecycle is distinct from Finance delivery lifecycle.

---

## 14. Audit and Traceability

The Revenue capability shall reuse the existing CDCS-EMP audit architecture.

Revenue records shall retain appropriate:

- creation information;
- update information;
- actor identity where supported;
- timestamps;
- lifecycle transition history through the established application architecture;
- source/reference information necessary to establish business traceability.

The revenue record must be traceable to its authoritative Catering business context.

C5 must subsequently preserve traceability from the Finance financial record back to the Catering revenue source.

The integration request identifier is an integration delivery identifier and must not become the authoritative identity of the revenue business fact.

---

## 15. Stable Revenue Identity

A2 shall establish a stable identity for each Catering revenue business fact.

This identity is required because:

- the same revenue fact may be delivered to Finance more than once;
- post-commit delivery may fail;
- delivery may be retried;
- individual integration attempts have their own request identifiers.

Therefore:

> **Catering Revenue Identity ≠ Integration Request Identity.**

The stable Catering revenue identity is the source identity used by C5 for contribution traceability and idempotent downstream processing.

---

## 16. A2 → C5 Boundary

A2 establishes the authoritative source fact consumed by C5.

C5 shall not reconstruct or infer the revenue fact from:

- Catering Event status;
- Catering Quotation status;
- quotation total;
- event completion;
- operational timestamps;
- other indirect information.

Instead:

```text
A2
↓
Authoritative Catering Revenue
↓
Explicit Revenue Contribution
↓
C5
```

The contribution shall communicate the established business fact required by Finance.

Conceptually, it includes:

- stable source contribution identity;
- Catering revenue identity;
- revenue amount;
- currency;
- revenue date/recognition date;
- source/reference information;
- applicable customer identity;
- applicable event identity;
- applicable revenue classification/context.

The exact contribution contract is governed by C5 and shall be reconciled with the approved A1 Finance contract before C5 implementation.

A2 does not directly access Finance repositories, Finance models, or Finance persistence.

---

## 17. Post-Commit Implication

C5 shall deliver recognized Catering revenue after the originating Catering transaction has successfully committed.

The architectural sequence is:

```text
Catering Revenue Transaction
        ↓
Catering Transaction Commits
        ↓
Post-Commit Executor
        ↓
Catering Revenue Contribution
        ↓
IntegrationRequest
        ↓
Finance Provider
```

A2 therefore does not require Finance delivery to occur inside the Catering transaction.

If Finance delivery fails after the Catering revenue transaction has committed:

- the recognized Catering revenue fact remains valid;
- the Catering transaction is not rolled back;
- the revenue record is not invalidated solely because Finance delivery failed;
- the integration remains retryable according to the C5/integration lifecycle.

The originating business fact and downstream delivery state remain distinct concerns.

---

## 18. Idempotency

The acceptance requirement for C5 is:

> **Revenue is represented once, with a clear source and ownership path.**

A2 therefore provides the stable source identity required for downstream idempotent consumption.

The generic `IntegrationRequest.request_id` must not be used as the business idempotency identity because every retry represents a new delivery attempt.

Finance shall establish its durable consumption/idempotency mechanism under A1/C5.

A2 does not create a Finance-owned persistence mechanism.

The architectural identity relationship is:

```text
Catering Revenue Identity
        ↓
Stable Contribution Identity
        ↓
Finance Idempotency / Consumption Identity
        ↓
Finance Revenue Identity
```

These identifiers may be related through explicit business references but remain owned by their respective boundaries.

---

## 19. Reuse of Existing CDCS-EMP Architecture

A2 shall reuse the established CDCS-EMP platform architecture.

The Catering Revenue Capability shall use, as appropriate:

- existing module discovery and lifecycle;
- existing model and persistence framework;
- existing `BaseModel`;
- existing timestamp and audit mixins;
- existing repository pattern;
- existing service pattern;
- existing workflow framework;
- existing execution framework;
- existing authorization/RBAC;
- existing transaction infrastructure;
- existing enterprise integration framework;
- existing post-commit execution architecture;
- existing reporting architecture.

A2 shall not introduce:

- a parallel transaction framework;
- a parallel persistence framework;
- a parallel authorization system;
- a parallel audit framework;
- a new enterprise integration framework;
- a second application/module framework.

---

## 20. Module Boundary

The Catering Revenue Capability belongs within the Catering bounded business module because the originating revenue business fact is a Catering business concern.

Finance does not become authoritative merely because the revenue fact is communicated to Finance.

Likewise, Catering does not become responsible for Finance accounting merely because it establishes the revenue source.

The ownership boundary is:

```text
Catering
    owns:
        originating revenue fact

Finance
    owns:
        financial representation and treatment
```

This follows the CDCS-EMP business-module architecture principle that bounded modules own their authoritative business capability and data while cross-module requirements are handled through explicit contracts.

---

## 21. Explicit Exclusions

A2 does **not** introduce:

- invoices;
- receipts;
- payments;
- receivables;
- supplier settlement;
- accounting entries;
- journal entries;
- general ledger;
- chart of accounts;
- tax engine;
- payment processing;
- banking integration;
- payroll accounting;
- full Accounts Receivable;
- full Accounts Payable;
- budgeting;
- financial consolidation;
- automated accounting allocation;
- Finance-owned revenue records;
- Finance-owned accounting classifications;
- Finance persistence inside Catering;
- direct Finance repository access;
- direct Finance database access;
- cross-module Finance foreign keys;
- distributed transactions;
- duplicate financial ownership inside Catering;
- event-status-only revenue inference;
- quotation-total-as-revenue inference;
- profitability calculations.

Catering profitability remains a later Catering business capability under **B7 — Revenue & Profitability**.

Invoices and receipts remain part of **A3 — Invoice & Receipt Capability**.

Financial history and summaries remain part of **A4 — Catering Financial History & Summaries**.

---

## 22. Architectural Invariants

The following invariants apply to A2:

1. Catering owns the originating Catering revenue business fact.
2. Revenue is represented explicitly rather than inferred from unrelated records.
3. Quotation acceptance does not automatically equal revenue recognition.
4. Event completion does not automatically equal revenue recognition.
5. Revenue recognition is an explicit Catering business decision.
6. The authoritative revenue amount is established by A2.
7. C5 shall not independently redefine the authoritative revenue amount.
8. Customer identity remains owned by Catering.
9. Catering Event identity remains owned by Catering.
10. Catering Revenue identity remains distinct from Finance Revenue identity.
11. Catering Revenue identity remains distinct from Integration Request identity.
12. Finance classification remains Finance-owned.
13. Finance accounting treatment remains Finance-owned.
14. No Finance-owned entities are persisted inside Catering.
15. No cross-module Finance foreign keys are required.
16. Cross-module communication occurs through the enterprise Integration Framework.
17. Finance delivery occurs after the originating Catering transaction commits.
18. Finance delivery failure does not roll back committed Catering revenue.
19. Revenue delivery must support stable business idempotency.
20. Integration retry state must remain distinct from the authoritative revenue business fact.
21. A2 does not introduce invoices, receipts, payments, accounting, ledger, or profitability.
22. A2 reuses existing CDCS-EMP platform architecture.
23. A2 remains reusable and is not SSRC-specific in its domain model.
24. C5 consumes the established A2 revenue fact rather than reconstructing it.
25. A2 changes to ownership, persistence, lifecycle, or integration boundaries require architectural review.

---

## 23. Implementation Sequencing

A2 implementation shall proceed only after this architecture is approved.

The controlled implementation sequence is:

### A2.1 — Revenue Domain Model

Establish the Catering-owned revenue record using the existing CDCS-EMP model architecture.

### A2.2 — Revenue Recognition Contract

Define the explicit recognition/eligibility boundary without embedding Finance processing.

### A2.3 — Revenue Classification / Source Context

Establish the minimum Catering-owned classification and source/reference information required by the pilot.

### A2.4 — Revenue Workflow and Service

Implement controlled revenue lifecycle transitions using the existing workflow/service architecture.

### A2.5 — Revenue Persistence and Audit

Add migration, repository/service persistence, audit, and validation according to existing platform conventions.

### A2.6 — Revenue Integration Boundary Preparation

Expose the authoritative revenue fact in a form that C5 can consume without reconstructing or duplicating it.

C5 implementation shall follow only after A2 and the C5 contribution contract are reconciled against A1.

---

## 24. Acceptance Criteria

A2 is considered implemented when:

- a distinct Catering Revenue business record exists;
- Catering remains authoritative for the originating revenue fact;
- revenue recognition/eligibility is explicit and auditable;
- revenue is not inferred solely from Event status;
- quotation acceptance does not automatically create recognized revenue;
- revenue amount is explicitly represented;
- currency is explicit;
- revenue date/recognition date is explicitly represented;
- applicable customer and event references are traceable;
- stable Catering Revenue identity exists;
- revenue lifecycle is controlled;
- existing CDCS-EMP audit architecture is reused;
- no Finance accounting fields are introduced into Catering;
- no Finance repositories or persistence are accessed directly;
- no cross-module Finance foreign keys are introduced;
- A2 can provide the authoritative source fact required by C5;
- implementation remains reusable for future CDCS-EMP clients;
- focused A2 tests pass;
- relevant Catering regression tests pass;
- the full project suite passes at the appropriate stage checkpoint;
- architecture documentation and implementation remain reconciled.

---

## 25. Relationship to A1

A2 complements the approved **A1 — Finance Domain & Contract Definition** architecture.

A1 establishes:

- Finance ownership;
- Finance Revenue Record;
- Finance revenue classification;
- Finance lifecycle;
- Finance financial treatment;
- Finance audit;
- Finance-side idempotency;
- Finance integration contract.

A2 establishes:

- Catering ownership;
- Catering Revenue Record;
- Catering revenue recognition/eligibility;
- Catering revenue amount;
- Catering revenue date;
- Catering source identity;
- applicable customer/event context;
- Catering-side audit and lifecycle.

Together:

```text
A2
Catering Revenue Capability
        ↓
Authoritative Catering Revenue
        ↓
C5 Contribution Contract
        ↓
Enterprise Integration Boundary
        ↓
A1
Finance Revenue Capability
        ↓
Finance-owned Financial Record
```

Neither capability absorbs the ownership of the other.

---

## 26. Relationship to C5

C5 is the enterprise integration boundary between A2 and Finance.

A2 establishes the business fact.

C5 communicates the business fact.

Finance establishes the financial representation.

Therefore:

> **A2 ≠ C5 ≠ Finance Revenue Capability**

A2 must not implement C5 delivery logic merely to establish revenue.

C5 must not implement A2 revenue recognition merely to deliver revenue.

Finance must not reconstruct the Catering business fact from unrelated Catering records.

---

## 27. Relationship to A3, A4 and B7

### A3 — Invoice & Receipt Capability

A3 introduces invoice and receipt capability where required.

Invoices and receipts are Finance-owned financial documents and are not part of the A2 Revenue Record.

### A4 — Catering Financial History & Summaries

A4 provides focused financial history and basic summaries using approved financial records.

A4 does not redefine revenue ownership.

### B7 — Revenue & Profitability

B7 connects Catering revenue with Catering costing for event-level operational profitability.

The intended relationship is:

```text
Recognized Catering Revenue
        −
Recognized Catering Cost
        =
Operational Profitability
```

Profitability remains a Catering business capability and does not transfer ownership of the revenue or cost records to a profitability subsystem.

---

## 28. Governance

This architecture is governed by the existing CDCS-EMP architecture and business-module governance.

Changes affecting any of the following require architectural review:

- Catering Revenue ownership;
- revenue recognition boundary;
- Revenue persistence;
- Revenue lifecycle;
- Finance integration boundary;
- cross-module identity;
- cross-module persistence;
- transaction boundary;
- audit boundary;
- idempotency boundary;
- Finance ownership;
- Catering profitability ownership.

Any approved change must be reconciled with:

- A1 — Finance Domain & Contract Definition;
- C5 — Catering → Finance Revenue Integration;
- the SSRC-IBMS Pilot Readiness Implementation Roadmap.

---

## 29. Decision Summary

The approved A2 architecture establishes the following model:

```text
Catering Business Activity
        ↓
Explicit Revenue Recognition Decision
        ↓
Authoritative Catering Revenue
        ↓
Stable Catering Revenue Identity
        ↓
C5 Revenue Contribution
        ↓
Enterprise Integration Boundary
        ↓
Finance Revenue Capability
        ↓
Finance-owned Financial Record
```

The fundamental ownership principle is:

> **Catering owns the originating revenue business fact; Finance owns its financial representation and treatment.**

This preserves a single authoritative source for the Catering revenue fact, prevents duplicate financial ownership, supports durable integration and retry, and provides the foundation required for C5 without prematurely expanding the pilot into a full accounting or ERP Finance subsystem.

**Status: APPROVED**

# Phase 4 — Focused Finance Domain & Contract Definition

**Status:** Approved
**Decision Type:** Architecture / Domain Contract
**Phase:** Phase 4 — Focused Finance
**Scope:** CDCS-EMP reusable platform and SSRC-IBMS pilot
**Primary Dependencies:** ADR-001, existing Enterprise Integration Framework, Phase 2.2 Procurement–Finance Integration Contract, SSRC-IBMS Pilot Readiness Implementation Roadmap
**Related Roadmap Components:** A1, A2, A3, A4, C5

---

## 1. Purpose

This decision establishes the bounded Finance capability required by the SSRC-IBMS pilot and defines the domain and integration contracts that will govern its implementation.

The Finance capability is intentionally **focused**. It provides the minimum reusable financial domain required to represent Catering revenue and related financial records without introducing a full accounting or ERP Finance subsystem prematurely.

This decision establishes:

- Finance as a bounded business module;
- Finance-owned financial records;
- Finance-owned revenue representation;
- Finance-owned revenue classification;
- Finance revenue lifecycle principles;
- financial source and reference traceability;
- business identity and idempotency boundaries;
- Finance integration boundaries;
- compatibility with the existing Procurement → Finance architecture;
- the dependency boundary between A1, A2, A3, A4 and C5;
- explicit exclusions from the focused Finance capability.

This decision does **not** define Catering's revenue-recognition rules. Those belong to **A2 — Catering Revenue Capability**.

---

## 2. Architectural Context

CDCS-EMP Phase 2 establishes reusable bounded business modules operating within a shared enterprise application platform.

ADR-001 defines the architectural principle that business capabilities are implemented as bounded modules which:

- own clearly defined business capabilities and authoritative business data;
- reuse the existing application, persistence, transaction, authorization, audit and integration infrastructure;
- do not create parallel enterprise frameworks;
- communicate across module boundaries through explicit contracts;
- avoid duplicate ownership of enterprise-wide concepts.

The existing Procurement → Finance integration architecture establishes that:

- Procurement owns Procurement business facts;
- Finance owns financial treatment and Finance financial records;
- Finance determines the financial consequence of information communicated by Procurement;
- Procurement must not directly persist or mutate Finance-owned records;
- Finance must not directly persist or mutate Procurement-owned records;
- cross-module persistence and direct repository access are prohibited;
- cross-module communication uses the Enterprise Integration Framework;
- integration-delivery state is distinct from Finance accounting or financial records;
- an integration request identifies a delivery attempt and is not itself the underlying business identity.

The focused Finance capability established by this decision follows the same architecture.

---

## 3. Decision

CDCS-EMP shall implement Finance as a normal bounded business module using the existing CDCS-EMP module architecture.

Finance shall own the financial records and financial processing introduced by the focused Finance capability.

For the initial pilot scope, the Finance capability shall establish a reusable foundation for:

- financial revenue representation;
- revenue classification;
- financial transaction context required by the supported capability;
- financial source and reference traceability;
- controlled financial lifecycle;
- audit information;
- idempotent receipt of cross-module financial contributions;
- financial history and basic summaries through A4;
- future invoice and receipt capability through A3.

Finance shall reuse:

- the existing module discovery and lifecycle framework;
- existing models and persistence conventions;
- existing repositories;
- existing services;
- existing workflow and execution architecture;
- existing authorization and RBAC;
- existing audit infrastructure;
- existing transaction infrastructure;
- existing Enterprise Integration Framework;
- existing post-commit execution architecture;
- existing reporting framework.

Finance shall not introduce a parallel application framework, transaction framework, persistence framework, security subsystem, integration framework or enterprise identity mechanism.

---

# 4. Finance Ownership Boundary

## 4.1 Finance owns

Finance is authoritative for:

- Finance-owned financial records;
- financial revenue records;
- Finance revenue classifications;
- financial status/lifecycle;
- financial source and reference representation;
- financial audit information;
- financial treatment within the focused capability;
- Finance-side idempotency/consumption identity;
- financial history;
- financial summaries;
- invoices and receipts when A3 is implemented;
- future payment and settlement capabilities when explicitly introduced;
- future accounting and ledger capabilities when explicitly introduced.

## 4.2 Other modules remain authoritative for their business facts

Catering remains authoritative for:

- Catering customers;
- Catering events;
- Catering quotations;
- Catering operational workflow;
- Catering production and delivery context;
- the originating Catering revenue business fact established through A2;
- Catering costing context;
- event-level profitability.

Procurement remains authoritative for:

- suppliers;
- purchase requirements;
- purchase requests;
- purchase orders;
- Procurement lifecycle;
- Procurement approvals;
- Procurement integration-delivery state.

Inventory remains authoritative for:

- stock items;
- inventory locations;
- stock balances;
- stock movements;
- stock transfers;
- physical stock effects.

Expense Management remains authoritative for:

- operational expense records;
- expense classifications;
- expense lifecycle;
- approved expense business facts.

Reporting remains a consumer of approved business data and does not become authoritative for Finance records.

---

# 5. Finance Revenue Domain

## 5.1 Finance Revenue Record

The focused Finance capability shall provide a Finance-owned revenue record representing a financial revenue fact received or established through an approved Finance capability.

The Finance Revenue Record shall be distinct from:

- the Catering revenue record;
- the Catering event;
- the customer record;
- the integration request;
- the integration-delivery state;
- an invoice;
- a receipt;
- a payment;
- an accounting ledger entry.

The Finance Revenue Record is a Finance-owned representation of financial revenue.

## 5.2 Revenue source

Every Finance revenue record originating from another business module shall retain sufficient source information to identify the authoritative originating business fact.

For Catering-originated revenue, the Finance representation shall be traceable to:

- the originating Catering revenue identity;
- the applicable Catering event identity where one exists;
- the applicable customer identity where one exists;
- the source business context required for audit.

These relationships shall be represented through business identifiers and references rather than cross-module foreign keys.

Finance shall not become owner of the Catering event or Catering revenue record merely because those identifiers are stored for traceability.

---

# 6. Revenue Classification

Revenue classification is Finance-owned.

Finance shall determine and maintain the classification applicable to financial revenue records.

The classification mechanism shall be explicit and reusable and shall follow the established CDCS-EMP pattern for bounded business master data.

Catering shall not maintain a parallel Finance accounting or financial classification system merely to support revenue integration.

A Catering-originated contribution may communicate source classification/context where required by the approved integration contract, but Finance remains authoritative for Finance-side classification and financial treatment.

---

# 7. Revenue Amount and Currency

Finance revenue amounts shall use the established CDCS-EMP monetary convention.

Persisted monetary values shall use appropriate fixed-precision numeric storage consistent with the existing platform convention, including the established `Numeric(18,2)` pattern where applicable.

Domain contracts shall use `Decimal` for monetary values.

Finance shall not independently recalculate or redefine an authoritative Catering revenue amount when consuming an approved Catering revenue contribution.

The originating business capability remains authoritative for the business fact it communicates.

Finance determines the financial representation and treatment of that fact.

Currency shall be explicit wherever a financial amount is represented.

A financial contribution shall not rely on an implicit currency assumption.

---

# 8. Revenue Date and Recognition Context

A Finance revenue record shall retain an explicit financial date appropriate to its domain semantics.

The distinction between:

- business event date;
- revenue recognition date;
- integration delivery time;
- record creation time;

shall be preserved.

A Catering event date shall not automatically be treated as the Finance revenue recognition date.

A Finance integration request timestamp shall not become the revenue date merely because the request was delivered at that time.

The exact recognition rule for Catering revenue shall be established by **A2 — Catering Revenue Capability** and communicated through the approved C5 contribution contract.

Finance shall apply its own Finance-side lifecycle and treatment rules to the received business fact.

---

# 9. Revenue Lifecycle

Finance revenue shall have an explicit lifecycle governed through the established CDCS-EMP workflow/service architecture.

The lifecycle shall distinguish the financial record's business state from the state of an external integration delivery attempt.

In particular:

- a Finance revenue record is a business record;
- integration delivery state is operational delivery state;
- integration success does not automatically mean every downstream accounting action has occurred;
- failure of a post-commit integration attempt does not invalidate an already-committed originating business fact.

The exact Finance revenue workflow states and transitions shall be defined during implementation from this contract.

They shall not be copied mechanically from Expense Management or Catering Event workflows.

---

# 10. Audit and Traceability

Finance records shall use the existing enterprise audit and timestamp conventions.

Finance shall preserve sufficient information to answer:

1. What financial record was created?
2. What business fact caused it to be created?
3. Which module was the source?
4. Which source business record was communicated?
5. Which contribution identity was used?
6. When was the financial record created or updated?
7. Who or what initiated the relevant Finance operation?
8. What integration delivery attempt communicated the business fact where applicable?

Enterprise integration audit information and Finance business-record audit information remain distinct.

An integration audit record is not itself a Finance accounting or revenue record.

---

# 11. Identity and Idempotency

## 11.1 Three distinct identities

The architecture shall preserve three separate identities:

```text
Catering Revenue Identity
        ≠
Finance Revenue Identity
        ≠
Integration Request Identity
```

### Catering Revenue Identity

Identifies the authoritative Catering revenue business fact.

It is owned by Catering/A2.

### Finance Revenue Identity

Identifies the Finance-owned financial revenue record.

It is owned by Finance.

### Integration Request Identity

Identifies an individual enterprise integration delivery request.

It is generated by the Enterprise Integration Framework and identifies the delivery attempt.

An integration request identifier shall not be used as the business idempotency identity.

---

## 11.2 Stable contribution identity

The C5 Catering → Finance integration shall communicate a stable contribution identity.

The identity shall remain stable across retries of the same business contribution.

Repeated delivery of the same contribution shall therefore be recognizable as the same underlying business operation.

A new `IntegrationRequest.request_id` on retry shall not cause a second Finance revenue record to be created.

---

## 11.3 Finance idempotency

Finance shall provide a durable mechanism for preventing duplicate representation of the same accepted business contribution.

The mechanism shall:

- use a stable business contribution identity;
- survive individual integration request retries;
- distinguish duplicate delivery from a new business contribution;
- remain Finance-owned;
- support auditability.

The exact persistence structure shall be established during Finance implementation.

It shall not be embedded into the generic `IntegrationRequest` model.

---

# 12. Customer and Event References

Finance may retain customer and event identifiers as business references when required for financial traceability.

These references shall not create cross-module foreign keys.

Therefore:

```text
Finance Revenue
    ├── customer_reference
    └── source_event_reference
```

does not imply:

```text
Finance Revenue
    ├── FK → Catering Customer
    └── FK → Catering Event
```

Finance does not own the source entities.

This preserves the established CDCS-EMP module ownership boundary and prevents persistence coupling between business modules.

---

# 13. Finance Integration Contract

## 13.1 Enterprise boundary

Cross-module Finance communication shall use the existing Enterprise Integration Framework:

```text
Domain Contribution
        ↓
IntegrationRequest
        ↓
IntegrationService
        ↓
Registered Finance Provider
        ↓
Finance Capability
        ↓
Finance-owned Persistence
```

The existing Finance provider identity shall remain:

```text
finance
```

The Enterprise Integration Provider Registry shall remain generic and shall not acquire Finance-specific knowledge.

---

## 13.2 Explicit operations

Finance integration operations shall be explicitly supported by the Finance provider.

The existing Procurement operation shall remain independently defined:

```text
procurement_commitment
```

C5 shall introduce a separate Finance operation for Catering revenue.

The exact operation constant/name shall be established during C5 implementation after A2 has established the final Catering revenue contribution contract.

C5 shall not reuse the Procurement financial-effect payload merely because both integrations target Finance.

---

# 14. Procurement → Finance Compatibility

This Finance domain decision does not supersede or alter the existing Procurement → Finance integration contract.

The existing Procurement architecture remains authoritative for:

- Procurement ownership;
- Procurement commitment representation;
- Procurement integration-delivery state;
- Procurement contribution identity;
- Procurement-specific Finance operation;
- Procurement retry and delivery state.

Finance remains authoritative for the financial consequence of Procurement information.

The existing `ProcurementFinanceCommitment` remains Procurement-owned integration-delivery state.

It is not a Finance financial record.

The implementation of the actual Finance revenue capability shall therefore coexist with, rather than replace, the existing Procurement Finance integration boundary.

---

# 15. Catering → Finance Contract Boundary

C5 shall establish the integration boundary between A2 and Finance.

The conceptual flow is:

```text
Catering Revenue Capability
        ↓
CateringRevenueContribution
        ↓
Post-Commit Boundary
        ↓
IntegrationRequest
(provider = "finance")
        ↓
Finance Provider
(operation = approved C5 operation)
        ↓
Finance Revenue Capability
        ↓
Finance-owned Revenue Record
```

The contribution shall communicate an already-established Catering revenue business fact.

It shall not instruct Finance how to perform accounting.

---

# 16. C5 Post-Commit Boundary

C5 shall use the existing `PostCommitExecutor` architecture.

The originating Catering transaction shall complete and commit before Finance delivery is attempted.

Therefore:

```text
Catering transaction
        ↓
COMMIT
        ↓
PostCommitExecutor
        ↓
Finance integration
```

Finance integration shall not be performed inside the originating Catering transaction.

A Finance integration failure after the Catering transaction commits shall not:

- roll back Catering;
- reject the Catering transaction;
- invalidate the Catering revenue fact;
- alter Catering revenue ownership.

The failure shall remain observable and retryable according to the applicable integration lifecycle.

---

# 17. Relationship to A2 — Catering Revenue Capability

A1 establishes the Finance side of the boundary.

A2 establishes the Catering side.

A2 shall determine:

- what constitutes Catering revenue;
- when revenue becomes recognized/eligible;
- the authoritative Catering revenue amount;
- the authoritative revenue date;
- the Catering revenue identity;
- the applicable customer/event relationship;
- the Catering revenue lifecycle;
- the source information required for integration.

C5 shall consume those established facts.

C5 shall not infer revenue eligibility merely because a Catering Event reaches `COMPLETED`.

Likewise, Finance shall not infer Catering revenue recognition solely from an event status.

An explicit A2 revenue fact is required.

---

# 18. Relationship to A3 — Invoice & Receipt Capability

Invoices and receipts are Finance-owned capabilities.

They are not part of the A1 revenue-domain definition beyond establishing the ownership boundary.

A3 shall define:

- invoice representation;
- receipt representation;
- invoice/receipt lifecycle;
- references to applicable financial records;
- customer-facing financial documentation;
- integration and audit requirements.

A1 shall not prematurely implement invoice or receipt processing.

A Catering quotation is not a Finance invoice.

A Catering operational receipt is not automatically a Finance receipt.

---

# 19. Relationship to A4 — Financial History & Summaries

A4 shall provide Finance-facing financial history and basic summaries required by the focused pilot.

A4 shall consume Finance-owned financial records.

Reporting/history capabilities shall not become alternative sources of financial truth.

A4 shall not create duplicate revenue ownership.

The Finance Revenue Record remains authoritative.

---

# 20. Relationship to Catering Profitability

Event-level profitability remains a Catering business capability.

The focused Finance capability does not own Catering profitability.

The future Catering profitability flow is:

```text
Catering Revenue
       +
Recognized Catering Cost
       ↓
Catering Profitability
```

Finance may provide financial records consumed by reporting or other approved business capabilities, but Finance shall not absorb Catering's operational profitability ownership.

This remains aligned with the roadmap's **B7 — Revenue & Profitability** capability.

---

# 21. Explicit Exclusions

The following are outside the scope of A1:

- full general ledger;
- chart of accounts;
- journal-entry subsystem;
- comprehensive accounting engine;
- tax engine;
- payment processing;
- supplier settlement;
- banking integration;
- payroll accounting;
- full accounts payable;
- full accounts receivable;
- budgeting;
- financial planning;
- advanced financial consolidation;
- automated accounting allocation;
- independent Catering revenue recognition rules;
- Catering costing;
- event profitability calculation;
- duplicate Finance persistence inside Catering;
- direct Finance repository access from other modules;
- direct cross-module database access;
- cross-module foreign keys;
- distributed transactions.

These capabilities may be introduced through future explicitly approved architecture decisions.

---

# 22. Architectural Invariants

The following invariants are mandatory.

1. **Finance is a bounded business module.**

2. **Finance owns Finance financial records.**

3. **Catering remains authoritative for its originating revenue business fact.**

4. **Procurement remains authoritative for Procurement business facts.**

5. **Integration-delivery state is distinct from Finance financial records.**

6. **Integration request identity is distinct from business contribution identity.**

7. **Finance revenue identity is distinct from Catering revenue identity.**

8. **Finance classification is Finance-owned.**

9. **Finance determines Finance-side financial treatment.**

10. **Cross-module references use business identifiers, not cross-module foreign keys.**

11. **Cross-module Finance communication uses the Enterprise Integration Framework.**

12. **The generic IntegrationRequest contract is not modified for Finance-specific business fields.**

13. **Finance provider operations are explicitly supported.**

14. **Procurement's existing Finance operation remains independent of Catering revenue integration.**

15. **C5 uses the post-commit boundary.**

16. **A committed Catering transaction is not rolled back because Finance delivery fails.**

17. **C5 does not infer revenue eligibility from Catering Event status alone.**

18. **Finance does not independently redefine an authoritative Catering revenue amount.**

19. **Invoices and receipts remain A3 capabilities.**

20. **Financial history and summaries remain A4 capabilities.**

21. **Catering profitability remains a Catering capability.**

22. **No duplicate financial ownership is created inside Catering.**

23. **No direct Finance repository or persistence access is permitted from Catering, Procurement, or other modules.**

24. **No direct cross-module persistence is permitted.**

25. **Finance implementation shall reuse existing CDCS-EMP enterprise infrastructure.**

26. **New enterprise-wide abstractions shall not be introduced without an independently justified architectural requirement.**

---

# 23. Implementation Sequencing

A1 establishes the architecture and contract foundation.

The implementation sequence shall be:

```text
A1 — Finance Domain & Contract Definition
        ↓
A2 — Catering Revenue Capability
        ↓
A3 — Invoice & Receipt Capability
        ↓
A4 — Financial History & Summaries
        ↓
C5 — Catering → Finance Revenue Integration
        ↓
B7 — Revenue & Profitability
```

The exact implementation order may be adjusted where dependencies require it, but C5 shall not be implemented against undefined revenue semantics.

At minimum:

- A1 must establish the Finance-side contract before Finance implementation;
- A2 must establish the authoritative Catering revenue fact before C5;
- C5 must use the resulting A1/A2 contract;
- A3 must not be simulated inside A1;
- A4 must consume Finance-owned records rather than create parallel financial truth.

---

# 24. Acceptance Criteria for A1

A1 is considered architecturally complete when:

- Finance is explicitly established as a bounded CDCS-EMP business module;
- Finance ownership is distinct from Catering, Procurement, Inventory and Expense ownership;
- Finance revenue representation is defined;
- Finance classification ownership is defined;
- amount, currency and date principles are defined;
- source/reference traceability is defined;
- customer/event references are defined without cross-module FKs;
- audit requirements are defined;
- Finance revenue lifecycle principles are defined;
- business identity and integration request identity are explicitly separated;
- durable Finance idempotency is required;
- the existing Finance provider boundary is preserved;
- the existing Procurement → Finance contract remains compatible;
- the C5 contribution boundary is defined;
- post-commit delivery is required for C5;
- failure isolation is defined;
- A2/A3/A4 ownership dependencies are explicit;
- profitability remains outside Finance ownership;
- no full accounting/ERP Finance subsystem is introduced prematurely.

---

# 25. Decision Summary

CDCS-EMP shall establish a focused, reusable Finance business module that owns financial representation while preserving the authority of originating business modules.

The Finance architecture follows the established enterprise pattern:

```text
Business Module
      ↓
Authoritative Business Fact
      ↓
Explicit Contribution Contract
      ↓
Enterprise Integration Boundary
      ↓
Finance Capability
      ↓
Finance-owned Financial Record
```

For Catering revenue specifically:

```text
Catering / A2
      ↓
Authoritative Catering Revenue
      ↓
C5 Contribution
      ↓
Post-Commit
      ↓
Enterprise Finance Provider
      ↓
Finance Revenue Capability
      ↓
Finance Revenue Record
```

The central ownership rule is:

> **Catering owns the originating revenue business fact; Finance owns the resulting financial representation and financial treatment.**

The central integration rule is:

> **Cross-module financial communication occurs through explicit contracts and the Enterprise Integration Framework, not through shared persistence or direct repository access.**

The central reliability rule is:

> **A stable business contribution identity must survive delivery retries so that revenue is represented once.**

The central scope rule is:

> **Focused Finance provides the minimum financial capability required by the pilot and does not become a prematurely implemented full accounting or ERP subsystem.**

This decision establishes the approved architectural foundation for **A2 — Catering Revenue Capability**, **A3 — Invoice & Receipt Capability**, **A4 — Financial History & Summaries**, and ultimately **C5 — Catering → Finance Revenue Integration**.

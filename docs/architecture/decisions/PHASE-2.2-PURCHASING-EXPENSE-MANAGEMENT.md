# CDCS-EMP — Phase 2.2 Architecture Decision Record

## Purchasing & Expense Management

**Status:** Approved / Active
**Decision Date:** 10 September 2026
**Documentation Date:** 10 September 2026
**Decision Type:** Phase Architecture Decision
**Phase:** Phase 2 — Business Modules
**Capability:** Purchasing & Expense Management
**Scope:** Capability ownership, bounded-domain boundaries, and integration principles
**Related ADRs:** ADR-001, ADR-008, ADR-015
**Authoritative Roadmap:** `PHASE-2-AUTHORITATIVE-ROADMAP.md`

---

## 1. Decision Summary

Phase 2.2 — Purchasing & Expense Management shall be implemented as bounded business capabilities that consume the existing CDCS-EMP enterprise platform and remain distinct from Catering, Inventory, and future Finance responsibilities.

Phase 2.2 shall establish clear ownership for:

* Procurement / Purchasing;
* Expense Management;
* Catering integration;
* Procurement / Purchasing ↔ Inventory integration;
* Procurement / Purchasing ↔ Finance integration; and
* cross-domain reporting consumption.

No Phase 2.2 capability shall introduce a parallel application, persistence, security, workflow, transaction, audit, reporting, or other enterprise infrastructure where an existing CDCS-EMP platform capability already provides the required contract.

This document is the authoritative architecture record for Phase 2.2. It is established at Phase 2.2.1 and shall be maintained as subsequent Phase 2.2 architectural decisions are approved.

---

## 2. Context

The Phase 2 roadmap identifies Purchasing & Expense Management as a future bounded capability distinct from Inventory.

The Catering functional specification identifies purchasing, supplier interaction, inventory receiving, expenses, invoices, payments, and financial integration as related concerns. However, that specification is a draft requirements document and does not establish the authoritative ownership of those concerns within CDCS-EMP.

Existing Phase 2 architecture has already established:

* business modules as bounded capabilities;
* Catering ownership of its business domain;
* Inventory ownership of physical stock effects;
* enterprise transaction infrastructure;
* enterprise security and governance;
* enterprise workflow;
* enterprise audit and events; and
* enterprise reporting infrastructure.

Phase 2.2 therefore requires an explicit architectural boundary before Procurement/Purchasing and Expense Management implementation begins.

The primary architectural risk is allowing related operational and financial concepts to collapse into a single subsystem or allowing Catering to create private purchasing or expense infrastructure.

---

## 3. Approved Capability Ownership Matrix

| Capability | Owns | Does Not Own |
|---|---|---|
| **Catering** | Customers, catering requests, events, menus, event requirements, production/delivery context, event costing context | Suppliers, purchase requests, purchasing transactions, expenses, payments, financial ledgers |
| **Procurement / Purchasing** | Suppliers, sourcing, purchase requirements/requests, approvals, purchasing transactions, procurement lifecycle | Physical stock balances, stock ledger, expenses, accounting ledger |
| **Inventory** | Stock items, locations, balances, movements, transfers, thresholds/configuration, physical stock effects | Suppliers, purchasing lifecycle, expenses, invoices, payments, accounting ledger |
| **Expense Management** | Expense records, classifications, expense lifecycle, expense-related business rules | Purchasing lifecycle, supplier master, stock balances, accounting ledger |
| **Finance** | Financial treatment, expenses as financial transactions, invoices, payments, receipts, income, accounting/financial ledger | Operational purchasing workflow, physical inventory, catering operations |
| **Reporting** | Cross-domain reporting/read models and analytical consumption | Ownership of operational or financial transactions |

The matrix above is approved as the Phase 2.2 capability ownership baseline.

---

## 4. Bounded Business Responsibilities

### 4.1 Catering

Catering owns the operational context in which catering services are planned and delivered.

Catering may identify and communicate a business need for goods or services, but it shall not own the procurement transaction created to satisfy that need.

Catering shall not create a private supplier master, purchase-request subsystem, purchasing ledger, or expense ledger.

### 4.2 Procurement / Purchasing

Procurement / Purchasing owns the sourcing and purchasing lifecycle.

This includes, subject to subsequent detailed design:

* supplier management;
* purchase requirements and purchase requests;
* sourcing;
* approval;
* purchase transactions;
* procurement status and lifecycle;
* supplier-facing purchasing information; and
* procurement-side receiving/handover processes where applicable.

Procurement / Purchasing does not own the physical inventory ledger or the financial ledger.

### 4.3 Inventory

Inventory owns the physical stock state.

Its responsibilities include:

* stock items;
* locations;
* stock balances;
* stock movements;
* stock transfers;
* thresholds and related configuration; and
* physical stock effects.

Procurement / Purchasing may cause a receiving event that results in a stock effect, but Inventory remains authoritative for the physical stock record.

### 4.4 Expense Management

Expense Management is a distinct bounded capability concerned with operational expense records and expense lifecycle rules.

Expense Management shall not absorb the procurement lifecycle merely because a purchase may eventually result in an expense.

### 4.5 Finance

Finance is a future bounded business capability.

Finance shall remain authoritative for financial treatment, including the financial ledger and financial representations of expenses, invoices, payments, receipts, and income.

Phase 2.2 shall not create a private accounting or financial ledger in Procurement, Catering, Inventory, or Expense Management.

### 4.6 Reporting

Reporting consumes approved cross-domain information through explicit reporting interfaces or read models.

Reporting does not become the owner of operational or financial transactions.

---

## 5. Approved Domain Distinctions

The following distinctions are architectural invariants for Phase 2.2.

### 5.1 Catering Purchase Requirement ≠ Procurement Purchase Request

A **Catering Purchase Requirement** expresses an operational need.

Example:

> Catering requires 25 kg of rice for Event X.

A **Procurement Purchase Request** represents the procurement action required to source and purchase that requirement.

Example:

> Procurement shall source and purchase 25 kg of rice from an approved supplier.

These concerns shall not be represented as one collapsed entity merely because they are related.

### 5.2 Purchase ≠ Expense

A purchase represents an operational procurement transaction.

An expense represents an expense record and, ultimately, its financial treatment.

A purchase may lead to an expense or financial liability, but the concepts are not interchangeable.

### 5.3 Physical Receipt ≠ Financial Expense

A physical stock receipt represents goods entering an Inventory-controlled location.

A financial expense represents financial treatment of an obligation or cost.

The two may be causally related but shall remain separate domain responsibilities.

### 5.4 Procurement Receiving ≠ Inventory Ownership

Procurement may own the procurement-side receiving or supplier handover process.

Inventory owns the resulting physical stock effect.

The integration contract shall explicitly cross that boundary.

---

## 6. Approved Integration Boundaries

The Phase 2.2 architecture shall use explicit integration boundaries.

```text
Catering
    │
    │ Purchase Requirement
    ▼
Procurement / Purchasing
    │
    ├──── Supplier / Purchase
    │
    ├──────────────► Inventory
    │                Physical Receipt / Stock Effect
    │
    └──────────────► Finance
                     Financial Effect

Expense Management
        │
        ▼
      Finance

Catering / Procurement / Inventory / Finance
                    │
                    ▼
                Reporting
```

### 6.1 Catering → Procurement / Purchasing

Catering shall communicate purchase requirements or procurement references through an explicit integration boundary.

Catering shall consume reusable Procurement / Purchasing capabilities rather than implementing a private purchasing subsystem.

### 6.2 Procurement / Purchasing → Inventory

Procurement / Purchasing may initiate or communicate a receiving event.

Inventory shall remain authoritative for:

* stock movement;
* stock balance;
* physical stock state; and
* stock-effect posting.

The receiving integration shall not allow Procurement to directly own or duplicate the Inventory stock ledger.

### 6.3 Procurement / Purchasing → Finance

Procurement / Purchasing may communicate approved financial effects to Finance.

Finance shall remain authoritative for financial treatment and accounting records.

Procurement shall not implement a private accounting ledger or financial settlement engine.

### 6.4 Expense Management → Finance

Expense Management shall communicate expense information to Finance through an explicit boundary.

Finance shall own the resulting financial treatment.

### 6.5 Cross-domain → Reporting

Reporting shall consume approved information from the relevant bounded capabilities.

Cross-domain reporting shall not require those capabilities to surrender ownership of their operational data.

---

## 7. Explicit Phase 2.2 Exclusions

The following are explicitly outside the Phase 2.2 implementation boundary unless a later approved architectural decision changes the scope:

* General Ledger / accounting engine;
* Chart of Accounts;
* Accounts Payable engine;
* tax engine;
* payroll;
* budget-management engine;
* full general invoicing subsystem;
* general payment-processing subsystem;
* supplier financial settlement engine;
* general financial reporting;
* private Catering purchasing subsystem;
* private Catering expense ledger; and
* duplicate enterprise infrastructure.

The future Finance capability remains a separate bounded capability.

---

## 8. Existing Platform Reuse

Phase 2.2 shall consume established CDCS-EMP platform capabilities, including where applicable:

* module discovery and lifecycle;
* enterprise data and CRUD infrastructure;
* repositories and query contracts;
* validation;
* services;
* workflow;
* execution;
* authentication and authorization;
* security and governance;
* audit;
* events;
* notifications;
* transaction infrastructure; and
* reporting.

Procurement, Purchasing, and Expense Management shall introduce module-specific abstractions only where required by genuine business-domain rules.

---

## 9. Security & Governance Principles

Phase 2.2 business capabilities shall follow the existing CDCS-EMP security and governance model.

Accordingly:

1. business capabilities shall define their own business permissions within the established permission architecture;
2. authorization shall be enforced through enterprise authorization boundaries;
3. business operations shall respect established execution and governance rules;
4. mutations shall use the established transaction infrastructure;
5. auditable business events shall use the enterprise event architecture;
6. workflow state transitions shall remain explicit and governed; and
7. repositories shall remain persistence-oriented rather than becoming authorization, workflow, or transaction owners.

Detailed permission, workflow, transaction, and audit decisions shall be documented during the corresponding Phase 2.2 design stages.

---

## 10. Architectural Principles Locked for Phase 2.2

The following principles are locked:

### 10.1 Existing Platform First

Use established CDCS-EMP enterprise infrastructure before introducing new infrastructure.

### 10.2 Bounded Business Ownership

Each business capability owns its own authoritative business concerns.

### 10.3 No Duplicate Infrastructure

Business modules shall not create parallel versions of enterprise services.

### 10.4 Explicit Cross-Module Integration

Related capabilities shall communicate through explicit contracts rather than direct ownership leakage.

### 10.5 Security and Governance by Default

Security, authorization, audit, workflow, execution, and transaction governance are part of the architecture rather than optional additions.

### 10.6 Physical and Financial Separation

Physical stock effects, procurement transactions, operational expenses, and financial treatment shall remain distinct concerns.

---

## 11. Phase 2.2 Implementation Direction

The detailed implementation sequence remains subject to validation during the Phase 2.2 design stages.

The current approved direction is:

```text
Phase 2.2 Design
       │
       ▼
Procurement Foundation
       │
       ▼
Procurement Operational Surface
       │
       ▼
Procurement Workflow
       │
       ▼
Procurement ↔ Inventory
       │
       ▼
Expense Foundation
       │
       ▼
Expense Operational Surface
       │
       ▼
Expense Workflow
       │
       ▼
Procurement ↔ Finance
       │
       ▼
Catering Integration
       │
       ▼
Reporting Integration
```

This sequence is an implementation direction rather than a license to predefine entities or contracts before the corresponding design stage.

---

## 12. Architectural Governance for Subsequent Phase 2.2 Stages

This document shall be maintained throughout Phase 2.2.

Each subsequent Phase 2.2 stage shall:

1. inspect the existing platform and affected business boundaries;
2. define and approve the relevant architectural detail;
3. update this document where the approved decision materially affects the Phase 2.2 architecture;
4. reconcile the authoritative Phase 2 roadmap where sequencing or status changes;
5. verify the affected implementation and regression surface; and
6. create a Git checkpoint after completion.

No ADR-016 is created by this document.

A new ADR shall be considered only if a genuinely new enterprise architectural decision arises that cannot reasonably be treated as an elaboration of the approved Phase 2.2 architecture.

---

## 13. Verification Requirements

Before Phase 2.2 is considered complete, verification shall cover, as applicable:

* focused domain unit tests;
* service/business-rule tests;
* repository/data tests;
* workflow tests;
* authorization/security tests;
* integration tests;
* application-surface tests;
* cross-module integration tests;
* full regression suite;
* architecture/documentation reconciliation; and
* clean Git working tree.

The exact verification scope shall be refined as the implementation stages are completed.

---

## 14. Decision Status

**Phase 2.2 — Purchasing & Expense Management architecture is approved and active.**

The capability ownership matrix and Phase 2.2.1 boundaries recorded in this document are locked as the baseline for subsequent Phase 2.2 design.

Subsequent design work shall refine these boundaries without silently transferring ownership between Catering, Procurement / Purchasing, Inventory, Expense Management, Finance, or Reporting.

---

## 15. Related Architecture Documentation

* `ADR-001-phase-2-business-module-architecture.md`
* `ADR-008-catering-inventory-domain-boundary.md`
* `ADR-015` — Inventory transaction posting boundary
* `PHASE-2-AUTHORITATIVE-ROADMAP.md`

---

## 16. Approval

**Approved by:** Project Architecture Review
**Approval Status:** Approved / Locked
**Effective Phase:** Phase 2.2 — Purchasing & Expense Management

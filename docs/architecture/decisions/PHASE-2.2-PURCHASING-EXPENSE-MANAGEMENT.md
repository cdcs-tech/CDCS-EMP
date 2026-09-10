# CDCS-EMP — Phase 2.2 Architecture Decision Record

## Purchasing & Expense Management

**Status:** Approved / Active
**Decision Date:** 10 September 2026
**Documentation Date:** 10 September 2026
**Decision Type:** Phase Architecture Decision
**Phase:** Phase 2 — Business Modules
**Capability:** Purchasing & Expense Management
**Scope:** Capability ownership, bounded-domain boundaries, integration principles, and Procurement/Purchasing domain model
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

Phase 2.2.2.1 — Procurement/Purchasing Domain Entities & Relationships is approved and locked as the first detailed Procurement/Purchasing domain model.

The approved domain model establishes the initial Procurement/Purchasing entity boundary, internal relationships, cross-module reference strategy, persistence approach, and intentionally deferred concepts.

## Phase 2.2.2.2 — Procurement Foundation Design

**Status:** APPROVED / LOCKED

### 1. Purpose

This stage establishes the technical and architectural foundation of the Procurement/Purchasing business module using the domain model approved in Phase 2.2.2.1.

The stage translates the approved Procurement/Purchasing domain boundary into the existing CDCS-EMP enterprise module architecture without prematurely implementing operational workflows, cross-module integrations, or future financial capabilities.

This stage is the foundation for subsequent Procurement/Purchasing operational development.

### 2. Scope

The Procurement Foundation shall establish:

* the Procurement/Purchasing business-module package and public module surface;
* integration with the existing CDCS-EMP module discovery and registration framework;
* the Procurement module manifest and module implementation;
* module-local SQLAlchemy domain models for the six approved Procurement entities;
* approved internal entity relationships and persistence mappings;
* standard enterprise model base classes and mixins where applicable;
* dedicated Alembic persistence migration(s);
* database-level constraints required to protect approved domain invariants;
* the minimum repository and service-layer foundation required to support the domain models;
* integration with existing platform database, module lifecycle, discovery, security, governance, audit, and testing infrastructure where applicable;
* module-level dependency declarations consistent with the approved Phase 2.2 ownership boundaries.

### 3. Approved Procurement Domain Entities

The foundation shall implement only the six entities approved and locked in Phase 2.2.2.1:

1. `Supplier`
2. `PurchaseRequirement`
3. `PurchaseRequest`
4. `PurchaseRequestLine`
5. `PurchaseOrder`
6. `PurchaseOrderLine`

No additional Procurement/Purchasing domain entities shall be introduced during this stage unless a new design decision is explicitly approved through the applicable Phase 2.2 design process.

### 4. Module Architecture

The Procurement/Purchasing capability shall be implemented as a dedicated business module under:

`app\modules\procurement`

The module shall follow the existing CDCS-EMP enterprise module architecture and shall not introduce a parallel module registration or discovery mechanism.

The module foundation shall use:

* `ModuleManifest`
* `BaseModule`
* existing module discovery
* existing module loader
* existing `ModuleManager`
* existing enterprise module lifecycle conventions

The Procurement module shall expose a package-level public API consistent with the established business-module pattern.

### 5. Module Discovery and Registration

The Procurement module shall integrate with the existing `app.core.discovery` framework.

The module shall provide:

* `manifest.py` containing `MODULE_MANIFEST`;
* a manifest referencing the Procurement `BaseModule` implementation;
* a valid and unique module code;
* appropriate module metadata;
* dependency declarations consistent with the approved architecture;
* enabled-state handling through the standard manifest mechanism.

The module discovery mechanism shall remain centralized within the platform.

Procurement shall not implement its own module discovery, registration registry, loader, or lifecycle mechanism.

### 6. Model and Persistence Architecture

Procurement domain models shall remain module-local under:

`app\modules\procurement\models`

They shall not be duplicated or promoted into `app.models` solely for convenience.

The six approved entities shall use the existing enterprise persistence conventions, including applicable:

* `BaseModel`
* timestamp behavior
* audit behavior
* soft-delete behavior
* GUID/reference conventions
* SQLAlchemy relationship conventions

Internal Procurement relationships approved in Phase 2.2.2.1 shall be represented using standard SQLAlchemy foreign keys and relationships.

Cross-module business references shall remain explicit references and shall not introduce hidden foreign-key coupling to Catering, Inventory, Finance, or other future business modules.

### 7. Persistence Migration

Procurement persistence shall be introduced through a dedicated Alembic migration following the existing migration-chain conventions.

The migration shall:

* create only the approved Procurement tables;
* establish approved internal foreign keys;
* establish required uniqueness and integrity constraints;
* use the established enterprise persistence-column conventions;
* preserve the existing Alembic migration chain;
* provide a clean downgrade path.

The migration shall not create tables belonging to Inventory, Finance, Expense Management, Catering, or other business modules.

### 8. Repository and Service Foundation

The Procurement foundation may establish module-local repositories and services where required to provide a clean application-layer boundary around the approved domain models.

Repository and service responsibilities shall remain limited to Procurement-owned data and business concerns established at this stage.

They shall not implement:

* approval workflow;
* supplier sourcing;
* quotation management;
* supplier evaluation;
* receiving;
* inventory stock effects;
* expense processing;
* financial accounting;
* payment processing;
* cross-module integration contracts.

Detailed operational behavior shall be established only during the corresponding later design stages.

### 9. Security and Governance Boundary

The Procurement module shall reuse the existing CDCS-EMP security and governance infrastructure.

Foundation implementation shall not create a separate authorization architecture.

Detailed Procurement permissions and workflow authorization shall be established as part of the appropriate operational/workflow design stages.

Any foundation-level security declarations required for module registration or platform integration shall remain minimal and consistent with existing enterprise conventions.

### 10. Explicitly Deferred

The following capabilities remain outside Phase 2.2.2.2:

* Procurement operational UI;
* Procurement routes and forms;
* Purchase Request CRUD surface;
* Purchase Order CRUD surface;
* approval workflows;
* sourcing;
* supplier quotations;
* supplier evaluation;
* procurement receiving;
* Inventory integration;
* physical stock effects;
* Expense Management;
* Finance integration;
* supplier invoices;
* supplier payments or settlement;
* accounting and general ledger;
* Catering integration;
* Reporting integration;
* budget management;
* tax processing;
* additional Procurement entities not approved in Phase 2.2.2.1.

These capabilities shall be designed and implemented only at their appropriate subsequent stages.

### 11. Architectural Invariants

The following invariants remain locked for this foundation stage:

1. Procurement/Purchasing owns the procurement lifecycle but does not own physical inventory balances or movements.
2. Procurement/Purchasing owns suppliers and purchasing transactions but does not own financial accounting or supplier settlement.
3. Purchase Requirement remains distinct from Purchase Request.
4. Purchase Request remains distinct from Purchase Order.
5. Purchase remains distinct from Expense.
6. Physical receipt remains distinct from financial expense recognition.
7. Cross-module references shall not create hidden database coupling.
8. Inventory remains authoritative for physical stock effects.
9. Finance remains authoritative for financial treatment and accounting.
10. Future cross-module integrations shall use explicit, approved boundaries.
11. The six approved Procurement entities shall not be expanded during this foundation stage without a new design decision.

### 12. Testing and Verification

The Procurement Foundation shall be verified using targeted tests covering at minimum:

* module package/import integrity;
* manifest validity;
* module discovery;
* module loading and registration;
* model import/registration;
* approved internal relationships;
* persistence constraints;
* migration behavior;
* repository/service foundation behavior where implemented;
* compatibility with the existing enterprise module architecture.

Relevant Procurement tests shall pass before the stage is considered complete.

The full test suite shall be executed at the stage boundary.

The working tree shall be clean after the corresponding Git checkpoint.

### 13. Stage Boundary

Phase 2.2.2.2 establishes the **technical Procurement/Purchasing foundation only**.

Completion of this stage does not imply that Procurement/Purchasing is operationally complete.

The next Procurement/Purchasing implementation stage shall be determined through the approved Phase 2.2 design sequence and shall be separately inspected and approved before implementation begins.

### 14. Approval Record

**Stage:** Phase 2.2.2.2 — Procurement Foundation Design

**Decision:** Approved and locked

**Approved by:** Project Architecture Review

**Approval Status:** Approved / Locked

**Effective Phase:** Phase 2.2 — Purchasing & Expense Management

**Date:** 11/09/2026

**Related Decision:** Phase 2.2.2.1 — Procurement/Purchasing Domain Entities & Relationships

**Authoritative Document:** `docs\architecture\decisions\PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

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

### 5.5 Procurement/Purchasing Domain Entities & Relationships

Phase 2.2.2.1 establishes the following six entities as the authoritative initial Procurement/Purchasing domain model:

1. Supplier
2. PurchaseRequirement
3. PurchaseRequest
4. PurchaseRequestLine
5. PurchaseOrder
6. PurchaseOrderLine

These entities form the initial Procurement/Purchasing foundation and shall remain within the Procurement/Purchasing bounded capability.

The approved conceptual relationships are:

```text
Supplier
   │
   └────────────── 1 → many
                         PurchaseOrder
                              │
                              └────────────── 1 → many
                                                    PurchaseOrderLine


PurchaseRequirement
   │
   └────────────── 1 → many
                         PurchaseRequest
                              │
                              ├────────────── 1 → many
                              │                    PurchaseRequestLine
                              │
                              └────────────── 1 → many
                                                   PurchaseOrder
```

The relationships above establish the following cardinalities:

| Relationship | Cardinality |
|---|---|
| Supplier → PurchaseOrder | 1 → many |
| PurchaseRequirement → PurchaseRequest | 1 → many |
| PurchaseRequest → PurchaseRequestLine | 1 → many |
| PurchaseRequest → PurchaseOrder | 1 → many |
| PurchaseOrder → PurchaseOrderLine | 1 → many |

#### 5.5.1 Supplier

Supplier is a Procurement/Purchasing-owned master entity representing an external or internal supplier used within the procurement lifecycle.

The initial Procurement foundation may represent supplier identity and operational contact information, including concepts such as:

* supplier name;
* supplier code/reference;
* supplier type;
* contact information;
* address information; and
* operational status.

Supplier settlement, banking, tax settlement, and other financial-treatment information are intentionally outside this initial Procurement foundation and remain subject to the future Finance boundary.

#### 5.5.2 PurchaseRequirement

PurchaseRequirement represents a Procurement-side record of a business need requiring procurement action.

The originating business capability remains authoritative for the underlying business context.

For example, Catering may originate a requirement for goods or services for a particular event. Procurement records that requirement using an explicit source reference.

The initial conceptual attributes include:

* reference;
* description;
* source_module;
* source_type;
* source_reference;
* required_by_date;
* status; and
* creation/ownership metadata.

PurchaseRequirement shall not contain a direct foreign key to a Catering Event or other external business-module entity.

#### 5.5.3 PurchaseRequest

PurchaseRequest is the central Procurement/Purchasing operational request representing the procurement action to satisfy one or more purchase requirements.

The initial conceptual attributes include:

* reference;
* purchase_requirement_id;
* request_date;
* required_by_date;
* status;
* justification; and
* notes.

The exact lifecycle status values are intentionally deferred to the Procurement workflow design stage.

#### 5.5.4 PurchaseRequestLine

PurchaseRequestLine represents an individual good, service, asset, or other procurement requirement within a PurchaseRequest.

The initial conceptual attributes include:

* purchase_request_id;
* description;
* item_reference;
* quantity;
* unit;
* estimated_unit_cost;
* estimated_total;
* required_by_date; and
* notes.

item_reference shall remain a Procurement-side reference unless a later approved integration explicitly establishes another relationship.

It shall not automatically become a direct foreign key to an Inventory product or stock entity.

#### 5.5.5 PurchaseOrder

PurchaseOrder represents the formal Procurement/Purchasing commitment issued to a Supplier.

PurchaseOrder is preferred over a generic Purchase entity because it clearly represents the formal supplier-facing procurement commitment.

The initial conceptual attributes include:

* supplier_id;
* reference;
* order_date;
* expected_delivery_date;
* status;
* purchase_request_id; and
* other procurement-specific operational metadata established during implementation.

A PurchaseRequest may result in multiple PurchaseOrders where sourcing or procurement circumstances require separate supplier commitments.

#### 5.5.6 PurchaseOrderLine

PurchaseOrderLine represents an individual good, service, asset, or other procurement item included in a PurchaseOrder.

The initial conceptual attributes include:

* purchase_order_id;
* description;
* item_reference;
* quantity;
* unit;
* unit_price;
* total_amount; and
* notes.

As with PurchaseRequestLine, item_reference shall not automatically establish ownership or direct foreign-key coupling to Inventory or another external business module.

#### 5.5.7 Internal Persistence Relationships

The six Procurement/Purchasing entities may use standard relational foreign keys and SQLAlchemy relationships for relationships internal to the Procurement/Purchasing bounded capability.

The initial internal persistence relationships are:

* PurchaseOrder.supplier_id → Supplier;
* PurchaseRequest.purchase_requirement_id → PurchaseRequirement;
* PurchaseRequestLine.purchase_request_id → PurchaseRequest;
* PurchaseOrder.purchase_request_id → PurchaseRequest; and
* PurchaseOrderLine.purchase_order_id → PurchaseOrder.

These relationships do not transfer ownership of any external business capability.

#### 5.5.8 Cross-Module Reference Strategy

Procurement/Purchasing shall not establish direct foreign-key dependencies on Catering, Inventory, Finance, or Expense Management domain entities as part of this initial domain model.

Cross-module business context shall use explicit references or integration contracts, such as:

* source_module;
* source_type; and
* source_reference.

This preserves bounded-domain ownership and prevents hidden persistence coupling between business modules.

#### 5.5.9 Approved Conceptual Flow

The approved initial Procurement/Purchasing flow is:

Business Need
      │
      ▼
PurchaseRequirement
      │
      ▼
PurchaseRequest
      │
      ▼
Approval / Sourcing
      │
      ▼
PurchaseOrder
      │
      ▼
Supplier Fulfillment
      │
      ▼
Receiving / Handover
      │
      ▼
Inventory Physical Stock Effect

The flow describes business responsibility and does not imply that all later stages belong to the Procurement/Purchasing persistence model.

#### 5.5.10 Deferred Procurement Concepts

The following concepts are intentionally deferred from Phase 2.2.2.1 unless subsequent requirements and architectural review establish a need for them:

* Sourcing;
* Supplier Quotation;
* Supplier Evaluation;
* Procurement Receipt;
* Inventory Receipt;
* Expense;
* Supplier Invoice;
* Payment;
* Financial Transaction;
* General Ledger;
* Catering Event;
* Catering Customer;
* Inventory Product;
* Chart of Accounts;
* Budget; and
* Tax Ledger.

Generic Sourcing or ProcurementReceipt entities shall not be introduced prematurely without a corresponding approved domain requirement and architectural decision.

#### 5.5.11 Domain Boundary Invariants

The following invariants are locked:

* PurchaseRequirement is distinct from PurchaseRequest.
* PurchaseRequest is distinct from PurchaseOrder.
* PurchaseRequestLine and PurchaseOrderLine remain line-level Procurement/Purchasing entities.
* Purchase is not synonymous with Expense.
* Procurement receiving is not synonymous with Inventory ownership.
* Physical stock effects remain owned by Inventory.
* Financial treatment remains owned by Finance.
* Expense Management remains distinct from Procurement/Purchasing.
* Supplier financial settlement details remain outside the initial Procurement foundation.
* Cross-module references shall not introduce hidden direct foreign-key coupling.

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

Phase 2.2.2.1 is the approved detailed Procurement/Purchasing domain-model decision recorded within this architecture document. Subsequent Procurement/Purchasing implementation stages shall refine implementation contracts and lifecycle behavior without silently changing the locked entity ownership or cross-module boundary established here.

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

**Phase 2.2.2.1 — Procurement/Purchasing Domain Entities & Relationships is approved and locked.**

The six-entity Procurement/Purchasing domain model consisting of Supplier, PurchaseRequirement, PurchaseRequest, PurchaseRequestLine, PurchaseOrder, and PurchaseOrderLine is the authoritative initial domain model for Procurement/Purchasing.

The approved internal relationships, cardinalities, cross-module reference strategy, persistence boundary, and deferred concepts recorded in Section 5.5 are locked for subsequent Procurement/Purchasing implementation.

Subsequent design and implementation work shall refine contracts, lifecycle behavior, workflow, authorization, persistence details, and integration behavior without silently transferring ownership between Catering, Procurement / Purchasing, Inventory, Expense Management, Finance, or Reporting.

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

**Locked Decisions:** Phase 2.2.1 Capability Ownership & Boundaries; Phase 2.2.2.1 Procurement/Purchasing Domain Entities & Relationships

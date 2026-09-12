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

### 13.1 Implementation & Verification Record

**Implementation Status:** IMPLEMENTED / VERIFIED / CLOSED

The Phase 2.2.2.2 Procurement Foundation has been implemented in accordance with the approved and locked design.

Implementation completed:

* Procurement business module established under `app\modules\procurement`;
* standard `ModuleManifest`, `BaseModule`, module discovery, and module registration conventions reused;
* the six approved Procurement domain entities implemented as module-local SQLAlchemy models;
* approved internal Procurement relationships implemented using standard foreign keys and relationships;
* no direct foreign-key coupling introduced to Catering, Inventory, Expense Management, Finance, or other external business modules;
* dedicated Alembic migration `b917d20cd76a` created and applied;
* six approved Procurement persistence tables created successfully;
* five approved internal foreign-key relationships verified successfully;
* no premature workflow/status constraints or deferred business entities introduced;
* Procurement-focused module and model tests implemented and passing.

### Verification Results

* Procurement-focused tests: **17 passed**;
* full regression test suite: **2,037 passed**;
* full-suite warnings: **1,386**;
* SQL Server Procurement schema verification: **passed**;
* migration revision after implementation: `b917d20cd76a`;
* `git diff --check`: **clean**;
* Git implementation checkpoint: `be6c85e feat(procurement): add procurement foundation`;
* final working tree after implementation checkpoint: **clean**.

The full regression suite also identified a pytest test-module naming collision caused by identical test filenames across non-package business-module test directories. The issue was resolved by adding the required package markers:

* `tests\unit\modules\catering\__init__.py`
* `tests\unit\modules\procurement\__init__.py`

No production architecture or approved Procurement domain boundaries were changed as a result.

**Stage Conclusion:** Phase 2.2.2.2 Procurement Foundation is implemented, verified, and closed. The locked architectural decisions remain unchanged and continue to govern subsequent Procurement/Purchasing stages.


### 14. Approval Record

**Stage:** Phase 2.2.2.2 — Procurement Foundation Design

**Decision:** Approved and locked

**Approved by:** Project Architecture Review

**Approval Status:** Approved / Locked

**Effective Phase:** Phase 2.2 — Purchasing & Expense Management

**Date:** 11/09/2026

**Related Decision:** Phase 2.2.2.1 — Procurement/Purchasing Domain Entities & Relationships

**Authoritative Document:** `docs\architecture\decisions\PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

## Phase 2.2.3 — Procurement Operational Surface Design

**Status: APPROVED / LOCKED**

### 1. Purpose

Phase 2.2.3 defines the operational user-facing surface for the Procurement/Purchasing module over the six domain entities already approved and implemented under Phase 2.2.2.1 and Phase 2.2.2.2.

The stage establishes how users interact with Procurement records through the existing CDCS-EMP application architecture without introducing new Procurement entities, workflow logic, or cross-module integrations.

### 2. Operational Surface Boundary

The Procurement operational surface shall provide ordinary operational management of:

1. Supplier;
2. Purchase Requirement;
3. Purchase Request;
4. Purchase Request Line;
5. Purchase Order;
6. Purchase Order Line.

The six entities remain the authoritative Procurement/Purchasing domain boundary established in Phase 2.2.2.1.

No additional Procurement entities are introduced by this stage.

### 3. Operational Navigation Model

The recommended top-level Procurement navigation is:

```text
Procurement
│
├── Suppliers
│
├── Purchase Requirements
│
├── Purchase Requests
│   └── Request Lines
│
└── Purchase Orders
    └── Order Lines
```

Purchase Request Line and Purchase Order Line shall be treated as dependent document components rather than independent top-level navigation areas.

This preserves the distinction between business-facing operational surfaces and implementation-level child entities.

### 4. Supplier Operational Surface

Supplier is Procurement-owned master data.

The operational surface shall support:

* supplier list;
* supplier detail;
* supplier creation;
* supplier editing;
* searching;
* filtering;
* pagination;
* operational status visibility.

The initial Supplier surface remains limited to the approved foundation fields:

* name;
* code;
* supplier type;
* contact information;
* address information;
* status.

The surface shall not introduce banking details, supplier settlement information, tax settlement information, supplier invoices, or supplier payments.

### 5. Purchase Requirement Operational Surface

Purchase Requirement represents the Procurement-side record of a business need.

The operational surface shall support:

* requirement list;
* requirement detail;
* creation;
* editing;
* searching;
* filtering;
* pagination;
* visibility of source/reference information.

The existing explicit cross-module reference model shall remain unchanged:

```text
source_module
source_type
source_reference
```

No direct Catering foreign key or other external business-module foreign key shall be introduced.

The originating business module remains authoritative for the originating business context.

### 6. Purchase Request Operational Surface

Purchase Request is the central Procurement operational document.

The surface shall support:

* request list;
* request detail;
* creation;
* editing;
* searching;
* filtering;
* pagination;
* viewing the associated Purchase Requirement;
* managing associated Purchase Request Lines.

The Purchase Request surface shall make its relationship to the parent Purchase Requirement visible.

A Purchase Request may contain multiple Purchase Request Lines.

### 7. Purchase Request Lines

Purchase Request Lines shall be managed within the Purchase Request surface.

The operational surface shall support:

* adding a line;
* editing a line;
* removing a line where ordinary CRUD permits;
* displaying quantity and unit;
* displaying estimated cost information;
* displaying required-by information;
* displaying item reference and notes.

`item_reference` remains an operational reference only and shall not automatically become an Inventory foreign key.

### 8. Purchase Order Operational Surface

Purchase Order represents the formal Procurement commitment to a Supplier.

The surface shall support:

* order list;
* order detail;
* creation;
* editing;
* searching;
* filtering;
* pagination;
* viewing Supplier;
* viewing the originating Purchase Request;
* managing associated Purchase Order Lines.

The surface shall clearly expose the relationship:

```text
Purchase Request
       │
       ▼
Purchase Order
       │
       ▼
Purchase Order Lines
```

A Purchase Request may result in multiple Purchase Orders, consistent with the approved domain model.

### 9. Purchase Order Lines

Purchase Order Lines shall be managed within the Purchase Order surface.

The operational surface shall support:

* adding a line;
* editing a line;
* removing a line where ordinary CRUD permits;
* displaying quantity and unit;
* displaying unit price;
* displaying total amount;
* displaying item reference and notes.

No receiving or Inventory stock effect shall be performed from the Purchase Order Line surface.

### 10. CRUD Boundary

Phase 2.2.3 establishes the ordinary operational CRUD boundary:

```text
Create
View
List
Search
Filter
Edit
```

Deletion/soft-deletion behavior shall follow the existing enterprise persistence and CRUD conventions rather than creating Procurement-specific deletion architecture.

No specialized lifecycle operation shall be introduced merely because an entity contains a `status` field.

### 11. Workflow Boundary

Phase 2.2.3 shall not implement Procurement Workflow.

The operational surface shall not introduce:

* Submit;
* Approve;
* Reject;
* authorize;
* return for correction;
* workflow-driven status transitions;
* approval routing;
* workflow permissions.

These capabilities belong to the subsequent Procurement Workflow stage.

The CRUD surface may display existing status values, but shall not define a workflow state machine.

### 12. Search, Filtering and Pagination

Procurement operational lists shall reuse the existing enterprise query and pagination framework, including:

* `QueryOptions`;
* repository query mechanisms;
* `PaginatedResult`;
* standard `CRUDService` boundaries.

Supported operational capabilities should include, where meaningful:

* pagination;
* sorting;
* text search;
* field filtering;
* status filtering;
* inactive-record handling where applicable.

Model-specific field resolution remains the responsibility of Procurement repositories.

The global `QueryOptions` framework shall not be modified for Procurement-specific requirements.

### 13. Forms and Validation

Procurement forms shall follow the existing CDCS-EMP Flask-WTF pattern.

Forms shall:

* represent operational input;
* perform basic field validation;
* enforce appropriate required, length, type, and related input constraints;
* remain thin;
* delegate business operations to services.

Business rules shall not be embedded into route functions or form definitions when they belong in the service or domain boundary.

### 14. Repository and Service Boundary

Where operational CRUD requires repositories and services, Procurement shall reuse the existing enterprise architecture:

```text
Route
  │
  ▼
Form / Input Validation
  │
  ▼
Procurement Service
  │
  ▼
Procurement Repository
  │
  ▼
SQLAlchemy Model
```

Services shall extend the existing `CRUDService` pattern where appropriate.

Repositories shall reuse the existing repository/data framework.

Procurement-specific behavior shall only be added where there is a demonstrated domain requirement.

### 15. Security and Governance

The Procurement operational surface shall reuse the existing CDCS-EMP security and governance architecture.

This stage shall not create:

* a parallel authorization framework;
* module-specific authentication;
* independent governance infrastructure;
* unrelated permission architecture.

Access-control requirements for Procurement operational actions shall be identified and implemented consistently with the existing platform security model.

Detailed workflow-specific authorization remains deferred to the Procurement Workflow stage.

### 16. Cross-Module Boundary

Phase 2.2.3 shall not implement cross-module operational integration.

**Catering**

No Catering routes, services, foreign keys, or integration contracts.

**Inventory**

No receiving, stock movement, stock balance, or physical stock effects.

**Finance**

No expenses, invoices, payments, settlement, or accounting treatment.

**Reporting**

No Reporting integration.

The Procurement operational surface shall operate against Procurement-owned data only.

### 17. UI/UX Boundary

The operational surface shall reuse the established CDCS-EMP UI foundation and conventions.

The design shall provide:

* consistent module navigation;
* list/detail presentation;
* standard forms;
* clear parent/child document presentation;
* consistent validation feedback;
* consistent pagination, search, and filtering behavior;
* consistent authorization feedback.

No separate Procurement-specific frontend architecture shall be introduced.

### 18. Explicitly Deferred

The following remain outside Phase 2.2.3:

* Procurement Workflow;
* approvals;
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
* additional Procurement entities.

### 19. Stage Completion Criteria

Phase 2.2.3 shall be considered complete when:

1. The Procurement operational surface design is approved and locked;
2. the six approved entities have clearly defined operational responsibilities;
3. parent/child surface relationships are defined;
4. CRUD boundaries are explicitly defined;
5. search, filtering, and pagination behavior is defined using existing framework contracts;
6. form and validation boundaries are defined;
7. repository and service boundaries are defined;
8. security and governance reuse is defined;
9. workflow boundaries are explicitly preserved;
10. cross-module integrations remain deferred;
11. no new Procurement entities or hidden dependencies are introduced.

### 20. Architectural Decision

Phase 2.2.3 shall establish a Procurement operational surface over the existing six approved Procurement entities, organized around Supplier, Purchase Requirement, Purchase Request, and Purchase Order as the primary operational surfaces, with Purchase Request Line and Purchase Order Line managed as child document components.

The surface shall reuse existing CDCS-EMP CRUD, query, repository, service, form, UI, security, and governance infrastructure.

Workflow and all cross-module integrations remain explicitly outside this stage.

### 21. Approval Record

**Stage:** Phase 2.2.3 — Procurement Operational Surface Design
**Decision:** Approved and locked
**Approved by:** Project Architecture Review
**Approval Status:** Approved / Locked
**Effective Phase:** Phase 2.2 — Purchasing & Expense Management
**Date:** 11/09/2026
**Related Decision:** Phase 2.2.2.2 — Procurement Foundation Design
**Authoritative Document:** `docs\architecture\decisions\PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

### Phase 2.2.3 — Supplier Operational Surface Implementation Completion

**Component:** Supplier Operational Surface
**Status:** IMPLEMENTED / VERIFIED
**Implementation Status:** Complete
**Verification Status:** Passed
**Verification Date:** 11/09/2026

#### Implementation Scope

The Supplier operational surface has been implemented as the first focused operational component of the Phase 2.2.3 Procurement Operational Surface.

The implementation provides the approved Supplier operational capabilities:

* Supplier list and detail views.
* Supplier search.
* Supplier status filtering.
* Supplier sorting and pagination.
* Supplier creation.
* Supplier viewing.
* Supplier editing.
* Supplier deletion using the established enterprise persistence conventions.
* Supplier CRUD permission enforcement through the existing enterprise authorization mechanism.
* Supplier form validation using the established Flask-WTF form pattern.
* Supplier repository and service integration using the existing enterprise CRUD and data-access infrastructure.

#### Architecture Conformance

The implementation conforms to the approved Phase 2.2.3 operational-surface design:

* The Supplier entity remains Procurement-owned.
* The existing module discovery and registration architecture is reused.
* The existing enterprise CRUD, repository, service, query, validation, security, and UI foundations are reused.
* No parallel authorization or governance architecture has been introduced.
* Supplier workflow or specialized lifecycle transitions have **not** been introduced at this stage.
* Supplier financial settlement, banking, tax settlement, invoices, payments, or accounting functionality has **not** been introduced.
* No direct cross-module foreign-key dependencies have been introduced.
* No Catering, Inventory, Expense Management, Finance, or Reporting operational integration has been introduced.

#### Verification

The following verification was completed:

* Procurement unit-test surface: **49 passed**.
* Full CDCS-EMP regression suite: **2,069 passed**.
* `git diff --check`: **clean**.
* Working-tree inspection confirmed only the expected Supplier operational-surface implementation and test changes were present.

#### Completion Decision

The **Supplier Operational Surface** is approved as **implemented and verified** within Phase 2.2.3.

The implementation establishes the Supplier CRUD operational pattern without prematurely introducing procurement workflow, receiving, financial processing, or cross-module integrations. Subsequent Procurement operational components shall continue to follow the approved Phase 2.2.3 boundaries and the established enterprise architecture.

**Related Design Decision:** Phase 2.2.3 — Procurement Operational Surface Design
**Authoritative Document:** `docs/architecture/decisions/PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

## Phase 2.2.3 — Procurement Operational Surface

**Status:** IMPLEMENTED / VERIFIED
**Decision:** Complete

### Scope Completed

Phase 2.2.3 establishes the approved Procurement operational-surface pattern over the six previously approved Procurement domain entities.

The operational components completed and verified under this stage are:

* Supplier
* Purchase Requirement

The remaining Procurement operational components are intentionally deferred to their subsequent implementation stages:

* Purchase Request
* Purchase Request Lines
* Purchase Order
* Purchase Order Lines

They are therefore **not considered implemented by this completion record**.

### Supplier Operational Surface

The Supplier operational surface was previously implemented and verified as the first focused Procurement operational component.

It provides:

* List and detail views
* Search
* Status filtering
* Sorting and pagination
* Create
* View
* Edit
* Delete according to enterprise persistence conventions
* Permission enforcement
* Flask-WTF form validation
* Repository/service integration through the existing enterprise CRUD and data-access infrastructure

### Purchase Requirement Operational Surface

The Purchase Requirement operational surface provides:

* List
* Search
* Status filtering
* Sorting
* Pagination
* Create
* View
* Edit
* Delete according to enterprise persistence conventions
* CSRF protection
* Permission-protected access
* Module-local Flask-WTF form validation
* Repository/service integration through the existing enterprise CRUD and data-access infrastructure

The implementation uses the approved Purchase Requirement fields and preserves the explicit `source_module`, `source_type`, and `source_reference` references without introducing direct cross-module foreign-key coupling.

### Architecture Conformance

The completed operational components conform to the approved Phase 2.2 architecture:

* Existing Procurement module discovery and registration infrastructure is reused.
* Existing CRUD, repository, service, query, validation, security, governance, transaction, and UI infrastructure is reused.
* No parallel authorization, governance, or transaction architecture has been introduced.
* No new Procurement domain entities have been introduced.
* No direct Catering, Inventory, Finance, or Expense Management foreign-key coupling has been introduced.
* Procurement workflow lifecycle actions remain deferred to the dedicated Procurement Workflow stage.
* Receiving and physical inventory effects remain deferred to the Procurement ↔ Inventory integration stage.
* Expense Management and Finance integration remain outside this stage.
* Supplier banking, settlement, tax settlement, invoices, payments, and accounting remain outside this stage.
* Catering integration and Reporting integration remain outside this stage.

### Verification

The completed Phase 2.2.3 operational components were verified through:

* Procurement unit-test surface: **78 passed**
* Shared application transaction tests: **10 passed**
* Full CDCS-EMP regression suite: **2,108 passed**
* Browser verification of the complete Purchase Requirement CRUD surface: **Passed**
* Search, filtering, sorting, and pagination: **Verified**
* Create, View, Edit, and Delete operations: **Verified**
* Procurement navigation and operational-surface access: **Verified**
* Previously completed Supplier operational surface: **Verified**

### Completion Decision

The completed Supplier and Purchase Requirement operational components are hereby recorded as **IMPLEMENTED / VERIFIED** within Phase 2.2.3.

This completion establishes the approved Procurement operational CRUD pattern while deliberately deferring workflow, receiving, cross-module integration, financial processing, and the remaining Procurement operational components to their designated subsequent stages.

**Related Decision:** Phase 2.2.3 — Procurement Operational Surface Design
**Authoritative Document:** `PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`

## Phase 2.2.4.1 — Procurement Workflow Scope & Lifecycle Ownership

**Decision Status:** APPROVED / LOCKED
**Approved By:** Project Architecture Review
**Approval Status:** Approved / Locked
**Effective Phase:** Phase 2.2
**Decision Date:** 11 September 2026
**Related Decision:** Phase 2.2.3 — Procurement Operational Surface Design

### Decision

Phase 2.2.4 establishes the workflow boundary for the approved Procurement domain entities. Workflow responsibility shall be assigned only to Procurement entities that represent meaningful business lifecycles requiring governed state transitions.

### Workflow-Enabled Entities

#### Purchase Request

Purchase Request shall have a dedicated Procurement workflow.

The Purchase Request workflow owns the controlled procurement-request lifecycle, including its future submission, authorization, rejection, return, and other approved lifecycle transitions.

The exact states, transition matrix, authorization requirements, execution operations, and auditable events shall be defined in the subsequent Purchase Request workflow design stage.

#### Purchase Order

Purchase Order shall have a separate dedicated Procurement workflow.

The Purchase Order workflow owns the supplier-facing procurement commitment lifecycle.

The Purchase Order workflow remains distinct from the Purchase Request workflow because one Purchase Request may result in multiple Purchase Orders and the two records represent different business responsibilities.

The exact states, transition matrix, authorization requirements, execution operations, and auditable events shall be defined in the subsequent Purchase Order workflow design stage.

### Non-Workflow Entities

#### Supplier

Supplier shall remain an ordinary Procurement master-data entity governed by the established CRUD and security architecture.

Supplier shall not receive a dedicated workflow in the current Phase 2.2 Procurement workflow scope.

Supplier status remains subject to ordinary enterprise data-management conventions unless a future approved architecture decision introduces a specialized lifecycle.

#### Purchase Requirement

Purchase Requirement shall remain a CRUD/status record and shall not receive a formal Procurement workflow in Phase 2.2.4.

Its current `DRAFT` status shall not be interpreted as establishing a formal workflow lifecycle.

The Purchase Requirement represents the recorded procurement/business need, while the Purchase Request represents the controlled procurement lifecycle.

This preserves the established distinction:

**Purchase Requirement ≠ Purchase Request**

Any future requirement for a governed Purchase Requirement approval lifecycle shall require a separate architectural decision.

#### Purchase Request Line

Purchase Request Line shall not have an independent workflow.

Its lifecycle is governed by its parent Purchase Request and the established child-record CRUD conventions.

#### Purchase Order Line

Purchase Order Line shall not have an independent workflow.

Its lifecycle is governed by its parent Purchase Order and the established child-record CRUD conventions.

### Lifecycle Ownership Model

The Procurement lifecycle boundary is therefore:

```text
Purchase Requirement
    CRUD / status-only
          │
          │ procurement need
          ▼
Purchase Request
    Dedicated Workflow
          │
          │ supplier-facing commitment
          ▼
Purchase Order
    Dedicated Workflow
          │
          ▼
Supplier
    Master Data / CRUD
```

Purchase Request Lines remain governed by Purchase Request.

Purchase Order Lines remain governed by Purchase Order.

### Architectural Principles

1. Workflow definitions shall reuse the enterprise workflow framework and registry.
2. Procurement shall not introduce a parallel workflow engine.
3. Workflow definitions shall describe states and permitted transitions but shall not become owners of authorization, transaction management, database persistence, or cross-module integration.
4. Workflow execution shall remain subject to the established enterprise authorization, execution, governance, transaction, audit, and event architecture.
5. Workflow boundaries shall not transfer ownership of Procurement, Inventory, Finance, Expense Management, or Catering responsibilities.
6. No cross-module foreign keys shall be introduced as a consequence of this workflow decision.
7. Purchase Request and Purchase Order shall remain separate workflows because they represent distinct procurement lifecycle responsibilities.
8. Child lines shall not become independent workflow entities.
9. Exact lifecycle states and transition matrices are deferred to the detailed workflow design stages.

### Explicitly Deferred

The following remain outside this decision:

* exact Purchase Request workflow states;
* Purchase Request transition matrix;
* exact Purchase Order workflow states;
* Purchase Order transition matrix;
* workflow-specific permissions;
* approval routing;
* execution handlers;
* workflow routes/actions;
* audit/event definitions;
* Procurement ↔ Inventory receiving and physical stock effects;
* Procurement ↔ Finance integration;
* Expense Management workflow;
* supplier invoices;
* supplier payments and settlement;
* accounting/general ledger processing;
* Catering integration;
* Reporting integration.

### Completion Decision

Phase 2.2.4.1 — Procurement Workflow Scope & Lifecycle Ownership is **APPROVED / LOCKED**.

The approved Procurement workflow scope consists of dedicated workflows for **Purchase Request** and **Purchase Order** only.

Supplier and Purchase Requirement remain CRUD/status-oriented within this stage, while Purchase Request Line and Purchase Order Line remain governed by their respective parent lifecycles.

The next design stage shall define the detailed lifecycle and transition model for the Purchase Request workflow without introducing implementation changes before that design is approved.

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

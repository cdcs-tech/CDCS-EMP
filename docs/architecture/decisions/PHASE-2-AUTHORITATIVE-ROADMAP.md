# CDCS-EMP — Phase 2 Authoritative Roadmap

**Version:** 2.0
**Status:** Approved / Active
**Phase:** Phase 2 — First Business Modules
**Current Business Module:** Catering
**Pilot:** SSRC-IBMS
**Original Version:** 1.0
**Reconciled:** 4 September 2026

---

# 1. Purpose

This document is the authoritative implementation roadmap for Phase 2 of the CDCS Enterprise Management Platform (CDCS-EMP).

Phase 2 moves CDCS-EMP from reusable enterprise foundation into the implementation of real business capabilities.

The first business module is Catering, developed initially for the SSRC-IBMS pilot.

This Version 2.0 reconciles the original Phase 2 roadmap with the architectural decisions and implementation completed after Version 1.0.

---

# 2. Phase 2 Objective

The objective of Phase 2 is to prove that the CDCS-EMP platform can support complete, bounded business capabilities without duplicating the enterprise platform foundation.

Phase 2 shall therefore:

1. implement real business modules;
2. establish clear business-data ownership;
3. consume existing platform capabilities;
4. maintain security and governance;
5. maintain auditable business operations;
6. validate persistence and transaction boundaries;
7. establish reusable patterns through real implementation;
8. avoid premature enterprise-wide generalization; and
9. provide a foundation for subsequent business modules.

---

# 3. Phase 2 Architectural Principles

All Phase 2 implementation shall follow these principles.

## 3.1 Existing Platform First

Business modules shall consume existing CDCS-EMP capabilities before introducing new infrastructure.

## 3.2 Bounded Business Ownership

Each module shall own a clearly defined business capability and its authoritative business data.

## 3.3 No Duplicate Infrastructure

Modules shall not create parallel:

* persistence frameworks;
* ORM foundations;
* CRUD frameworks;
* transaction managers;
* security frameworks;
* identity models;
* module lifecycle systems; or
* application frameworks.

## 3.4 Explicit Cross-Module Integration

Cross-module dependencies shall be implemented through explicit interfaces and approved integration mechanisms.

## 3.5 Security and Governance by Default

Business modules shall use the existing authentication, RBAC, authorization, audit, and governance infrastructure.

## 3.6 Incremental Verification

Every significant implementation stage shall undergo focused verification followed by broader regression verification.

## 3.7 Architecture Must Be Documented

Meaningful architectural decisions shall be documented through ADRs.

The permanent completion sequence is:

```text
Implementation
      ↓
Architecture Review
      ↓
ADR Creation / Update
      ↓
Roadmap Reconciliation
      ↓
Regression Verification
      ↓
Git Checkpoint
```

---

# 4. Phase 2 Architecture

The Phase 2 architecture is:

```text
CDCS-EMP Platform
│
├── Core Enterprise Capabilities
│   ├── Configuration
│   ├── CRUD
│   ├── Data
│   ├── Discovery
│   ├── Events
│   ├── Execution
│   ├── Integration
│   ├── Modules
│   ├── Notifications
│   ├── Platform
│   ├── Reporting
│   ├── Security
│   ├── Services
│   ├── Startup
│   ├── Validation
│   └── Workflow
│
└── Business Modules
    │
    └── Catering
```

Future business modules shall follow the same bounded-module architecture.

---

# 5. Catering Module

Catering is the first Phase 2 business module.

Its initial scope is being implemented incrementally.

The current architecture separates Catering master data from Inventory and future operational capabilities.

---

# 6. Catering Implementation Status

## 6.1 Catering Module Foundation

**Status: COMPLETE**

Implemented:

* Catering module package;
* module manifest;
* module lifecycle integration;
* model registration boundary;
* Catering security integration;
* application surface integration.

---

## 6.2 Catering Master Data

**Status: COMPLETE**

Implemented:

* ProductCategory;
* Product;
* model relationships;
* database constraints;
* repositories;
* services;
* security permissions;
* application routes;
* forms;
* templates;
* navigation integration;
* focused verification.

Authoritative decisions:

* ADR-002 — Catering Model Registration Boundary;
* ADR-003 — Catering Relationships & Database Constraints.

---

## 6.3 Catering Application Surface

**Status: COMPLETE**

Implemented application surface includes:

* Catering landing surface;
* Product Category listing;
* Product Category creation;
* Product listing;
* Product creation;
* permission enforcement;
* enterprise navigation integration.

Architectural decision:

* ADR-007 — Catering Application Surface Architecture.

---

# 7. Catering Inventory

Inventory has been established as a distinct bounded capability within Catering.

**Status: FOUNDATION COMPLETE — OPERATIONAL POSTING CONTINUES**

Inventory owns:

* Stock Items;
* Inventory Locations;
* Stock Balances;
* Stock Movements;
* Stock Transfers;
* inventory thresholds and stock configuration.

Inventory does not own:

* Purchasing;
* Supplier financial transactions;
* Expenses;
* Income;
* Invoicing;
* Payments;
* General accounting.

The Catering Product remains the authoritative product master.

Inventory does not create a duplicate product registry.

---

# 8. Inventory Architecture

## 8.1 Stock Item

**Status: COMPLETE**

A StockItem represents inventory configuration for an existing Catering Product.

Relationship:

```text
Product
   │
   └── 0..1 StockItem
```

A Product may therefore exist without being inventory-managed.

StockItem owns:

* Product relationship;
* minimum level;
* reorder level;
* active state.

Current quantity is not stored on StockItem.

---

## 8.2 Inventory Location

**Status: COMPLETE**

Inventory locations provide the physical/logical locations at which stock is held.

Each location has:

* code;
* name;
* description;
* active state.

The current architecture deliberately uses a flat location structure.

---

## 8.3 Stock Balance

**Status: COMPLETE**

StockBalance represents the current persisted quantity for:

```text
Stock Item + Location
```

The database enforces one balance per StockItem/location pair.

Quantity cannot be negative.

Zero is valid.

---

## 8.4 Stock Movement Ledger

**Status: FOUNDATION COMPLETE — POSTING IMPLEMENTATION IN PROGRESS**

Stock movements form the auditable inventory ledger.

Movement types:

```text
OPENING_BALANCE
RECEIPT
ISSUE
ADJUSTMENT
TRANSFER
```

Movement quantity is signed.

Examples:

```text
RECEIPT          positive
ISSUE            negative
OPENING_BALANCE  signed
ADJUSTMENT       signed
TRANSFER         reserved for transfer posting
```

Posted movements are immutable.

Corrections shall use compensating movements rather than destructive modification.

---

## 8.5 Stock Transfer

**Status: MODEL FOUNDATION COMPLETE — POSTING OPERATION PENDING**

StockTransfer represents movement of stock between two distinct locations.

A transfer contains:

* StockItem;
* source location;
* destination location;
* positive quantity;
* reference;
* reason;
* status;
* occurrence timestamp;
* posting timestamp.

Posting shall create the corresponding source and destination inventory effects atomically.

---

# 9. Inventory Repository and Service Architecture

**Status: COMPLETE FOUNDATION**

Inventory repositories use the existing Enterprise Data Framework.

Repositories remain persistence-focused.

Inventory services own:

* business validation;
* business rules;
* orchestration;
* transaction coordination;
* balance updates;
* movement creation;
* transfer posting.

No repository owns application transaction lifecycle.

Architectural decision:

* ADR-014 — Inventory Repository & Service Boundary.

---

# 10. Transaction and Posting Architecture

**Status: COMPLETE FOUNDATION**

The platform now provides a concrete SQLAlchemy implementation of the existing TransactionManager abstraction.

Inventory user-facing services use the TransactionManager abstraction rather than depending directly on the execution layer.

The execution layer can wrap a TransactionManager through the existing execution transaction boundary.

This preserves dependency direction and prevents transaction ownership from leaking into repositories.

Architectural decision:

* ADR-015 — Inventory Transaction & Posting Boundary.

---

# 11. Remaining Catering Capabilities

The following capabilities remain planned.

## 11.1 Product and Category Management

**Status: COMPLETE**

Already implemented.

---

## 11.2 Inventory / Food Stock Management

**Status: IN PROGRESS**

Foundation and service-level posting operations implemented.

Completed:

* stock movement posting;
* transfer posting;
* core inventory business-rule verification;
* inventory repositories and services;
* transaction boundary integration.

Remaining operational work includes, as justified:

* operational inventory workflows;
* application surface for inventory operations;
* reporting integration;
* appropriate integration boundaries.

---

## 11.3 Purchasing & Expense Management

**Status: PLANNED**

Future capability.

Purchasing shall remain distinct from Inventory.

Inventory may receive stock from purchasing through an explicit integration boundary.

---

## 11.4 Catering Income Management

**Status: PLANNED**

Future capability.

---

## 11.5 Invoice & Receipt Management

**Status: PLANNED**

Future capability.

---

## 11.6 Catering Reporting & Analytics

**Status: PLANNED**

Catering reporting shall consume the existing CDCS-EMP Reporting Framework.

A parallel reporting infrastructure shall not be created.

---

## 11.7 Workflow & Business Rules

**Status: PLANNED / INCREMENTAL**

Business-specific workflow shall be introduced only where operational requirements justify it.

Existing workflow infrastructure shall be reused.

---

## 11.8 Integration & Cross-Module Services

**Status: PLANNED**

Cross-module integration shall be implemented through explicit interfaces and contracts.

Potential future relationships include:

```text
Purchasing
     │
     ▼
Inventory
     │
     ▼
Reporting
```

and:

```text
Catering Operations
        │
        ▼
     Income
        │
        ▼
    Invoicing
```

Exact integration contracts shall be defined when the corresponding business capabilities are implemented.

---

# 12. ADR Register

The Phase 2 architectural record currently consists of:

| ADR     | Decision                                        | Status                              |
| ------- | ----------------------------------------------- | ----------------------------------- |
| ADR-001 | Phase 2 Business Module Architecture & Strategy | Approved — Retrospective            |
| ADR-002 | Catering Model Registration Boundary            | Approved / Authoritative            |
| ADR-003 | Catering Relationships & Database Constraints   | Approved / Complete / Authoritative |
| ADR-004 | Catering Repository Architecture                | Approved — Retrospective            |
| ADR-005 | Catering Service Architecture                   | Approved — Retrospective            |
| ADR-006 | Catering Security & Governance Integration      | Approved — Retrospective           |
| ADR-007 | Catering Application Surface Architecture       | Approved — Retrospective             |
| ADR-008 | Catering Inventory Domain Boundary              | Approved — Retrospective            |
| ADR-009 | Inventory Stock Item Architecture               | Approved — Retrospective            |
| ADR-010 | Inventory Location Architecture                 | Approved — Retrospective            |
| ADR-011 | Inventory Stock Balance Architecture            | Approved — Retrospective            |
| ADR-012 | Inventory Stock Movement Ledger Architecture    | Approved — Retrospective            |
| ADR-013 | Inventory Stock Transfer Architecture           | Approved — Retrospective            |
| ADR-014 | Inventory Repository & Service Boundary         | Approved — Retrospective            |
| ADR-015 | Inventory Transaction & Posting Boundary        | Approved — Retrospective            |

The register may be adjusted when architectural review determines that two decisions should be consolidated or that a new superseding ADR is required.

ADR numbers shall not be assigned merely to fill numerical gaps.

---

# 13. Version 1.0 Reconciliation

Version 1.0 remains part of the architectural history of CDCS-EMP.

Version 2.0 supersedes Version 1.0 as the active implementation roadmap.

The following changes are material:

### 13.1 Completed Work Reconciled

The roadmap now records as completed:

* Catering module foundation;
* Catering model registration;
* ProductCategory;
* Product;
* relationships and constraints;
* repositories;
* services;
* security integration;
* application surface;
* inventory domain models;
* inventory schema;
* inventory repositories;
* inventory services;
* transaction-manager integration.

### 13.2 Inventory Architecture Refined

The original roadmap described stock movement concepts differently from the architecture subsequently implemented.

The current authoritative Inventory architecture is governed by the forthcoming Inventory ADRs, particularly the:

* Inventory Domain Boundary;
* Stock Movement Ledger;
* Stock Transfer; and
* Transaction & Posting Boundary

decisions.

Where Version 1.0 conflicts with those approved decisions, the approved ADRs govern the architecture.

### 13.3 Roadmap Does Not Override ADRs

The roadmap describes:

**what is planned and when.**

ADRs describe:

**why the architecture is designed that way.**

A subsequent approved ADR supersedes an earlier roadmap assumption where the two conflict.

---

# 14. Verification and Completion Process

Every significant Phase 2 implementation stage shall follow:

```text
1. Implement
2. Focused Tests
3. Architecture Review
4. ADR Creation / Update
5. Roadmap Reconciliation
6. Module / Integration Verification
7. Full Regression
8. Git Status
9. Checkpoint Commit
10. Push
```

A stage is not considered architecturally complete until the documentation checkpoint has been completed.

---

# 15. Change Control

Material changes require architectural review.

These include changes to:

* business-module boundaries;
* authoritative data ownership;
* persistence architecture;
* tenant/organization architecture;
* module lifecycle;
* security;
* repository architecture;
* service architecture;
* transaction architecture;
* migration strategy;
* cross-module integration;
* major domain relationships.

Material architectural changes shall be documented through a new ADR or superseding ADR.

The roadmap shall then be reconciled.

---

# 16. Source of Truth

The following hierarchy applies:

### Architectural Decisions

Approved ADRs are authoritative for the architectural decisions they document.

### Implementation Roadmap

This document is authoritative for Phase 2 sequencing, implementation status, and planned work.

### Implementation

The repository is authoritative for the actual implementation.

### Verification

Tests and verification results provide evidence that the implementation satisfies the documented design.

When these sources appear inconsistent:

1. determine whether an architectural decision has changed;
2. document the change through an ADR;
3. reconcile the roadmap;
4. verify the implementation;
5. preserve the historical record.

---

# 17. Current Phase 2 Position

As of Version 2.0:

```text
Phase 2
│
└── Catering
    │
    ├── Module Foundation              ✅
    ├── Master Data                    ✅
    ├── Relationships & Constraints   ✅
    ├── Repositories                   ✅
    ├── Services                       ✅
    ├── Security & Governance          ✅
    ├── Application Surface            ✅
    │
    └── Inventory
        ├── Domain Models              ✅
        ├── Schema                     ✅
        ├── Repositories               ✅
        ├── Services                   ✅
        ├── Transaction Foundation     ✅
        ├── Movement Posting           ✅
        ├── Transfer Posting           ✅
        └── Operational Workflows      🔄
```

The planned Phase 2 architectural documentation sequence through ADR-015 is complete.

ADR-001 through ADR-015 are approved and recorded in the architectural decision register.

No additional ADR is currently planned. Future ADRs shall be introduced only if a genuinely new architectural decision requires formal documentation.
---

# 18. Status

**Version 2.0 — Approved / Active**

This version supersedes Version 1.0 as the active Phase 2 implementation roadmap.

Version 1.0 is retained as historical architectural planning evidence.

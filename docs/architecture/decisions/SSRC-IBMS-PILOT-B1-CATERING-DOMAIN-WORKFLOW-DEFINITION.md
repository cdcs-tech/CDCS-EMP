# SSRC-IBMS Pilot
## Stage B1 — Catering Domain & Workflow Definition

**Document Type:** Architecture Decision / Domain Definition
**Status:** Approved / Active
**Stage:** B1 — Catering Domain & Workflow Definition
**Roadmap:** SSRC-IBMS Pilot Readiness Implementation Roadmap — Version 1
**Module:** Catering
**Primary Pilot Capability:** Catering Operations
**Implementation Status:** Architecture approved; implementation not yet started

---

## 1. Purpose

This document establishes the approved domain model, business lifecycle, workflow boundaries, ownership rules, and integration boundaries for the Catering business capability required for the SSRC-IBMS pilot.

The existing Catering module provides a coherent inventory foundation. Stage B1 expands the architectural definition of Catering from an inventory-support capability into the primary business capability for managing catering services from customer request through event completion and associated financial/reporting context.

This document is the architectural baseline for subsequent Catering implementation work.

No implementation decision in later stages may redefine the boundaries established here without an explicit architecture decision.

---

## 2. Scope

Stage B1 defines:

- Catering business-domain concepts;
- domain ownership;
- relationships between Catering concepts;
- the primary Catering business lifecycle;
- quotation lifecycle;
- event-requirement lifecycle;
- production and delivery lifecycle;
- Catering-to-Procurement boundary;
- Catering-to-Inventory boundary;
- Catering-to-Expense Management boundary;
- Catering-to-Finance boundary;
- Catering-to-Reporting boundary;
- authorization principles;
- deferred capabilities;
- implementation guardrails.

Stage B1 does not implement the domain models, services, workflows, routes, forms, permissions, migrations, reports, or dashboards.

Those are implementation activities following this architecture decision.

---

## 3. Existing Catering Foundation

The existing Catering module is a registered enterprise business module under:

`app/modules/catering`

The module already provides the following inventory-oriented capabilities:

- Product;
- Product Category;
- Stock Item;
- Inventory Location;
- Stock Balance;
- Stock Movement;
- Stock Transfer;
- Inventory purchase-order receipt idempotency handling.

The existing inventory lifecycle follows the established CDCS-EMP workflow architecture in which:

1. workflow definitions establish lifecycle transition validity;
2. services perform business validation and authorization;
3. services execute transactional persistence;
4. inventory physical effects are applied atomically;
5. posted inventory transactions are treated as terminal/immutable at the service boundary.

The existing Catering authorization adapter also provides an enterprise service-layer authorization boundary and must be reused rather than replaced.

The business-layer expansion defined by B1 therefore extends the existing Catering module rather than creating a new module or SSRC-specific fork.

---

## 4. Catering Business Domain

The approved Catering business domain consists of the following primary concepts.

### 4.1 Customer

Represents the person or organization receiving Catering services.

Customer owns:

- identity;
- contact information;
- customer reference information required by Catering.

Customer does not become a Finance debtor/account merely because financial activity is associated with the customer.

---

### 4.2 Catering Request

Represents an initial request for Catering services.

A Catering Request provides the entry point into the Catering operational lifecycle.

It may capture:

- customer;
- requested service;
- requested event/service date;
- expected attendance;
- initial requirements;
- customer/request notes;
- request status.

A request is not automatically a confirmed business commitment.

---

### 4.3 Catering Event

Represents the operational Catering engagement created from an accepted/confirmed request.

The Catering Event is the central operational context for:

- event requirements;
- procurement requirements;
- production;
- delivery/service;
- revenue context;
- cost context;
- profitability;
- reporting.

The Event is a Catering business concept and must not be confused with a Procurement transaction, Inventory transaction, or Finance transaction.

---

### 4.4 Quotation

Represents the commercial offer prepared for a customer.

A quotation may contain:

- proposed Catering services/items;
- quantities;
- prices;
- adjustments;
- totals;
- validity period;
- customer-facing notes.

Quotation ownership remains within Catering.

A quotation is not itself an invoice, payment, receivable, or general-ledger transaction.

---

### 4.5 Event Requirement

Represents what a Catering Event requires operationally.

Requirements may describe:

- food/material requirements;
- quantities;
- timing;
- preparation requirements;
- service requirements;
- inventory-supported requirements;
- procurement-required requirements.

The Event Requirement expresses the Catering business need.

It does not represent a Procurement Purchase Request.

---

### 4.6 Catering Purchase Requirement

Represents a specific Event Requirement that Catering has identified as requiring procurement.

The Catering Purchase Requirement expresses:

> What the Catering Event needs to obtain externally.

It does not express:

> How Procurement will source, approve, order, or receive that requirement.

The Procurement lifecycle begins at the Procurement boundary.

---

### 4.7 Production / Delivery

Represents the operational fulfilment of the Catering Event.

Production / Delivery provides the business context for:

- preparation;
- production;
- readiness;
- delivery/service;
- completion.

Physical inventory effects remain owned by Inventory.

Catering must not create a parallel inventory ledger.

---

### 4.8 Catering Financial Context

Represents the event-level financial information required for Catering operations and management reporting.

It supports:

- quoted value;
- revenue context;
- event costs;
- associated expenses/costs;
- profitability.

This is a focused Catering-support financial boundary.

It does not establish a full Finance or accounting subsystem.

---

## 5. Domain Relationship Model

The approved conceptual relationship is:

```text
Customer
   |
   v
Catering Request
   |
   v
Catering Event
   |
   +--------------------> Quotation
   |                           |
   |                           v
   |                    Approval / Confirmation
   |
   +--------------------> Event Requirements
   |                           |
   |                           +----> Inventory-supported requirement
   |                           |
   |                           +----> Catering Purchase Requirement
   |                                         |
   |                                         v
   |                               Procurement Purchase Requirement
   |                                         |
   |                                         v
   |                               Procurement Purchase Request
   |                                         |
   |                                         v
   |                                    Purchase Order
   |                                         |
   |                                         v
   |                               Inventory Physical Receipt
   |
   +--------------------> Production / Delivery
   |
   +--------------------> Revenue / Cost Context
                                  |
                                  v
                              Profitability
                                  |
                                  v
                               Reporting
```

The Catering Event is the central business context.

Downstream capabilities retain their own ownership boundaries.

---

## 6. Principal Catering Business Lifecycle

The approved primary Catering Event lifecycle is:

```text
REQUESTED
    |
    v
QUOTED
    |
    v
PENDING_CONFIRMATION
    |
    v
CONFIRMED
    |
    v
PLANNING
    |
    v
READY
    |
    v
IN_PRODUCTION
    |
    v
DELIVERED
    |
    v
COMPLETED
```

Controlled cancellation is supported from appropriate pre-completion states:

```text
REQUESTED --------------> CANCELLED
QUOTED -----------------> CANCELLED
PENDING_CONFIRMATION ---> CANCELLED
```

Exact transition authorization and service validation are implementation concerns and must be defined from this lifecycle rather than independently invented.

---

## 7. Catering Request Lifecycle

A Catering Request represents an initial customer demand before a confirmed operational commitment exists.

The Request lifecycle must distinguish:

- receipt of the request;
- preparation of a quotation;
- customer confirmation;
- cancellation or rejection where applicable.

The Request must not be treated as equivalent to an Event.

This separation allows the system to retain the difference between:

- a customer asking for Catering services; and
- a confirmed Catering engagement.

---

## 8. Quotation Lifecycle

Quotation has an independent lifecycle:

```text
DRAFT
  |
  v
ISSUED
  |
  +----> ACCEPTED
  |
  +----> DECLINED
  |
  +----> EXPIRED
```

An accepted quotation enables creation or confirmation of the associated Catering Event.

Quotation approval/acceptance must remain distinct from Procurement approval.

Quotation acceptance is a Catering/customer business decision.

Procurement approval is a Procurement organizational control.

---

## 8.1 Quotation / Event Coordination Contract

Stage B4.3 establishes the explicit application-service coordination boundary between an accepted Catering Quotation and its associated Catering Event.

### Purpose

B4.3 provides a controlled application-service capability through which an accepted Catering Quotation can enable explicit progression of its associated Catering Event.

The primary coordination operation is:

```text
progress_event_from_accepted_quotation(
    quotation_id,
    *,
    subject
)
```

The operation coordinates existing Catering-owned aggregates without merging their independent lifecycles and without introducing a new domain aggregate.

### Ownership

- Catering Quotation remains owned by Catering.
- Catering Event remains owned by Catering.
- Cross-aggregate coordination is an application-service responsibility within Catering.
- No new aggregate or duplicate ownership is introduced.

### Required Relationship

The coordinator must load and validate both the quotation and its associated event.

The following conditions are required:

1. The quotation exists.
2. The associated event exists.
3. The quotation status is `ACCEPTED`.
4. The quotation references the loaded event.
5. The quotation and event belong to the same customer.
6. The event is currently in `REQUESTED` status.

The coordinator must not infer, repair, or silently correct inconsistent quotation/event/customer relationships.

### Event Lifecycle Coordination

B4.3 performs only the following Event lifecycle transition:

```text
REQUESTED → QUOTED
```

This transition must be invoked through the existing `CateringEventWorkflow`.

The coordinator must not directly assign an Event status in a manner that bypasses workflow validation.

The established Event lifecycle remains:

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

B4.3 does not perform or bypass the later Event transitions.

In particular, B4.3 does not:

- confirm the customer;
- move `QUOTED` to `PENDING_CONFIRMATION`;
- move `PENDING_CONFIRMATION` to `CONFIRMED`;
- plan the event;
- begin production;
- deliver the event;
- complete the event.

Quotation acceptance and Event confirmation therefore remain separate and auditable business actions.

### Authorization

B4.3 reuses the existing Catering Event authorization boundary.

The required permission for the coordination operation is:

```text
CATERING.CATERING_EVENT.QUOTE
```

No new B4.3-specific permission is introduced.

Authorization must occur before Event workflow execution and before Event persistence.

The coordinator must remain independent of Flask request context and `current_user`.

### Quotation Acceptance Boundary

`CateringQuotationService.accept()` remains the authoritative operation for:

```text
ISSUED → ACCEPTED
```

Quotation acceptance remains independent from B4.3 coordination.

B4.3 must not re-accept, modify, or otherwise mutate the quotation.

After successful coordination:

```text
Quotation.status == ACCEPTED
```

The quotation's totals, lines, dates, and other commercial information remain unchanged.

Quotation acceptance therefore does not silently trigger Event mutation. Event progression occurs only through the explicit B4.3 coordination capability.

### Persistence

After all coordination preconditions pass:

1. The coordinator invokes `CateringEventWorkflow` for the `REQUESTED → QUOTED` transition.
2. The Event status is updated from the returned workflow state.
3. The Event is persisted through the established Event repository boundary.
4. The updated Event is returned to the caller.

The quotation is not persisted by the coordination operation because its state remains unchanged.

### Failure Atomicity

If authorization, relationship validation, or workflow validation fails:

```text
Quotation: unchanged
Event:      unchanged
Event persistence: not performed
```

A denied authorization must not invoke the Event workflow or modify the Event.

A failed workflow transition must likewise leave the Event unchanged.

### Service Composition Boundary

The B4.3 coordination service composes existing lower-level Catering boundaries directly:

```text
CateringQuotationRepository
CateringEventRepository
CateringEventWorkflow
CateringAuthorizationAdapter
```

It does not depend on `CateringQuotationService` or `CateringEventService`.

This preserves the established CDCS-EMP application-service structure and avoids introducing a new service-to-service composition pattern solely for B4.3.

The coordinator is responsible only for cross-aggregate coordination. Quotation lifecycle rules remain owned by `CateringQuotationService`, while Event lifecycle validity remains owned by `CateringEventWorkflow`.

### 8.2 B4.4 Event Confirmation

#### Purpose

B4.4 establishes the explicit Event confirmation boundary following successful B4.3 quotation-to-event coordination.

B4.4 provides the two remaining Event lifecycle operations required for the B4 quotation and confirmation acceptance gate:

```text
QUOTED → PENDING_CONFIRMATION
PENDING_CONFIRMATION → CONFIRMED
```

These are separate and auditable business actions.

The first operation represents requesting or placing the associated Event into the customer-confirmation stage.

The second operation records confirmation of the Event and allows the Event to proceed to later operational planning.

B4.4 does not combine the two transitions into a single operation.

#### Ownership

Catering remains the sole owner of the Catering Event lifecycle.

`CateringEventService` remains the application-service boundary for the Event confirmation operations.

`CateringEventWorkflow` remains the authoritative owner of Event lifecycle transition validity.

No new aggregate, entity, repository, workflow, or ownership boundary is introduced by B4.4.

Quotation lifecycle ownership remains with `CateringQuotationService`.

B4.4 does not modify quotation state and does not duplicate quotation ownership.

#### Public Operations

B4.4 exposes two explicit application-service operations:

```text
request_confirmation(event, *, subject)
confirm(event, *, subject)
```

`request_confirmation()` performs:

```text
QUOTED → PENDING_CONFIRMATION
```

`confirm()` performs:

```text
PENDING_CONFIRMATION → CONFIRMED
```

Each operation represents one business action and one Event lifecycle transition.

Neither operation performs the subsequent operational planning transition.

#### Preconditions

For `request_confirmation()`:

1. The Event must exist.
2. The Event must currently be in `QUOTED` status.
3. The Event lifecycle transition must be valid according to `CateringEventWorkflow`.

For `confirm()`:

1. The Event must exist.
2. The Event must currently be in `PENDING_CONFIRMATION` status.
3. The Event lifecycle transition must be valid according to `CateringEventWorkflow`.

B4.4 does not infer, repair, or silently advance an Event from an invalid lifecycle state.

B4.4 does not independently re-validate quotation acceptance.

Successful B4.3 coordination establishes the Event's `QUOTED` state as the boundary into the confirmation process.

#### Authorization

Both B4.4 operations reuse the existing Catering Event confirmation permission:

```text
CATERING.CATERING_EVENT.CONFIRM
```

No new B4.4-specific permission is introduced.

Authorization must occur before Event workflow execution and before Event persistence.

The operations must remain independent of Flask request context and `current_user`.

The existing service-level fail-closed authorization behavior remains applicable when no authorization adapter has been configured.

#### Workflow Boundary

B4.4 must delegate lifecycle transition validity to `CateringEventWorkflow`.

For `request_confirmation()` the service invokes:

```text
CateringEventWorkflow:
    QUOTED → PENDING_CONFIRMATION
```

For `confirm()` the service invokes:

```text
CateringEventWorkflow:
    PENDING_CONFIRMATION → CONFIRMED
```

The service applies the returned `WorkflowState` to the Event.

B4.4 must not bypass the workflow by assigning Event status directly without workflow validation.

The existing Event workflow remains unchanged by B4.4 because both required confirmation transitions are already defined.

#### Persistence

After authorization and successful workflow validation:

1. The Event status is updated from the returned workflow state.
2. The Event is persisted through the established Event repository boundary.
3. The updated Event is returned to the caller.

Persistence must use the existing base CRUD update path rather than the authorization-protected `CateringEventService.update()` operation.

This preserves the established pattern used by the Event cancellation operation and ensures that `CATERING.CATERING_EVENT.CONFIRM` remains the lifecycle-specific authorization boundary.

#### Failure Atomicity

If authorization fails:

```text
Event: unchanged
Event persistence: not performed
Workflow transition: not invoked
```

If workflow validation fails:

```text
Event: unchanged
Event persistence: not performed
```

A failed confirmation operation must not partially advance the Event lifecycle.

No quotation mutation or downstream business-module side effect occurs when B4.4 fails.

#### Quotation Boundary

B4.4 does not accept, decline, expire, modify, or otherwise mutate a Catering Quotation.

`CateringQuotationService.accept()` remains authoritative for:

```text
ISSUED → ACCEPTED
```

B4.3 remains authoritative for coordinating an accepted quotation with its associated Event:

```text
REQUESTED → QUOTED
```

B4.4 begins from the established `QUOTED` Event boundary and is responsible only for the Event confirmation lifecycle.

This preserves the separation:

```text
Quotation acceptance
        ↓
B4.3 quotation/event coordination
        ↓
Event QUOTED
        ↓
B4.4 confirmation process
        ↓
Event CONFIRMED
```

#### Downstream Boundary

B4.4 introduces no downstream Procurement, Inventory, Finance, Expense Management, Production, Delivery, or Reporting side effects.

The following transitions remain outside B4.4:

```text
CONFIRMED → PLANNING
PLANNING → READY
READY → IN_PRODUCTION
IN_PRODUCTION → DELIVERED
DELIVERED → COMPLETED
```

Those capabilities remain governed by their corresponding future implementation stages and existing Event workflow definitions.

#### No New Infrastructure

B4.4 introduces:

- no new database table;
- no new migration;
- no new aggregate;
- no new repository;
- no new workflow;
- no new permission;
- no new cross-module integration;
- no duplicate quotation ownership.

The existing `CateringEventService`, `CateringEventWorkflow`, `CateringEventRepository`, and `CateringAuthorizationAdapter` remain the authoritative implementation boundaries.

#### Acceptance Gate

B4.4 completes the Event confirmation portion of the B4 quotation-management acceptance gate when an Event can progress through:

```text
REQUESTED
    ↓
QUOTED
    ↓
PENDING_CONFIRMATION
    ↓
CONFIRMED
```

where:

- B4.3 performs `REQUESTED → QUOTED`;
- B4.4 performs `QUOTED → PENDING_CONFIRMATION`;
- B4.4 performs `PENDING_CONFIRMATION → CONFIRMED`.

Quotation acceptance remains separately auditable as:

```text
ISSUED → ACCEPTED
```

B4.4 therefore completes confirmation without collapsing quotation acceptance, quotation/event coordination, and Event confirmation into one operation.

### Transactional Boundary

Event workflow transition and Event persistence occur within the established service/repository transaction boundary.

The coordination operation does not introduce a distributed transaction or cross-module transactional ownership.

Quotation state remains unchanged.

### Exclusions

B4.3 introduces no side effects in:

- Event Requirements;
- Catering Purchase Requirements;
- Procurement Purchase Requests;
- Purchase Orders;
- Inventory;
- Production;
- Delivery;
- Revenue;
- Expenses;
- Costs;
- Profitability;
- Finance;
- Invoices;
- Payments;
- Accounts Receivable;
- General Ledger; or
- Reporting.

These capabilities remain subject to their respective later roadmap stages.

### Architectural Decision

1. Quotation acceptance and Event progression remain separate business operations.
2. An accepted quotation may explicitly enable progression of its associated Event.
3. `progress_event_from_accepted_quotation()` is the defined B4.3 coordination operation.
4. B4.3 validates quotation status, quotation/event relationship, customer consistency, and Event lifecycle state before coordination.
5. B4.3 uses the existing `CATERING.CATERING_EVENT.QUOTE` authorization permission.
6. Event lifecycle validity remains owned by `CateringEventWorkflow`.
7. B4.3 performs only the `REQUESTED → QUOTED` Event transition.
8. Quotation status remains unchanged during coordination.
9. Cross-aggregate coordination remains an application-service responsibility within Catering.
10. No new domain aggregate, database entity, migration, or B4.3-specific permission is introduced.
11. No Procurement, Inventory, Finance, Expense, Production, Delivery, or Reporting side effects are introduced.
12. The approved independent Quotation and Event lifecycles are preserved.

---

## 9. Event Requirement Lifecycle

Event Requirements represent operational needs of a Catering Event.

The conceptual lifecycle is:

```text
IDENTIFIED
    |
    v
PLANNED
    |
    +----> AVAILABLE
    |
    +----> PROCUREMENT_REQUIRED
    |
    +----> CANCELLED
```

A requirement may therefore be fulfilled through:

1. existing Inventory; or
2. Procurement.

The requirement lifecycle must not duplicate Procurement Purchase Request states.

---

## 10. Production / Delivery Lifecycle

The operational execution lifecycle is:

```text
PLANNED
   |
   v
IN_PRODUCTION
   |
   v
READY_FOR_DELIVERY
   |
   v
DELIVERED
   |
   v
COMPLETED
```

Catering owns the operational context.

Inventory owns physical stock effects.

For example, when ingredients or materials are consumed:

```text
Catering Event / Production Context
              |
              v
        Inventory operation
              |
              v
       Stock Movement
```

Catering must not directly maintain or duplicate Stock Balance or Stock Movement logic.

---

## 11. Procurement Boundary

The approved distinction is:

```text
Catering Event Requirement
          |
          v
Catering Purchase Requirement
          |
          v
Procurement Purchase Requirement
          |
          v
Procurement Purchase Request
          |
          v
Procurement lifecycle
```

### Catering owns:

- identification of the business need;
- association with the Catering Event;
- required quantity/context;
- event-related justification;
- operational required-by information where applicable.

### Procurement owns:

- Procurement Purchase Requirement processing;
- Purchase Request;
- sourcing;
- supplier selection;
- procurement approvals;
- Purchase Order;
- procurement transaction lifecycle.

The existing Procurement `PurchaseRequest` model and service remain authoritative for Procurement processing.

**Catering Purchase Requirement ≠ Procurement Purchase Request.**

No duplicate Catering Purchase Request entity is to be introduced.

---

## 12. Inventory Boundary

Inventory owns:

- Stock Item;
- Inventory Location;
- Stock Balance;
- Stock Movement;
- Stock Transfer;
- physical receipt effects;
- inventory posting;
- inventory receipt idempotency.

Catering may provide event and production context for inventory operations, but must not duplicate inventory ownership.

The existing purchase-order receipt idempotency mechanism must be reused for Procurement-to-Inventory receipt processing.

The existing distinction remains:

**Physical Receipt ≠ Financial Expense.**

---

## 13. Expense Management Boundary

Expense Management owns:

- expense records;
- expense classification;
- expense lifecycle;
- expense-specific business rules.

Catering may associate an expense or cost with a Catering Event for operational and profitability purposes.

Catering must not create a parallel authoritative Expense entity merely to support event profitability.

The relationship is contextual:

```text
Expense Management Expense
             |
             v
     Catering Event Context
             |
             v
        Profitability
```

---

## 14. Finance Boundary

The pilot requires focused financial capability supporting Catering.

The focused Finance boundary may provide:

- Catering revenue;
- financial transaction history;
- invoicing where required;
- receipts where required;
- event financial summaries;
- profitability-support information.

This does not establish a full accounting ERP.

The following remain outside B1:

- general ledger;
- accounts payable;
- accounts receivable;
- payroll;
- tax engine;
- comprehensive budgeting;
- full payment management;
- general accounting.

Existing Procurement ↔ Finance integration architecture remains authoritative for procurement-originated financial events.

---

## 15. Reporting Boundary

Catering will provide business data and context required by the existing Reporting & Analytics framework.

Potential future outputs include:

- Catering revenue reports;
- event activity reports;
- event cost reports;
- procurement requirements;
- procurement expenditure;
- inventory consumption;
- event profitability;
- management dashboards.

Reporting infrastructure remains a platform capability.

B1 does not implement dashboards or SSRC-specific reports.

---

## 16. Authorization Principles

The existing `CateringAuthorizationAdapter` remains the authoritative Catering authorization boundary.

No replacement authorization mechanism is required.

Future business-layer permissions should follow the established enterprise vocabulary:

```text
CATERING.<RESOURCE>.<ACTION>
```

Examples may include:

```text
CATERING.CUSTOMER.CREATE
CATERING.CUSTOMER.READ
CATERING.CUSTOMER.UPDATE
CATERING.CUSTOMER.DELETE
```

and lifecycle-specific actions where required.

Exact permission definitions must be derived from the finalized domain/workflow implementation and must not be invented independently of the approved B1 lifecycle.

Authorization remains service-layer enforced and must not depend on Flask request context or direct `current_user` coupling.

---

## 17. Domain Ownership Rules

The following ownership rules are mandatory.

### Rule 1 — Catering owns customer and event operations

Customer, Catering Request, Catering Event, Quotation and operational fulfilment belong to Catering.

### Rule 2 — Catering owns the business requirement

Catering determines what an Event requires.

### Rule 3 — Procurement owns procurement

Catering does not own suppliers, sourcing, Purchase Orders, Procurement approvals or procurement transactions.

### Rule 4 — Inventory owns physical stock

Catering does not maintain a second inventory ledger.

### Rule 5 — Expense Management owns expenses

Catering does not duplicate the authoritative Expense lifecycle.

### Rule 6 — Finance owns financial transactions

The focused Finance capability supports the Catering pilot without turning Catering into a general accounting module.

### Rule 7 — Reporting owns reporting infrastructure

Catering supplies business data; Reporting provides reusable reporting/query/dashboard infrastructure.

---

## 18. Principal Pilot Flow

The approved SSRC pilot business flow is:

```text
Customer
   |
   v
Catering Request / Event
   |
   v
Quotation
   |
   v
Approval / Confirmation
   |
   v
Event Requirements
   |
   v
Catering Purchase Requirements
   |
   v
Procurement
   |
   v
Purchase Order
   |
   v
Inventory Receipt
   |
   v
Catering Production / Delivery
   |
   v
Catering Revenue
   |
   v
Catering Expenses / Costs
   |
   v
Profitability
   |
   v
Management Report / Dashboard
```

This flow is the primary business scenario against which later implementation and acceptance testing should be validated.

---

## 19. Deferred Capabilities

The following capabilities are explicitly deferred from B1 and the immediate pilot scope:

- Hall Hire Management;
- Asset Management;
- Membership Management;
- broader/general Finance capability;
- full accounting/ERP functionality;
- general ledger;
- payroll;
- tax management;
- comprehensive payment management;
- supplier management within Catering;
- standalone warehouse management.

These capabilities must not be introduced indirectly while implementing B1.

---

## 20. Implementation Guardrails

Future implementation must follow these rules.

### 20.1 Extend the existing Catering module

All Catering business-domain implementation belongs under:

`app/modules/catering`

No SSRC-specific fork is permitted.

### 20.2 Preserve existing inventory architecture

Existing inventory models, repositories, services and workflows remain authoritative.

Business-domain implementation must integrate with them rather than reproduce them.

### 20.3 Preserve module boundaries

Catering must communicate with Procurement, Inventory, Expense Management, Finance and Reporting through their established service/domain contracts.

### 20.4 Workflow owns lifecycle validity

Workflow definitions establish legal state transitions.

Services remain responsible for:

- business validation;
- authorization;
- transactions;
- persistence;
- side effects;
- integration coordination.

### 20.5 Avoid premature financial modelling

B1 must not evolve into a general accounting implementation.

### 20.6 Implement incrementally

Implementation must proceed one focused component at a time:

1. inspect required existing contracts;
2. define smallest implementation;
3. implement one focused change;
4. run targeted tests;
5. run relevant regression;
6. run full suite at the appropriate checkpoint;
7. verify Git working tree;
8. create a Git checkpoint;
9. update architecture documentation where decisions change.

---

## 21. B1 Architecture Decision

The following architecture is approved for the SSRC-IBMS pilot:

1. Catering becomes the primary business capability for the SSRC catering operational flow.
2. The existing Catering inventory foundation remains inside the same module and becomes a supporting capability.
3. Customer, Catering Request, Catering Event, Quotation, Event Requirement, Catering Purchase Requirement and Production/Delivery are Catering-owned concepts.
4. Procurement Purchase Request remains Procurement-owned.
5. Inventory remains the authoritative owner of physical stock.
6. Expense Management remains the authoritative owner of expenses.
7. Focused Finance provides the financial capability required to support Catering.
8. Reporting consumes Catering and integrated business data through the existing Reporting framework.
9. No duplicate cross-module ownership is permitted.
10. The principal pilot flow is Customer → Request/Event → Quotation → Confirmation → Requirements → Procurement/Inventory → Production/Delivery → Revenue/Costs → Profitability → Reporting.

---

## 22. Acceptance Criteria

B1 is architecturally complete when:

- the Catering business domain is explicitly defined;
- domain ownership is unambiguous;
- the primary Catering lifecycle is defined;
- quotation lifecycle is defined;
- event-requirement lifecycle is defined;
- production/delivery lifecycle is defined;
- Procurement boundary is explicit;
- Inventory boundary is explicit;
- Expense Management boundary is explicit;
- Finance boundary is explicit;
- Reporting boundary is explicit;
- authorization principles are established;
- deferred capabilities are documented;
- the principal SSRC pilot flow is established;
- this document is committed as the authoritative B1 architecture baseline.

---

## 23. Status

**Status: APPROVED / ACTIVE**

This document establishes the architectural baseline for Stage B1.

Implementation may proceed only from this approved definition.

Any material change to the domain ownership, lifecycle, or cross-module boundaries defined here requires an explicit architecture decision and documentation update.

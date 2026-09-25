# PHASE 2.2 — PROCUREMENT ↔ FINANCE INTEGRATION CONTRACT

**Document Status:** APPROVED / ACTIVE / LOCKED
**Phase:** Phase 2.2 — Purchasing & Expense Management
**Decision Area:** Procurement ↔ Finance Integration
**Decision Date:** 25 September 2026
**Documentation Date:** 25 September 2026
**Decision Type:** Architecture / Integration Boundary / Ownership
**Implementation Status:** Design Approved — Implementation Pending

---

## 1. Purpose

This architecture decision establishes the authoritative boundary and integration contract between the CDCS-EMP Procurement capability and the future Finance capability.

The decision defines:

- ownership of Procurement and Finance responsibilities;
- the Procurement business fact that is eligible for Finance communication;
- the architectural integration boundary;
- the information Procurement may communicate to Finance;
- responsibilities that remain exclusively Finance-owned;
- response, failure, retry, and idempotency principles;
- cancellation and future financial-effect communication principles;
- security, authorization, audit, events, and governance requirements;
- transaction-boundary requirements;
- explicit exclusions preventing Procurement from becoming a financial accounting subsystem.

This decision is design-first.

No Finance entities, accounting models, financial persistence, invoice models, payment models, ledger structures, or Finance-specific implementation shall be introduced solely as a consequence of this decision.

---

# 2. Scope

## 2.1 In Scope

This decision covers:

1. Procurement ownership of Purchase Orders and procurement lifecycle.
2. Finance ownership of financial treatment and accounting information.
3. The Procurement → Finance business trigger.
4. The enterprise integration boundary between the capabilities.
5. Procurement-to-Finance business information communication.
6. Integration success and failure semantics.
7. Retry and idempotency principles.
8. Future cancellation/change communication principles.
9. Security and authorization boundaries.
10. Audit and integration lifecycle records.
11. Integration events.
12. Transaction boundaries.
13. Cross-module persistence restrictions.
14. Architectural governance invariants.
15. Future implementation sequencing.

## 2.2 Out of Scope

The following are explicitly outside this decision:

- Finance entities;
- financial transaction schema;
- chart of accounts;
- journal-entry model;
- general ledger;
- accounts payable;
- invoice schema;
- payment schema;
- receipt schema;
- supplier settlement model;
- financial posting rules;
- accounting recognition rules;
- reconciliation model;
- Finance HTTP/UI;
- Finance workflow implementation;
- Finance database schema;
- Finance-specific reporting models;
- detailed financial classification;
- tax accounting;
- payment execution;
- additional Procurement → Finance operations not yet separately approved.

These require separate Finance architecture decisions.

---

# 3. Architectural Context

CDCS-EMP uses bounded business capabilities rather than allowing individual modules to reproduce enterprise infrastructure or take ownership of adjacent business domains.

The Phase 2.2 architecture establishes Procurement, Inventory, Expense Management, Finance, and Reporting as distinct responsibilities.

The relevant ownership boundaries are:

| Capability | Primary Responsibility |
| --- | --- |
| Procurement | Suppliers, sourcing, purchase requirements, purchase requests, purchase orders, approvals, procurement lifecycle and procurement transactions |
| Inventory | Physical stock, stock items, locations, balances, movements, transfers and physical stock effects |
| Expense Management | Expense records, classifications and expense lifecycle |
| Finance | Financial treatment, financial transactions, invoices, payments, receipts, settlement, accounting and financial ledger |
| Reporting | Read-oriented consumption of approved business/read models |

Procurement therefore requires an explicit integration boundary when procurement information has financial significance.

---

# 4. Core Ownership Decision

## 4.1 Procurement Owns Procurement

Procurement remains authoritative for:

- Supplier;
- Purchase Requirement;
- Purchase Request;
- Purchase Request Line;
- Purchase Order;
- Purchase Order Line;
- procurement approvals;
- procurement lifecycle;
- supplier-facing procurement references;
- procurement commercial information;
- procurement transaction state.

Procurement is responsible for determining whether a Purchase Order has reached a valid Procurement lifecycle state.

## 4.2 Finance Owns Financial Treatment

Finance remains authoritative for:

- financial treatment;
- financial transactions;
- invoices;
- payments;
- receipts;
- supplier settlement;
- accounting treatment;
- accounting classification;
- ledger information;
- financial posting;
- financial rules.

Finance determines the financial consequence of information communicated by Procurement.

## 4.3 Ownership Boundary

Procurement shall not:

- create Finance ledger entries;
- maintain a private accounting ledger;
- determine final accounting treatment;
- create Finance-owned financial transactions;
- process supplier payments;
- settle suppliers financially;
- duplicate Finance invoice/payment functionality;
- directly modify Finance persistence.

Finance shall not:

- own Procurement Purchase Orders;
- own Procurement supplier lifecycle;
- directly change Procurement Purchase Order state;
- directly mutate Procurement repositories.

---

# 5. Procurement Purchase Order Approval as the Finance Integration Trigger

The authoritative Procurement → Finance trigger is:

> **The successful Procurement transition of a Purchase Order to `APPROVED` creates the Procurement business fact eligible for Finance communication.**

This wording is intentional.

The trigger is the successful business transition rather than merely the existence of an object whose current state happens to be `APPROVED`.

The integration therefore occurs only after the Procurement transaction has successfully established the approved Purchase Order state.

---

# 6. Why Purchase Order Approval Is the Trigger

A Purchase Order represents the formal Procurement transaction with the supplier.

A Purchase Request is an internal procurement request and does not itself represent the finalized supplier-facing procurement commitment.

Therefore:

- Purchase Request creation is not the Finance trigger.
- Purchase Request submission is not the Finance trigger.
- Purchase Request approval is not the Finance trigger.
- Purchase Order creation is not the Finance trigger.
- Purchase Order submission is not the Finance trigger.
- Purchase Order approval is the Procurement business fact eligible for Finance communication.
- Physical receipt is not the Finance trigger.
- Inventory posting is not the Finance trigger.
- Expense approval is not the Finance trigger.
- Payment is not a Procurement trigger.

---

# 7. Purchase Order Approval Does Not Mean Accounting Recognition

A Purchase Order reaching `APPROVED` is a Procurement business fact.

It does **not** automatically mean:

- accounting recognition;
- invoice creation;
- financial posting;
- payment obligation recognized by Finance;
- supplier settlement;
- ledger posting;
- payment execution;
- financial transaction creation.

The Finance capability determines whether and how the approved procurement information results in Finance-owned processing.

Therefore:

> `PurchaseOrder.APPROVED` ≠ accounting recognition.

---

# 8. Procurement Purchase Order Lifecycle

The Procurement Purchase Order workflow remains Procurement-owned.

The approved lifecycle is:

```text
DRAFT
  │
  └── SUBMIT
        ↓
     SUBMITTED
        │
        ├── APPROVE → APPROVED
        │
        └── REJECT → REJECTED

APPROVED
  │
  └── CANCEL → CANCELLED
```

Finance integration does not introduce additional Finance states into this workflow.

The Purchase Order shall not acquire states such as:

- `FINANCE_PENDING`;
- `FINANCE_APPROVED`;
- `FINANCE_REJECTED`;
- `FINANCE_POSTED`;
- `PAYMENT_PENDING`;
- `PAID`.

Financial lifecycle belongs to Finance.

---

# 9. Separation of Procurement Approval and Finance Processing

Procurement approval and Finance processing are separate business concerns.

After the Purchase Order successfully reaches `APPROVED`, Procurement may communicate the approved procurement commitment to Finance.

Finance may:

- accept the integration;
- reject the integration for a Finance-owned business reason;
- fail to process the request;
- process the information according to Finance-owned rules.

A Finance-side outcome shall not automatically change the Procurement Purchase Order state.

In particular:

> Finance rejection shall not automatically reject an already-approved Procurement Purchase Order.

Any subsequent Procurement action requires an explicit Procurement business transition or separately approved business rule.

---

# 10. Integration Architecture

The existing enterprise Integration Framework is mandatory.

The architectural execution path is:

```text
Procurement Business Fact
        │
        ▼
Domain Integration Request
        │
        ▼
Enterprise IntegrationRequest
        │
        ▼
IntegrationService.execute()
        │
        ▼
IntegrationProviderRegistry
        │
        ▼
Finance Integration Provider
        │
        ▼
Finance Capability
        │
        ▼
IntegrationResponse
        │
        ▼
IntegrationResult
```

The integration shall use the existing enterprise integration infrastructure rather than introducing a private Procurement ↔ Finance transport mechanism.

---

# 11. Existing Enterprise Integration Framework

The existing framework remains authoritative for cross-capability integration.

The framework includes:

```text
app/core/integration/models.py
app/core/integration/service.py
app/core/integration/providers/base.py
app/core/integration/providers/registry.py
```

The generic `IntegrationRequest` remains unchanged.

The generic integration framework is responsible for:

- request envelope;
- provider resolution;
- operation resolution;
- provider validation;
- provider execution;
- standardized response;
- standardized result;
- integration errors;
- lifecycle handling.

The Finance integration contract shall build on this framework.

---

# 12. Finance Provider Boundary

The future Finance integration shall be represented through the enterprise Integration Provider mechanism.

A Finance provider identity may be established as:

```text
finance
```

This is the architectural provider identity.

The exact implementation constant, registration location, and operation naming remain implementation concerns and shall be finalized during the implementation stage without changing this architectural boundary.

---

# 13. Domain-Specific Finance Integration Payload

The generic `IntegrationRequest` shall remain unchanged.

Finance-specific business information shall be carried in a domain-specific payload.

A candidate implementation name such as:

```text
ProcurementFinancialEffectRequest
```

may be used during implementation, but the exact class name is not locked by this document.

The payload must communicate Procurement facts rather than prescribe Finance accounting treatment.

---

# 14. Procurement Information That May Be Communicated

The Finance integration payload may contain information such as:

### 14.1 Procurement Identity

- Purchase Order reference;
- Purchase Request reference, where relevant;
- procurement transaction reference;
- business operation reference;
- source-system/platform reference.

### 14.2 Supplier Information

Where required by the integration contract:

- supplier reference;
- supplier display/name information;
- supplier-facing procurement reference.

Supplier identity remains Procurement-owned.

### 14.3 Purchase Order Information

Potential information includes:

- Purchase Order reference;
- Purchase Order date;
- approval status;
- approval timestamp;
- supplier reference;
- currency;
- total procurement value;
- relevant procurement terms;
- organizational/unit context.

### 14.4 Purchase Order Line Information

Potential information includes:

- Purchase Order Line reference;
- description;
- quantity;
- unit;
- unit price;
- line amount;
- currency;
- procurement classification/reference where applicable.

### 14.5 Procurement Context

The payload may also identify:

- originating capability;
- originating module;
- transaction type;
- organizational context;
- business unit context;
- source platform reference.

The exact payload fields shall be finalized during implementation based on the approved Finance contract.

---

# 15. Information Procurement Must Not Prescribe

Procurement shall not send information that attempts to dictate Finance-owned accounting treatment.

The Procurement → Finance contract shall not prescribe:

- general ledger account;
- debit account;
- credit account;
- journal entry;
- accounting posting;
- financial ledger record;
- payment instruction;
- payment status;
- supplier settlement status;
- Finance invoice identifier;
- Finance receipt identifier;
- Finance transaction identifier;
- Finance accounting classification;
- Finance posting decision.

Where such information exists, it is Finance-owned.

---

# 16. Finance Determines Financial Treatment

The Finance capability determines:

1. whether the Procurement information creates a Finance-owned financial effect;
2. what financial treatment applies;
3. whether an invoice or other Finance record is required;
4. what accounting classification applies;
5. whether accounting recognition occurs;
6. whether a ledger entry is created;
7. whether payment or settlement becomes relevant;
8. what Finance lifecycle applies.

Procurement provides facts.

Finance determines financial treatment.

---

# 17. No Direct Cross-Module Persistence

Procurement shall not directly access Finance persistence.

The following are prohibited:

```text
Procurement Repository
        ↓
Finance Repository
```

and:

```text
Procurement Service
        ↓
Finance Database Table
```

and:

```text
Procurement Model
        ↓
Finance-Owned Foreign Key
```

The integration boundary shall remain explicit.

There shall be no direct Procurement → Finance database mutation.

---

# 18. No Direct Cross-Module Foreign Keys

Procurement and Finance shall not establish hidden database coupling through direct cross-module foreign keys merely to support integration.

Business references shall be communicated through the integration contract.

The Finance representation of a Procurement Purchase Order is Finance-owned.

The Procurement Purchase Order remains Procurement-owned.

---

# 19. Integration Response Semantics

A successful `IntegrationResponse` means that the Finance integration boundary has successfully accepted or processed the request according to the agreed integration contract.

It does **not** mean that:

- accounting recognition necessarily occurred;
- a ledger entry necessarily exists;
- an invoice necessarily exists;
- payment necessarily occurred;
- supplier settlement necessarily occurred.

The Finance response may provide:

- success/failure;
- Finance processing reference, where applicable;
- processing message;
- standardized error information;
- metadata;
- request identity.

The exact Finance response payload is Finance-owned and shall be finalized separately.

---

# 20. Integration Failure Semantics

Integration failure is distinct from Procurement business failure.

If Finance integration fails after the Purchase Order has successfully reached `APPROVED`:

- the Purchase Order remains `APPROVED`;
- Procurement approval is not automatically reversed;
- Procurement does not create a compensating cancellation merely because integration failed;
- Finance processing may be retried;
- the failure is recorded through enterprise integration lifecycle mechanisms.

Therefore:

> Integration failure shall not automatically reverse Procurement approval.

---

# 21. Failure Categories

Integration failures should be understood in three broad categories.

## 21.1 Request / Contract Failure

Examples:

- invalid request;
- invalid payload;
- missing required business reference;
- unsupported operation;
- invalid integration envelope.

## 21.2 Delivery / Execution Failure

Examples:

- provider unavailable;
- delivery failure;
- timeout;
- infrastructure failure;
- unexpected execution exception.

## 21.3 Finance Business Rejection

A Finance provider may reject a request because of a Finance-owned business rule.

This is a Finance outcome, not a Procurement Purchase Order rejection.

The exact Finance business rejection taxonomy is deferred to Finance architecture.

---

# 22. Retry Architecture

Integration retry shall be independent of Procurement transaction state.

A failed Finance integration may be retried without re-running the Procurement Purchase Order approval transition.

The retry must represent the same underlying Procurement business fact.

Therefore:

```text
PO APPROVED
    │
    └── Finance integration attempt
            │
            ├── SUCCESS
            │
            └── FAILURE
                  │
                  └── RETRY
                       │
                       └── same business-operation identity
```

Retry shall not create a second Procurement approval.

---

# 23. Idempotency

Finance integration shall be idempotent at the business-operation level.

Idempotency shall not be based merely on:

```text
Purchase Order ID
```

because a Purchase Order may have multiple distinct future financial operations.

The idempotency identity shall represent the specific business operation/fact being communicated.

For the initial approved-commitment integration, the conceptual identity is:

```text
Purchase Order
+
Approved Commitment Operation
```

The exact idempotency-key format remains an implementation decision.

The same business operation must retain the same identity across retries.

---

# 24. Lifecycle Fact Versus Integration Operation

The Procurement lifecycle fact and the integration operation are separate concepts.

The lifecycle fact is:

```text
Purchase Order successfully transitions to APPROVED
```

The integration operation communicates that fact to Finance.

This distinction prevents integration mechanics from becoming part of the Procurement workflow.

---

# 25. Cancellation After Approval

Cancellation is a distinct Procurement business fact.

A Purchase Order that has reached `APPROVED` may subsequently transition to:

```text
CANCELLED
```

This cancellation is not the same operation as the original approval communication.

A future Finance integration may communicate cancellation or another financially significant change.

However:

- cancellation communication is not part of the initial approved-commitment contract;
- no exact cancellation operation is locked here;
- Finance determines the financial consequence;
- any cancellation integration requires explicit architecture approval before implementation.

---

# 26. Changes After Approval

Not every Purchase Order update should automatically generate a Finance integration operation.

A generic:

```text
purchase_order.updated
```

integration operation is not approved by this decision.

Only explicitly defined Procurement facts that are determined to be financially significant may become Finance-facing operations.

Each such operation shall be separately defined and governed.

---

# 27. Physical Receipt Remains Separate

Physical receipt is not part of the Procurement → Finance approval integration.

The approved architecture remains:

```text
Purchase Order APPROVED
        │
        ├── Finance communication
        │
        └── physical receipt
                │
                ▼
             Inventory
```

Inventory remains authoritative for physical stock effects.

A Purchase Order being approved does not create stock.

A Finance integration response does not create stock.

Finance shall not post physical stock movements.

---

# 28. Procurement ↔ Inventory Boundary Remains Authoritative

The existing Procurement ↔ Inventory integration contract remains unchanged.

The Inventory capability remains authoritative for:

- StockMovement;
- StockBalance;
- physical stock effect;
- inventory transaction boundaries;
- receipt posting.

The Finance integration shall not duplicate or replace the Procurement ↔ Inventory receiving contract.

---

# 29. Expense Management Remains Separate

Expense Management remains a distinct capability.

In particular:

```text
Expense APPROVED
```

does not automatically mean:

- payment;
- reimbursement;
- accounting recognition;
- financial settlement;
- ledger posting.

Finance integration for Expense Management may be designed separately.

This Procurement ↔ Finance decision shall not introduce an Expense → Finance implementation.

---

# 30. Transaction Boundary

Procurement and Finance shall retain separate transaction boundaries.

The integration shall not require a shared transaction across the two capabilities.

The architectural model is:

```text
Procurement Transaction
        │
        └── commits Procurement fact
                 │
                 ▼
          Integration Boundary
                 │
                 ▼
           Finance Transaction
```

Each capability remains authoritative for its own persistence.

---

# 31. No Distributed Transactions

The integration shall not introduce:

- distributed transactions;
- two-phase commit;
- shared transaction managers;
- manual transaction-manager coordination;
- shared database transaction scope;
- repository-level cross-module rollback;
- compensating database operations owned by Procurement.

A Finance failure shall be handled as an integration failure rather than by attempting to roll back a previously committed Procurement transaction.

---

# 32. Security and Authorization

Security and authorization shall reuse enterprise infrastructure.

The Finance integration must execute within the established authorization/governance boundary.

Procurement users shall not receive direct permissions to modify Finance-owned records.

Finance permissions remain Finance-owned.

The integration mechanism must not create a hidden authorization bypass.

The architectural flow is:

```text
Enterprise Authorization
        ↓
Procurement Business Action
        ↓
Integration Lifecycle
        ↓
Finance Provider
```

No parallel authorization framework shall be created for this integration.

---

# 33. Audit

Integration activity shall use the existing enterprise audit infrastructure.

At minimum, integration lifecycle records should identify:

- provider;
- operation;
- integration request identity;
- business reference;
- execution subject;
- outcome;
- timestamp;
- failure information where applicable.

Integration audit records are not financial accounting records.

An audit record stating that a Procurement commitment was communicated to Finance does not itself constitute:

- an accounting entry;
- a journal entry;
- a financial transaction;
- an invoice;
- a payment;
- a ledger record.

---

# 34. Integration Events

The existing enterprise integration lifecycle event model shall be reused.

Relevant lifecycle events include:

```text
integration.request
integration.result
integration.failure
```

These events represent integration execution.

They are not accounting events.

Finance-specific accounting events, if required, remain Finance-owned and require separate Finance architecture.

---

# 35. Governance

The integration shall reuse enterprise governance mechanisms for:

- command authorization;
- business authorization;
- transaction boundaries;
- integration lifecycle;
- audit;
- standardized errors;
- provider registration;
- observability.

Procurement shall not introduce private versions of these enterprise capabilities.

---

# 36. Observability

Integration observability should make it possible to identify:

- business reference;
- provider;
- operation;
- request identity;
- outcome;
- retry state where applicable;
- failure category;
- execution subject;
- timestamp.

Observability must allow operators to distinguish:

```text
Procurement business state
```

from:

```text
Integration execution state
```

and from:

```text
Finance financial state
```

---

# 37. Integration Status Separation

If Procurement later requires local integration-status visibility, that status must remain an integration/execution status rather than a financial or Procurement workflow state.

Potential integration statuses may conceptually include:

```text
PENDING
SUCCEEDED
FAILED
RETRY_REQUIRED
```

These are not approved Purchase Order workflow states.

No integration-status persistence model is introduced by this decision.

---

# 38. No Automatic Procurement Compensation

A Finance integration failure shall not automatically create:

- Purchase Order rejection;
- Purchase Order cancellation;
- Purchase Request reversal;
- supplier status reversal;
- accounting reversal;
- Procurement compensation transaction.

Any such action requires a separately defined business rule and explicit architecture decision.

---

# 39. Reverse Communication

This decision does not authorize Finance to directly mutate Procurement state.

If Finance later needs to communicate a business fact back to Procurement, that communication must use a separate explicit integration contract.

Examples may include:

- Finance-side processing status;
- financial rejection requiring Procurement attention;
- financial transaction reference;
- settlement status.

Such information does not gain authority over Procurement lifecycle merely because Finance communicates it.

---

# 40. Procurement Financial Effect Boundary

Procurement may communicate facts that have potential financial significance.

Procurement shall not determine the final financial effect.

The distinction is:

```text
Procurement:
"What procurement transaction occurred?"

Finance:
"What financial treatment does that transaction require?"
```

This separation is fundamental to the architecture.

---

# 41. Supplier Identity Boundary

Procurement remains authoritative for supplier identity within the Procurement domain.

Finance may maintain its own Finance representation of a supplier.

The integration shall therefore communicate a supplier reference or business identity where required rather than introducing a direct cross-module supplier foreign key.

Finance determines how supplier information is represented internally.

---

# 42. Purchase Order Identity Boundary

The Procurement Purchase Order reference remains authoritative within Procurement.

Finance may store a corresponding reference to the originating Procurement transaction.

Such a reference is an integration/business reference, not a shared ownership model.

Finance shall not become the owner of the Procurement Purchase Order.

---

# 43. Purchase Order Line Boundary

Purchase Order Lines remain Procurement-owned.

Finance may receive line-level information where required for Finance processing.

A Finance-side representation of a Purchase Order Line does not make Finance the owner of the Procurement line.

Similarly, Procurement shall not create Finance-owned accounting line structures.

---

# 44. Architectural Invariants

The following invariants are locked.

### Invariant 1

Procurement owns Purchase Orders and Procurement lifecycle.

### Invariant 2

Finance owns financial treatment and accounting records.

### Invariant 3

Successful transition of a Purchase Order to `APPROVED` creates the Procurement business fact eligible for Finance communication.

### Invariant 4

Purchase Order approval is not itself accounting recognition.

### Invariant 5

The existing enterprise Integration Framework is mandatory.

### Invariant 6

Procurement communicates Procurement facts, not accounting instructions.

### Invariant 7

Finance determines financial treatment.

### Invariant 8

Finance integration outcome does not automatically change Procurement Purchase Order state.

### Invariant 9

Integration failure does not automatically reverse Procurement approval.

### Invariant 10

Retry preserves the identity of the underlying business operation.

### Invariant 11

Cancellation is a separate Procurement business fact.

### Invariant 12

Procurement shall not directly mutate Finance persistence.

### Invariant 13

Finance shall not directly mutate Procurement persistence.

### Invariant 14

No direct Procurement ↔ Finance foreign-key coupling shall be introduced.

### Invariant 15

No distributed transaction shall be introduced.

### Invariant 16

Enterprise authorization, audit, events, lifecycle, and governance infrastructure shall be reused.

### Invariant 17

Integration lifecycle records are not financial accounting records.

### Invariant 18

Inventory remains authoritative for physical stock effects.

### Invariant 19

Finance-specific implementation shall not be simulated inside Procurement.

### Invariant 20

Finance workflow and financial lifecycle shall remain separate from Procurement workflow.

---

# 45. Explicitly Prohibited Architecture

The following patterns are explicitly prohibited:

```text
Procurement
    └── private accounting ledger
```

```text
Procurement
    └── private payment processor
```

```text
Procurement
    └── Finance repository access
```

```text
Procurement
    └── Finance database mutation
```

```text
Procurement PurchaseOrder
    └── Finance foreign key
```

```text
Finance
    └── direct Procurement repository mutation
```

```text
Purchase Order APPROVED
    └── automatic ledger posting by Procurement
```

```text
Finance integration failure
    └── automatic PO rejection
```

```text
Finance integration failure
    └── automatic PO cancellation
```

```text
Finance state
    └── embedded inside Procurement PO workflow
```

```text
Procurement + Finance
    └── distributed transaction
```

---

# 46. Deferred Decisions

The following remain intentionally deferred:

1. Finance entity model.
2. Financial transaction model.
3. Financial ledger model.
4. Journal model.
5. Chart of accounts.
6. Invoice model.
7. Payment model.
8. Receipt model.
9. Settlement model.
10. Accounting recognition rules.
11. Financial posting rules.
12. Finance workflow.
13. Finance HTTP/UI.
14. Finance database schema.
15. Exact Finance provider registration implementation.
16. Exact Finance operation constant/name.
17. Exact domain payload class name.
18. Exact payload field schema.
19. Exact idempotency-key format.
20. Integration-status persistence model.
21. Retry implementation.
22. Purchase Order cancellation integration operation.
23. Purchase Order amendment/adjustment integration operations.
24. Invoice-related Procurement → Finance operations.
25. Finance → Procurement reverse communication contracts.

Each deferred item shall be addressed only when the relevant Finance or integration stage is formally entered.

---

# 47. Implementation Constraints

Implementation following this decision must not introduce Finance entities merely to make the integration executable.

The first implementation stage shall establish only the approved integration boundary and contract.

Implementation shall not include:

- general ledger;
- accounting entries;
- payment processing;
- supplier settlement;
- invoice processing;
- financial transaction persistence;

unless those capabilities are separately designed and approved.

---

# 48. Implementation Sequence

The implementation should proceed in controlled stages.

## Stage 1 — Integration Contract Foundation [COMPLETED]

Establish:

- Finance provider boundary;
- domain integration payload contract;
- operation contract;
- request/response expectations;
- enterprise Integration Framework wiring.

No Finance accounting persistence.

## Stage 2 — Post-Commit Execution Capability [NEXT]

Establish the generic enterprise capability, not Finance-specific wiring:

- post-commit execution abstraction;
- commit executor;
- execution only after successful transaction commit;
- post-commit failure isolation from the committed transaction;
- reusable capability for future business integrations.

## Stage 3 — Procurement Approval Integration Boundary [NEXT]

Wire the successful:

```text
Purchase Order → APPROVED
```

business transition to the approved Finance integration boundary.

The Procurement transaction must remain authoritative.

## Stage 4 — Response and Failure Handling

Implement:

- standardized success;
- Finance rejection;
- integration failure;
- error classification;
- lifecycle handling.

## Stage 5 — Retry and Idempotency

Implement:

- business-operation identity;
- idempotent retry;
- observability;
- retry handling.

## Stage 6 — Security, Audit and Governance Verification

Verify:

- authorization;
- audit;
- integration lifecycle;
- events;
- transaction boundaries;
- no cross-module persistence.

## Stage 7 — End-to-End Verification

Verify the real enterprise path:

```text
Purchase Order
    ↓
APPROVED
    ↓
Enterprise Integration Framework
    ↓
Finance Provider Boundary
    ↓
IntegrationResponse
    ↓
IntegrationResult
```

Finance financial persistence remains outside this stage unless separately approved.

---

# 49. Verification Requirements

Verification shall demonstrate that:

1. Purchase Order approval remains Procurement-owned.
2. Finance integration occurs only after successful approval.
3. Finance integration does not alter Procurement workflow state.
4. Integration failure does not reverse approval.
5. Retry does not create a second Procurement approval.
6. Business-operation identity is preserved.
7. No direct Finance repository access exists in Procurement.
8. No direct Procurement repository mutation exists in Finance.
9. No direct cross-module foreign keys are introduced.
10. Enterprise authorization is enforced.
11. Enterprise audit is used.
12. Enterprise integration lifecycle is used.
13. Integration events use the enterprise event boundary.
14. Inventory remains independent and authoritative for physical stock.
15. No distributed transaction is introduced.
16. Finance accounting implementation is not duplicated in Procurement.

---

# 50. Relationship to Existing Procurement ↔ Inventory Architecture

This decision does not modify the approved Procurement ↔ Inventory integration architecture.

The two integration boundaries remain independent:

```text
                 ┌───────────────┐
                 │   Procurement │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        ┌───────────┐         ┌───────────┐
        │  Finance  │         │ Inventory │
        └───────────┘         └───────────┘
```

Finance owns financial treatment.

Inventory owns physical stock effects.

Procurement owns procurement lifecycle.

No integration may collapse these ownership boundaries.

---

# 51. Relationship to Expense Management

Expense Management remains independently governed.

The approval or closure of an Expense does not automatically imply:

- financial payment;
- reimbursement;
- accounting recognition;
- ledger posting;
- settlement.

Any Expense → Finance integration shall require a separate architecture decision.

---

# 52. Relationship to Reporting

Reporting remains a consumer of approved read models.

Reporting shall not become an integration intermediary between Procurement and Finance.

The Procurement → Finance communication shall occur directly through the enterprise integration boundary.

Reporting may later consume:

- Procurement data;
- Finance data;
- integration status/read models;

according to the Reporting architecture.

---

# 53. Architectural Decision Statement

The authoritative decision is:

> **CDCS-EMP Procurement shall communicate an approved procurement commitment to the future Finance capability through the existing enterprise Integration Framework. Procurement remains authoritative for Purchase Orders, suppliers, procurement transactions, and procurement lifecycle, while Finance remains authoritative for financial treatment, accounting, invoices, payments, receipts, settlement, and ledger information. The successful transition of a Purchase Order to `APPROVED` constitutes the Procurement business fact eligible for Finance communication. Finance processing, integration failure, retry, and subsequent financial treatment shall remain separate from Procurement workflow state. No direct cross-module persistence, shared financial ledger, or distributed transaction shall be introduced.**

---

# 54. Final Locked Architecture

The resulting architecture is:

PROCUREMENT
│
└── Purchase Order
      │
      ├── SUBMIT
      ↓
   SUBMITTED
      │
      └── APPROVE
            ↓
        APPROVED
            │
            │ Procurement business fact
            ↓
     Procurement transaction
            │
            └── COMMIT
                  │
                  ↓
          Post-Commit Executor
                  │
                  ↓
    Enterprise Integration Framework
                  │
                  ↓
          Finance Provider
                  │
                  ↓
               FINANCE
                  │
                  ├── Financial treatment
                  ├── Accounting
                  ├── Invoice
                  ├── Payment
                  ├── Settlement
                  └── Ledger

Separately:

APPROVED PURCHASE ORDER
            │
            ↓
     Physical Receipt
            │
            ↓
        INVENTORY
            │
            └── Stock Effect

The three ownership boundaries remain independent:

```text
Procurement → Procurement facts
Finance     → Financial treatment
Inventory   → Physical stock effects
```

Finance communication occurs only after the successful Procurement transaction containing the SUBMITTED → APPROVED transition has committed. Failure of the post-commit Finance integration does not roll back, reject, cancel, or otherwise alter the already-committed Purchase Order approval.

---

# 55. Governance Rule for Future Stages

Any future implementation or architecture proposal that crosses the Procurement ↔ Finance boundary must be checked against this decision before implementation.

A proposal must not introduce:

- hidden cross-module persistence;
- duplicated Finance logic;
- Procurement-owned accounting;
- direct Finance repository mutation;
- Finance-owned Procurement state;
- distributed transactions;
- implicit financial posting;
- implicit payment;
- implicit settlement.

If a future requirement cannot be satisfied within this contract, a new architecture decision or explicit amendment must be approved before implementation.

---

# 56. Approval Record

This architecture decision consolidates the previously reviewed Procurement ↔ Finance design drafts and the final architecture reconciliation.

The user has approved the reconciliation and authorized consolidation into this final authoritative architecture decision.

**Approval Status:** APPROVED
**Architecture Status:** ACTIVE / LOCKED
**Implementation Status:** PENDING IMPLEMENTATION

The implementation shall follow this decision unless a subsequent approved architecture decision explicitly supersedes or amends it.

---

# 57. Authoritative Document

**File:**

```text
docs\architecture\decisions\PHASE-2.2-PROCUREMENT-FINANCE-INTEGRATION-CONTRACT.md
```

This document becomes the authoritative Procurement ↔ Finance integration architecture for Phase 2.2 after being saved and committed to the repository.

---

# 58. Related Architecture Decisions

This decision should be read together with:

- `PHASE-2.2-PURCHASING-EXPENSE-MANAGEMENT.md`
- `PHASE-2.2-PROCUREMENT-INVENTORY-INTEGRATION-CONTRACT.md`
- applicable enterprise integration architecture;
- applicable enterprise execution/security/governance architecture;
- applicable Expense Management architecture.

The Phase 2.2 Purchasing & Expense Management roadmap remains authoritative for sequencing subsequent business-capability stages.

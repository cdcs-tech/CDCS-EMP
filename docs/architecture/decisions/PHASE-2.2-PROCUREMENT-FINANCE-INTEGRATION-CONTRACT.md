# PHASE 2.2 — PROCUREMENT ↔ FINANCE INTEGRATION CONTRACT

**Document Status:** APPROVED / ACTIVE / LOCKED
**Phase:** Phase 2.2 — Purchasing & Expense Management
**Decision Area:** Procurement ↔ Finance Integration
**Decision Date:** 25 September 2026
**Documentation Date:** 25 September 2026
**Decision Type:** Architecture / Integration Boundary / Ownership
**Implementation Status:** Stages 1–4 Completed — Stage 5 Architecture Approved / Implementation Pending

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

## 10. Integration Architecture

The Procurement ↔ Finance integration shall use the existing enterprise Integration Framework and shall remain strictly separated from the Procurement transaction boundary.

The implemented integration path is:

```text
Purchase Order APPROVED
        ↓
Procurement Transaction
        ↓
Transaction COMMIT
        ↓
Post-Commit Executor
        ↓
Procurement Finance Integration Adapter
        ↓
IntegrationLifecycle
        ↓
IntegrationService
        ↓
IntegrationProviderRegistry
        ↓
Finance Integration Provider
        ↓
Finance Capability
        ↓
IntegrationResponse
        ↓
IntegrationResult
```

The architecture therefore separates three concerns:

1. **Procurement business state**
   - Purchase Order approval remains owned by Procurement.
   - The Purchase Order reaches `APPROVED` through the normal Procurement workflow.
   - Approval is committed through the normal Procurement transaction.

2. **Integration execution**
   - Finance communication occurs only after the Procurement transaction has successfully committed.
   - The post-commit execution boundary invokes the Procurement Finance integration adapter.
   - The adapter uses the enterprise `IntegrationLifecycle`, which provides the standard integration request, execution, result, audit, and event lifecycle.

3. **Finance processing**
   - The Finance provider receives the approved Procurement business fact through the enterprise integration boundary.
   - Finance remains responsible for its own financial processing and persistence.
   - Finance does not become part of the Procurement transaction.

The Procurement Finance integration shall not introduce a private integration mechanism, direct Finance service invocation, direct Finance repository access, or direct Finance database persistence.

---

## 11. Enterprise Integration Framework

The Procurement ↔ Finance integration shall reuse the existing enterprise Integration Framework.

The authoritative framework components are:

- `app/core/integration/models.py`
  - `IntegrationRequest`
  - `IntegrationResponse`
  - `IntegrationResult`

- `app/core/integration/service.py`
  - `IntegrationService`

- `app/core/integration/provider.py`
  - Integration provider contract

- `app/core/integration/provider_registry.py`
  - Provider registration and resolution

- `app/core/integration/lifecycle.py`
  - `IntegrationLifecycle`

- Enterprise integration audit and event hooks
  - Integration request/result/failure observability

The Integration Framework is responsible for:

- integration request envelopes;
- provider identity;
- operation identity;
- request validation;
- provider resolution;
- provider execution;
- response normalization;
- result construction;
- integration lifecycle observability;
- integration audit records;
- integration lifecycle events;
- integration exception handling.

The Procurement module remains responsible for:

- determining when the Procurement business fact exists;
- constructing the domain-specific financial-effect request;
- maintaining Procurement-owned integration commitment state;
- determining Procurement-side retry eligibility;
- preserving business-operation identity across retries.

The Finance provider remains responsible for:

- accepting the Procurement integration request;
- performing Finance-side processing;
- determining Finance-side financial treatment;
- returning the appropriate integration response.

The Procurement Finance integration shall not create a second integration framework.

---

## 12. Finance Provider and Operation Contract

The Procurement ↔ Finance integration uses the enterprise Finance provider identity:

```text
Provider:
finance
```

The approved Procurement commitment operation is:

```text
Operation:
procurement_commitment
```

These identifiers form part of the enterprise integration contract and shall be used consistently by the Procurement integration adapter and Finance provider registration.

The integration boundary is therefore:

```text
Provider = finance
Operation = procurement_commitment
```

The Finance provider remains an integration boundary. Procurement shall not directly invoke internal Finance services, repositories, database operations, accounting functions, or financial persistence mechanisms.

Finance provider implementation details remain Finance-owned and shall not be simulated or duplicated inside Procurement.

---

## 13. Domain Integration Payload

The Procurement Finance integration shall use the Procurement-owned domain contract:

```text
ProcurementFinancialEffectRequest
```

The request represents the financial effect associated with an approved Procurement commitment.

The domain request contains the Procurement information required to communicate that business fact, including:

- Purchase Order reference;
- Purchase Request reference;
- supplier reference;
- Purchase Order date;
- approval timestamp;
- currency;
- total Procurement value;
- relevant Purchase Order lines;
- deterministic business-operation idempotency key.

The domain payload remains Procurement-owned.

The payload shall communicate Procurement facts and commercial information required by the Finance boundary. It shall not contain Finance accounting instructions.

Procurement shall not provide:

- General Ledger account assignments;
- debit/credit instructions;
- journal entries;
- ledger posting instructions;
- payment instructions;
- settlement instructions;
- Finance accounting classifications;
- Finance recognition decisions.

Finance remains responsible for determining the financial treatment of the Procurement business fact.

The currently implemented deterministic idempotency key is:

```text
procurement-commitment:<purchase_order.reference>
```

This key identifies the underlying Procurement financial commitment operation and is distinct from an individual enterprise integration request identity.

---

## 14. Information Communicated to Finance

The Procurement ↔ Finance integration may communicate the Procurement information required to establish the financial context of the approved Procurement commitment.

The approved implementation communicates:

### Procurement identity

- Purchase Order reference;
- Purchase Request reference;
- supplier reference.

### Procurement dates and state

- Purchase Order date;
- approval timestamp;
- approved Procurement context.

### Commercial information

- currency;
- total Procurement value;
- Purchase Order line information required by the domain contract.

### Integration identity

- Procurement financial commitment idempotency key;
- enterprise integration request identity for the individual integration attempt.

The information communicated shall remain limited to the business purpose of the approved Procurement commitment.

Procurement shall not communicate accounting instructions or attempt to determine Finance-owned treatment.

---

## 15. Information Explicitly Excluded from the Procurement Payload

The Procurement Finance integration shall not use the Procurement payload to prescribe Finance accounting treatment.

The following information remains Finance-owned and shall not be supplied as Procurement accounting instructions:

- General Ledger account;
- debit account;
- credit account;
- journal entry;
- journal posting instruction;
- ledger posting instruction;
- accounting recognition decision;
- payment instruction;
- payment execution state;
- settlement instruction;
- settlement state;
- Finance invoice identifier;
- Finance receipt identifier;
- Finance transaction identifier;
- Finance accounting classification;
- Finance posting decision.

Where Finance requires additional information for its own processing, that requirement shall be addressed through a separately approved Finance integration contract rather than by expanding Procurement into Finance ownership.

---

## 16. Finance Determines Financial Treatment

The Procurement module communicates an approved Procurement business fact.

Finance determines the subsequent financial treatment of that fact.

The Finance capability may determine, according to Finance-owned rules:

- whether and how the commitment is financially recognized;
- accounting classification;
- ledger treatment;
- financial transaction creation;
- invoice treatment;
- payment treatment;
- settlement treatment;
- reconciliation requirements.

None of these responsibilities shall be implemented inside Procurement solely to support the Procurement ↔ Finance integration.

The existence of a successful Procurement commitment integration response shall not be interpreted as Procurement having performed accounting recognition.

---

## 17. No Direct Cross-Module Persistence

Procurement shall not directly persist Finance-owned entities.

The Procurement module shall not:

- import Finance repositories;
- write Finance database tables;
- create Finance-owned records;
- update Finance-owned records;
- maintain Finance-owned accounting state;
- use Finance database identifiers as Procurement-owned foreign keys.

Likewise, Finance shall not directly persist or mutate Procurement-owned entities.

Cross-module communication shall occur through the approved enterprise Integration Framework.

The Procurement Finance commitment state introduced for retry and idempotency is **Procurement-owned integration-delivery state**. It is not Finance persistence and shall not represent Finance accounting state.

---

## 18. No Cross-Module Foreign Keys

The Procurement ↔ Finance integration shall not introduce database foreign keys between Procurement-owned and Finance-owned entities.

Procurement may maintain references necessary to identify its own business objects and its own integration-delivery state.

Finance-owned identifiers, once returned by Finance, shall remain integration data rather than becoming database relationships from Procurement into Finance-owned persistence.

The integration boundary is therefore:

```text
Procurement-owned persistence
        ↕
Enterprise Integration Framework
        ↕
Finance-owned persistence
```

and not:

```text
Procurement database
        ↕
Finance database
```

---

## 19. Integration Response Semantics

The Finance integration response shall use the enterprise `IntegrationResponse` and `IntegrationResult` contracts.

A successful response indicates that the Finance integration boundary accepted or successfully processed the request according to the Finance provider contract.

A successful integration response does **not** by itself mean that:

- accounting recognition has occurred;
- a ledger entry has been posted;
- an invoice has been created;
- payment has been executed;
- supplier settlement has occurred;
- Finance reconciliation is complete.

A provider-declared unsuccessful response is represented by:

```text
IntegrationResponse(success=False)
```

and produces:

```text
IntegrationResult.failed == True
```

The Procurement integration lifecycle shall preserve this distinction between:

1. a provider-declared business outcome; and
2. a technical failure during delivery or execution.

Integration responses may contain provider-defined:

- success/failure information;
- Finance reference information;
- message;
- error information;
- response metadata;
- integration request identity.

Finance owns the meaning of Finance-specific response data.

---

## 20. Integration Failure Semantics

A Finance integration failure shall not automatically reverse, reject, or cancel an already approved Purchase Order.

The following principle is mandatory:

```text
Procurement Approval
        ↓
PO becomes APPROVED
        ↓
Procurement transaction commits
        ↓
Finance integration may succeed or fail
```

Therefore:

> Integration failure shall not automatically reverse Procurement approval.

The Purchase Order remains in its valid Procurement state even where Finance communication fails.

Failure handling belongs to the integration-delivery lifecycle and the Procurement-owned commitment/retry mechanism.

Where a technical delivery failure occurs, the Procurement Finance commitment may become eligible for retry without rerunning the Purchase Order approval.

Where Finance explicitly rejects the request as a business outcome, the Procurement Purchase Order remains approved and the Finance outcome remains separate from the Procurement workflow.

---

## 21. Integration Failure Categories

The Procurement ↔ Finance integration recognizes the following broad failure categories:

### 21.1 Request or Contract Failure

The integration request cannot be validly constructed, validated, or accepted by the enterprise integration contract.

Examples include:

- invalid request structure;
- missing required integration information;
- unsupported operation;
- invalid provider contract.

Such failures do not constitute successful Finance processing.

They are not a reason to alter the Procurement Purchase Order workflow.

Automatic retry shall not be assumed for request or contract failures unless a separate retry rule explicitly permits it.

### 21.2 Technical Delivery or Execution Failure

The request cannot successfully reach or execute through the Finance provider because of a technical integration failure.

Examples include:

- provider execution exception;
- transport or delivery failure;
- unavailable integration endpoint;
- technical provider failure.

These failures are eligible for the Stage 5 retry mechanism.

### 21.3 Finance Business Rejection

The Finance provider successfully receives and processes the integration request but returns a business-level unsuccessful response.

Represented by:

```text
IntegrationResponse(success=False)
```

This is a provider-declared outcome rather than a technical delivery exception.

A Finance business rejection shall not automatically trigger another Procurement approval and shall not automatically reverse the approved Purchase Order.

Provider-declared business rejection is not automatically retryable under the Stage 5 architecture.

---

## 22. Retry Architecture

Finance integration retry shall be independent of the Procurement Purchase Order approval workflow.

The architectural sequence is:

```text
Purchase Order APPROVED
        ↓
Procurement Finance Commitment created
        ↓
Procurement transaction COMMIT
        ↓
Finance integration attempt
        ↓
      ┌───────────────┐
      │               │
   SUCCESS         TECHNICAL
                   FAILURE
      │               │
      ↓               ↓
  COMMITTED      RETRYABLE_FAILURE
                      │
                      ↓
                Eligible Retry
                      │
                      ↓
              New Integration Attempt
                      │
                      ↓
              Same Business Identity
```

A retry shall:

- not rerun Purchase Order approval;
- not create another Purchase Order;
- not create another Procurement approval event;
- preserve the same Procurement financial commitment identity;
- preserve the same idempotency key;
- create a new enterprise integration request identity for the individual attempt.

The retry mechanism is therefore an integration-delivery mechanism, not a Procurement workflow mechanism.

Stage 5 shall introduce durable Procurement-owned commitment state so that a pending or retryable Finance commitment survives an application failure occurring after Procurement commit.

A generic enterprise queue, worker framework, message broker, or background-job infrastructure is not introduced as part of this stage.

---

## 23. Idempotency Architecture

Idempotency shall operate at the **business-operation level** rather than solely at the Purchase Order identifier level.

The approved Procurement Finance commitment operation uses:

```text
procurement-commitment:<purchase_order.reference>
```

as its deterministic business-operation idempotency key.

The architecture distinguishes two identities:

### 23.1 Enterprise Integration Request Identity

`IntegrationRequest.request_id` identifies an individual integration attempt.

Each new delivery attempt may therefore have a new:

```text
request_id
```

### 23.2 Procurement Finance Commitment Identity

`ProcurementFinanceCommitment.idempotency_key` identifies the underlying Procurement financial commitment business operation.

The same:

```text
idempotency_key
```

shall be preserved across retries.

Therefore:

```text
Attempt 1
request_id = A
idempotency_key = procurement-commitment:PO-001

Attempt 2
request_id = B
idempotency_key = procurement-commitment:PO-001

Attempt 3
request_id = C
idempotency_key = procurement-commitment:PO-001
```

The request identities differ because they represent different delivery attempts.

The idempotency key remains constant because all attempts represent the same underlying Procurement financial commitment.

Stage 5 shall enforce durable uniqueness of the Procurement commitment idempotency key.

The idempotency mechanism shall prevent duplicate registration of the same Procurement financial commitment while allowing subsequent delivery attempts to reuse the same business-operation identity.

If Finance accepts a request but the application fails before local commitment state is updated, a subsequent retry shall use the same idempotency key. Where Finance supports corresponding idempotent processing, this allows the Finance boundary to recognize the same business operation rather than treating the retry as a new financial commitment.

Idempotency shall not be implemented by modifying `IntegrationRequest.request_id`.

`request_id` remains attempt identity; `idempotency_key` remains business-operation identity.

---

## 24. Procurement Lifecycle Fact vs. Integration Operation

The Procurement Purchase Order approval is a Procurement lifecycle fact.

The Finance communication is a separate integration operation that communicates that fact to the Finance boundary.

The distinction is:

```text
Procurement Lifecycle Fact
        │
        │
        ▼
Purchase Order becomes APPROVED
        │
        │
        ▼
Procurement Finance Commitment
        │
        │
        ▼
Finance Integration Operation
```

The Procurement workflow shall not contain Finance processing logic.

The Procurement Purchase Order workflow is responsible for:

- Purchase Order state transition;
- Procurement approval;
- Procurement lifecycle validation;
- Procurement business authorization.

The Procurement Finance integration is responsible for:

- registering the Finance commitment intent;
- communicating the approved Procurement business fact;
- recording integration-delivery state;
- determining whether a technical failure is retryable;
- preserving business-operation identity across attempts.

The Finance capability is responsible for:

- Finance-side processing;
- financial treatment;
- accounting decisions;
- Finance-owned persistence;
- Finance workflow.

The integration operation therefore communicates a Procurement business fact without making Finance processing part of the Procurement workflow.

---

## 25. Purchase Order Cancellation

Purchase Order cancellation is a separate Procurement lifecycle operation.

Cancellation shall not automatically reuse the original `procurement_commitment` integration operation.

If cancellation later requires financial communication, it shall be introduced as a separately approved integration operation with its own:

- business purpose;
- domain contract;
- provider operation;
- lifecycle semantics;
- idempotency identity;
- retry rules;
- Finance response semantics.

The Stage 5 Procurement Finance commitment mechanism shall not assume that:

```text
PO CANCELLED
```

automatically means:

```text
Reverse Finance Commitment
```

Any such reverse or cancellation communication requires a separately approved contract.

---

## 26. Changes After Purchase Order Approval

Changes to a Purchase Order after approval shall not automatically produce another Finance integration operation.

The existence of an approved Purchase Order does not establish a generic:

```text
PurchaseOrder.updated
```

Finance operation.

Only explicitly defined financially significant Procurement facts may result in future Finance communication.

Potential future examples include:

- approved amendment;
- approved value change;
- approved cancellation;
- approved reversal;
- other separately defined financial effect.

Each such operation shall have its own approved business identity and idempotency semantics.

Stage 5 applies specifically to the approved Procurement commitment operation and shall not be generalized to unspecified future Purchase Order changes.

---

## 27. Physical Receipt and Inventory Boundary

Physical receipt remains an Inventory concern.

The following distinction remains mandatory:

```text
Purchase Order Approved
        ≠
Physical Goods Received
        ≠
Inventory Stock Posted
        ≠
Finance Payment
```

Procurement owns the Purchase Order and Procurement transaction.

Inventory owns:

- physical stock;
- stock locations;
- stock balances;
- stock movements;
- stock transfers;
- physical receipt effects.

The Finance commitment integration shall not create or modify Inventory state.

Likewise, Inventory receipt processing shall not be treated as a second trigger for the Procurement `procurement_commitment` Finance operation.

The Finance commitment created from Purchase Order approval and the Inventory physical receipt process remain separate business concerns.

---

## 28. Expense Management Boundary

Expense Management remains separate from Procurement Purchase Order commitment processing.

The following are distinct:

```text
Purchase Order
        ≠
Expense Record
        ≠
Finance Transaction
```

A Purchase Order approval does not automatically create an Expense Management record.

Likewise, an Expense Management record does not automatically represent a Finance accounting transaction.

Expense Management remains responsible for its own:

- expense records;
- classifications;
- lifecycle;
- approval rules;
- expense business logic.

Any future communication between Expense Management and Finance shall require its own approved integration contract.

The Stage 5 Procurement Finance commitment mechanism shall not be reused as an Expense Management persistence mechanism.

---

## 29. Separation of Procurement, Inventory, Expense, and Finance Effects

The Phase 2.2 architecture shall preserve the following separation:

| Business concern | Authoritative owner | Example effect |
|---|---|---|
| Procurement commitment | Procurement | Purchase Order approved |
| Physical stock | Inventory | Stock movement posted |
| Expense record | Expense Management | Expense recorded/approved |
| Financial treatment | Finance | Accounting/financial processing |

No single module shall silently assume ownership of another module's business effect.

In particular:

- Procurement does not own physical stock;
- Inventory does not own Procurement approvals;
- Expense Management does not own Finance accounting;
- Finance does not own Procurement workflow;
- Finance does not own Inventory stock state.

The Procurement Finance commitment state introduced in Stage 5 belongs to Procurement because it records the delivery state of a Procurement-owned financial integration operation.

It does not represent the Finance financial effect itself.

---

## 30. Transaction Boundary

The Procurement transaction and Finance processing remain separate transactions.

The approved architecture is:

```text
Procurement Business Transaction
        │
        ├── Purchase Order approval
        │
        ├── Procurement Finance Commitment = PENDING
        │
        ▼
   TRANSACTION COMMIT
        │
        ▼
Post-Commit Integration Attempt
        │
        ▼
Enterprise Integration Framework
        │
        ▼
Finance Provider
        │
        ▼
Finance Transaction / Processing
```

The Procurement Finance commitment record is created as part of the Procurement transaction.

This ensures that the following local business facts are committed together:

- Purchase Order approval;
- Procurement Finance commitment intent.

The actual Finance delivery occurs only after the Procurement transaction commits.

This design prevents a failure between Procurement commit and Finance delivery from silently losing the intent to communicate the approved Procurement commitment.

The critical architectural sequence is therefore:

```text
PO APPROVED
+
Finance Commitment PENDING
        ↓
single Procurement transaction
        ↓
COMMIT
        ↓
Finance delivery
```

The Finance processing itself remains outside the Procurement transaction.

The architecture does not introduce:

- distributed transactions;
- two-phase commit;
- shared transaction managers;
- cross-module rollback;
- shared database transaction scope.

---

## 31. No Distributed Transactions

The Procurement ↔ Finance integration shall not use distributed transactions.

Specifically prohibited:

- two-phase commit;
- distributed database transactions;
- shared transaction managers between Procurement and Finance;
- cross-module rollback coordination;
- Finance participation in the Procurement database transaction;
- Procurement participation in a Finance database transaction;
- compensating Procurement database operations used solely to simulate transactional Finance rollback.

The intended failure model is:

```text
Procurement Commit
        ↓
Finance Integration Attempt
        ↓
Success / Failure
```

If Finance delivery fails:

- Procurement approval remains valid;
- Procurement commitment state remains durable;
- technical failure may become retryable;
- Finance processing remains separate.

This is an eventual integration model rather than a distributed transaction model.

---

## 32. Security and Authorization Boundary

The Procurement ↔ Finance integration shall reuse the enterprise security and authorization framework.

The approved execution boundary is:

```text
Enterprise Authorization
        ↓
Procurement Business Action
        ↓
Procurement Finance Commitment Registration
        ↓
Procurement Transaction Commit
        ↓
Post-Commit Integration
        ↓
IntegrationLifecycle
        ↓
Finance Provider
```

The integration shall not create a hidden authorization bypass.

The identity under which the Procurement action is performed shall remain available to the integration lifecycle where applicable.

Integration execution shall therefore preserve the enterprise governance model for:

- authenticated identity;
- authorization;
- subject identity;
- auditability;
- lifecycle observability.

Post-commit execution does not grant Procurement permission to bypass Finance authorization or Finance-owned governance.

---

## 33. Integration Audit

Procurement Finance integration activity shall use the enterprise Integration Audit mechanism.

The integration lifecycle shall provide audit records for relevant integration activity, including:

- provider;
- operation;
- integration request identity;
- Procurement business reference;
- subject where available;
- outcome;
- timestamp;
- failure information where applicable.

The audit lifecycle distinguishes:

```text
Integration Request
Integration Result
Integration Failure
```

A provider-declared unsuccessful result is recorded as an integration result with unsuccessful outcome.

A technical exception during integration execution is recorded through the integration failure lifecycle.

The Procurement Finance commitment state provides durable business-delivery state; it does not replace the enterprise integration audit.

Similarly, integration audit records are not Finance accounting records.

The following distinction shall remain explicit:

```text
Integration Audit
        ≠
Finance Accounting Record
```

---

## 34. Integration Lifecycle Events

Procurement Finance integration shall use the enterprise Integration Lifecycle event model.

The relevant lifecycle events are:

- integration request;
- integration result;
- integration failure.

The lifecycle event model provides integration observability and shall not be interpreted as an accounting event stream.

A successful integration result event indicates an integration outcome.

A provider-declared unsuccessful response produces an unsuccessful integration result.

A technical delivery exception produces an integration failure event.

The lifecycle events shall not:

- alter the Procurement Purchase Order state automatically;
- create Finance accounting entries;
- create Inventory stock movements;
- create Expense Management records;
- replace Finance-owned accounting events.

The Procurement Finance commitment state and integration lifecycle events serve different purposes:

```text
ProcurementFinanceCommitment
        =
Durable Procurement delivery state

Integration Lifecycle Event
        =
Integration observability event
```

---

## 35. Governance and Framework Reuse

The Procurement ↔ Finance integration shall reuse the enterprise governance capabilities already established in CDCS-EMP.

Required capabilities include:

- enterprise authorization;
- Procurement business authorization;
- transaction boundary;
- IntegrationLifecycle;
- integration audit;
- integration events;
- integration error handling;
- provider registration;
- integration observability;
- Procurement-owned commitment state.

No private governance framework shall be introduced for Procurement ↔ Finance communication.

The integration must remain inside the same architectural governance boundary as other enterprise integrations.

Stage 5 does not modify the generic enterprise Integration Framework.

The Procurement-specific commitment service owns only the Procurement business rules required to manage the lifecycle of the Finance commitment.

---

## 36. Integration Observability

The Procurement ↔ Finance integration shall maintain sufficient observability to distinguish:

1. Procurement business state;
2. Procurement integration-delivery state;
3. enterprise integration execution state;
4. Finance financial state.

At minimum, relevant observability shall allow the system to associate:

- Purchase Order reference;
- Procurement Finance commitment identity;
- provider;
- operation;
- enterprise integration request identity;
- idempotency key;
- integration outcome;
- retry state;
- failure category;
- subject where available;
- attempt timestamp.

The following identities shall remain distinct:

```text
Purchase Order Reference
        =
Procurement business identity

ProcurementFinanceCommitment.idempotency_key
        =
Business-operation identity

IntegrationRequest.request_id
        =
Individual integration-attempt identity

Finance-owned reference
        =
Finance-side identity
```

Observability shall not collapse these identities into a single identifier.

The integration-delivery state shall not be presented as if it were a Finance accounting state.

---

## 37. Integration Status Separation

Integration-delivery status shall remain separate from Procurement workflow status and Finance financial status.

The Purchase Order workflow remains responsible for Procurement states such as:

```text
DRAFT
SUBMITTED
APPROVED
REJECTED
CANCELLED
```

The Procurement Finance commitment shall maintain its own delivery state.

The approved Stage 5 state model is:

```text
PENDING
   │
   ├── successful Finance delivery ──────► COMMITTED
   │
   ├── provider-declared business
   │   rejection ────────────────────────► REJECTED
   │
   └── technical delivery failure ───────► RETRYABLE_FAILURE
                                               │
                                               │ successful retry
                                               ▼
                                           COMMITTED

RETRYABLE_FAILURE
        │
        └── technical retry failure ─────► RETRYABLE_FAILURE
```

### 37.1 PENDING

`PENDING` means:

> Procurement has durably recorded that the approved Purchase Order requires the Finance commitment operation, but successful Finance delivery has not yet been recorded locally.

`PENDING` is created within the same Procurement transaction as the Purchase Order approval.

### 37.2 COMMITTED

`COMMITTED` means:

> The Finance integration attempt returned a successful provider outcome and the Procurement commitment state has been updated accordingly.

`COMMITTED` is a terminal state for automatic retry.

### 37.3 RETRYABLE_FAILURE

`RETRYABLE_FAILURE` means:

> Finance delivery encountered a technical failure that may be retried without rerunning Procurement approval.

Retry eligibility is determined by the Procurement Finance commitment service.

The conceptual eligibility condition is:

```text
status == RETRYABLE_FAILURE
AND
next_retry_at <= current_time
```

### 37.4 REJECTED

`REJECTED` represents a provider-declared business rejection of the Finance commitment operation.

`REJECTED` is terminal for automatic retry under the Stage 5 architecture.

A provider-declared rejection shall not automatically change the Purchase Order state.

### 37.5 Status Separation Invariant

The following distinctions are mandatory:

```text
PurchaseOrder.status
        ≠
ProcurementFinanceCommitment.status
        ≠
Finance financial/accounting status
```

A Purchase Order may therefore remain:

```text
APPROVED
```

while its Procurement Finance commitment is:

```text
PENDING
```

or:

```text
RETRYABLE_FAILURE
```

without contradiction.

Likewise, a successful Procurement Finance commitment does not prescribe the resulting Finance accounting state.

The Procurement Finance commitment is a Procurement-owned integration-delivery state and shall not be treated as a Finance ledger, invoice, payment, settlement, or accounting record.

Stage 5 therefore **does introduce durable integration-status persistence**, but only within Procurement ownership and only for the approved Procurement Finance commitment operation. This does not contradict the prohibition on introducing Finance persistence solely for the integration.

---

## 38. No Automatic Compensation

Finance integration failure shall not automatically trigger a compensating Procurement transaction.

In particular, Finance integration failure shall not automatically:

- reject the Purchase Order;
- cancel the Purchase Order;
- reverse the Procurement approval;
- create a second Purchase Order;
- rerun Procurement approval;
- modify Procurement lifecycle state.

The approved failure model is:

```text
Procurement Approval
        ↓
Procurement Commit
        ↓
Finance Integration Attempt
        ↓
Success / Failure
```

Where delivery fails technically, the Procurement Finance commitment remains available for retry according to its durable state.

Any future business requirement for compensation, reversal, cancellation, or financial reversal shall require a separately approved business operation.

---

## 39. Reverse Communication Is a Separate Contract

Finance-to-Procurement communication is outside the initial Procurement Finance commitment operation.

If Finance later needs to communicate:

- financial rejection requiring Procurement action;
- payment status;
- settlement status;
- invoice status;
- financial reversal;
- other Finance-owned lifecycle events;

such communication shall use a separately approved integration contract.

The initial Procurement Finance commitment operation does not establish a generic reverse communication channel.

Finance communication shall therefore not implicitly create new Procurement workflow transitions.

---

## 40. Financial Effect Boundary

The Procurement Finance integration communicates the existence and context of an approved Procurement commitment.

The financial effect itself remains Finance-owned.

The boundary is:

```text
Procurement
    │
    │ Approved Procurement Commitment
    ▼
Enterprise Integration Boundary
    │
    ▼
Finance
    │
    │ Financial Treatment
    ▼
Finance-Owned Financial Effect
```

Procurement may communicate:

- Purchase Order identity;
- Purchase Request identity;
- supplier identity;
- Procurement dates;
- approval timestamp;
- currency;
- commercial value;
- Purchase Order lines;
- Procurement business-operation identity.

Finance determines:

- financial recognition;
- accounting classification;
- accounting treatment;
- financial transaction creation;
- ledger treatment;
- invoice treatment;
- payment treatment;
- settlement treatment.

The Procurement Finance commitment record is therefore an integration-delivery record rather than the financial effect itself.

---

## 41. Supplier Identity Boundary

Supplier identity communicated through Procurement remains a Procurement business reference.

Procurement may provide the supplier reference required to establish the context of the approved Purchase Order.

Finance remains responsible for determining how that supplier is represented and managed within Finance-owned persistence.

The Procurement Finance integration shall not establish a shared Supplier entity between Procurement and Finance.

No cross-module foreign key is required or permitted solely for supplier identity.

Where Finance maintains its own supplier identity, mapping between the two domains shall occur through the integration boundary.

---

## 42. Purchase Order Identity Boundary

The Purchase Order reference is a Procurement-owned business identity.

The Finance integration shall communicate the Purchase Order reference as business context.

Finance shall not become the owner of the Purchase Order.

Likewise, Procurement shall not treat a Finance-owned reference as a replacement for the Procurement Purchase Order identity.

The identities remain distinct:

```text
Procurement Purchase Order Reference
        ≠
Enterprise Integration Request ID
        ≠
Procurement Finance Idempotency Key
        ≠
Finance-Owned Reference
```

The Procurement Finance commitment shall preserve these distinctions.

---

## 43. Purchase Order Line Boundary

Purchase Order line information communicated to Finance remains Procurement-owned commercial information.

Procurement may communicate line-level information required to establish the financial context of the approved commitment, including:

- line reference;
- description;
- quantity;
- unit price;
- line amount;
- currency;
- relevant Procurement classification information.

Procurement shall not use Purchase Order line information to prescribe Finance accounting treatment.

Finance remains responsible for determining any Finance-side classification, recognition, or accounting treatment.

The Finance integration shall not create a Finance-owned copy of the Procurement Purchase Order merely to reproduce Procurement ownership.

---

## 44. Architectural Invariants

The following invariants are mandatory for the Procurement ↔ Finance architecture.

### 1. Procurement owns Purchase Orders and Procurement lifecycle.

### 2. Finance owns financial treatment and accounting.

### 3. Successful Purchase Order approval creates the Procurement business fact eligible for Finance communication.

### 4. Purchase Order approval is not equivalent to accounting recognition.

### 5. The enterprise Integration Framework is mandatory for Procurement ↔ Finance communication.

### 6. Procurement communicates Procurement facts, not accounting instructions.

### 7. Finance determines financial treatment.

### 8. Finance outcomes do not automatically change Procurement Purchase Order state.

### 9. Finance integration failure does not automatically reverse Procurement approval.

### 10. Retry preserves the same Procurement financial commitment business-operation identity.

### 11. Each integration attempt may have a new enterprise `request_id`.

### 12. The Procurement Finance idempotency key remains constant across retries.

### 13. The Procurement Finance commitment idempotency key is durably unique.

### 14. A Procurement Finance commitment is created within the same Procurement transaction as the approved Purchase Order transition.

### 15. Actual Finance delivery occurs only after the Procurement transaction commits.

### 16. `ProcurementFinanceCommitment` is Procurement-owned integration-delivery state, not Finance persistence.

### 17. Procurement shall not persist or directly mutate Finance-owned entities.

### 18. Finance shall not persist or directly mutate Procurement-owned entities.

### 19. No cross-module foreign keys shall be introduced between Procurement and Finance.

### 20. No distributed transaction shall be introduced.

### 21. Enterprise authorization, audit, lifecycle, events, and governance shall be reused.

### 22. Integration lifecycle records are not Finance accounting records.

### 23. Inventory remains authoritative for physical stock.

### 24. Finance implementation shall not be simulated inside Procurement.

### 25. Finance workflow remains separate from Procurement workflow.

### 26. `PurchaseOrder.status`, `ProcurementFinanceCommitment.status`, and Finance financial/accounting state shall remain separate.

### 27. `COMMITTED` and `REJECTED` are terminal states for automatic retry.

### 28. `RETRYABLE_FAILURE` is reserved for technical delivery failures eligible for retry.

### 29. Retry shall never rerun the Procurement Purchase Order approval.

### 30. Future cancellation, amendment, reversal, or other financially significant Procurement operations require separately approved integration contracts.

---

## 45. Explicitly Prohibited Architecture

The following architecture remains explicitly prohibited:

- private Procurement accounting ledger;
- private Procurement payment processor;
- private Procurement financial transaction engine;
- direct Finance repository access from Procurement;
- direct Finance database mutation from Procurement;
- direct Procurement repository access from Finance;
- direct Procurement database mutation from Finance;
- Purchase Order foreign key to Finance-owned financial records;
- Finance foreign key to Procurement Purchase Orders;
- automatic ledger posting implemented inside Procurement;
- automatic payment execution implemented inside Procurement;
- automatic supplier settlement implemented inside Procurement;
- Finance integration failure automatically rejecting or cancelling an approved Purchase Order;
- Finance state embedded inside the Purchase Order workflow;
- distributed transactions;
- two-phase commit;
- shared Finance/Procurement transaction managers;
- duplicated enterprise integration infrastructure;
- using `IntegrationRequest.request_id` as the Procurement business idempotency identity;
- creating a new idempotency key for each retry;
- treating Procurement integration-delivery state as Finance accounting state.

The Procurement Finance commitment mechanism does not violate these prohibitions because it is Procurement-owned state used to manage delivery of a Procurement-owned integration operation.

---

## 46. Deferred Decisions

The following decisions remain deferred to future Finance or separately approved integration work:

1. Finance entity model;
2. Finance financial transaction model;
3. General Ledger model;
4. journal model;
5. chart of accounts;
6. Finance invoice model;
7. Finance payment model;
8. Finance receipt model;
9. supplier settlement model;
10. Finance recognition rules;
11. Finance posting rules;
12. Finance workflow;
13. Finance UI;
14. Finance database schema;
15. additional Procurement → Finance operations;
16. Purchase Order cancellation communication;
17. Purchase Order amendment communication;
18. invoice-related integration operations;
19. Finance → Procurement reverse communication;
20. Finance reconciliation architecture;
21. Finance-specific reporting/read models;
22. future financial-effect operations not covered by the approved Procurement commitment contract.

The following decisions are **no longer deferred** because they were resolved through Stages 3–5:

- Finance provider identity: `finance`;
- Procurement Finance operation: `procurement_commitment`;
- domain payload: `ProcurementFinancialEffectRequest`;
- Procurement Finance idempotency key format:
  `procurement-commitment:<purchase_order.reference>`;
- distinction between `request_id` and business idempotency key;
- Procurement-owned durable commitment state;
- Stage 5 commitment state model;
- retry eligibility model;
- retry without rerunning Procurement approval.

---

## 47. Implementation Constraints

Implementation shall preserve the following constraints:

1. No Finance entities shall be introduced solely to simulate Finance functionality inside Procurement.

2. No General Ledger, accounting, payment, settlement, invoice, or Finance financial transaction persistence shall be implemented in Procurement unless separately approved.

3. The Procurement Finance commitment model shall remain Procurement-owned.

4. The commitment model shall contain only integration-delivery state required to support the approved Procurement Finance operation.

5. Finance delivery shall remain post-commit.

6. Retry shall reuse the same business-operation idempotency key.

7. Each retry may use a new enterprise integration `request_id`.

8. Duplicate commitment registration shall be prevented through durable uniqueness of the idempotency key.

9. The generic enterprise Integration Framework shall not be redesigned for Procurement-specific retry behavior.

10. Generic queue, worker, broker, or background-job infrastructure shall not be introduced solely for Stage 5.

11. The Procurement Finance integration shall not introduce cross-module database foreign keys.

12. The Procurement Finance integration shall not introduce distributed transaction coordination.

---

## 48. Implementation Sequence

The Procurement ↔ Finance integration has progressed through the following controlled stages.

### Stage 1 — Integration Contract Foundation — COMPLETED

Established:

- Finance provider boundary;
- Procurement Finance domain payload;
- operation contract;
- enterprise IntegrationRequest/Response/Result usage;
- Finance provider integration boundary.

### Stage 2 — Post-Commit Execution Capability — COMPLETED

Established:

- generic post-commit execution capability;
- transaction-safe separation between Procurement commit and integration delivery;
- post-commit failure isolation.

Implementation checkpoint:

```text
84a6628
feat(execution): add post-commit execution boundary
```

### Stage 3 — Procurement Approval Integration — COMPLETED

Established:

- Purchase Order approval as the Procurement Finance trigger;
- approval timestamp propagation;
- Procurement Finance integration adapter;
- Finance provider identity;
- `procurement_commitment` operation;
- `ProcurementFinancialEffectRequest`;
- deterministic Procurement Finance idempotency key;
- post-commit Finance integration wiring.

Implementation checkpoint:

```text
66a7cae
feat(procurement): integrate approved purchase orders with finance
```

### Stage 4 — Response and Failure Handling — COMPLETED

Established:

- `IntegrationLifecycle` usage;
- integration request/result/failure observability;
- integration audit;
- integration lifecycle events;
- provider-declared failure handling;
- technical delivery failure handling;
- post-commit failure isolation.

Implementation checkpoint:

```text
dfd96b8
feat(procurement): add integration response and failure handling
```

### Stage 5 — Retry and Idempotency — CURRENT

Architecture approved.

Stage 5 shall implement:

- Procurement-owned `ProcurementFinanceCommitment`;
- durable commitment registration;
- transactional `PENDING` intent;
- deterministic idempotency identity;
- duplicate registration prevention;
- attempt tracking;
- retry timing;
- retry eligibility;
- successful commitment state;
- provider-declared rejection state;
- technical retryable failure state;
- integration with the existing post-commit Finance delivery path.

Stage 5 implementation is pending.

### Stage 6 — Security, Audit, and Governance Verification

Future stage covering final verification that the complete Procurement Finance integration complies with:

- authorization;
- audit;
- lifecycle events;
- governance;
- identity propagation;
- module boundaries.

### Stage 7 — End-to-End Verification

Future stage covering complete Procurement → Finance integration verification, including:

- approval;
- commitment registration;
- transaction commit;
- post-commit delivery;
- response handling;
- failure handling;
- retry;
- idempotency;
- terminal states;
- regression.

---

## 49. Verification Requirements

The completed Procurement ↔ Finance integration shall verify at minimum:

1. Purchase Order approval remains Procurement-owned.

2. Finance integration occurs only after successful Procurement transaction commit.

3. Purchase Order approval is not altered by Finance integration failure.

4. Finance integration failure does not reject or cancel the approved Purchase Order.

5. A Procurement Finance commitment is created transactionally with the approved Purchase Order.

6. A `PENDING` commitment survives an application failure occurring after Procurement commit and before Finance delivery.

7. Duplicate commitment registration using the same idempotency key is prevented.

8. The idempotency key remains unchanged across retries.

9. Each integration retry may receive a new enterprise `request_id`.

10. Retry does not rerun Purchase Order approval.

11. Successful Finance delivery transitions the commitment to `COMMITTED`.

12. Technical delivery failure transitions the commitment to `RETRYABLE_FAILURE` where retry is permitted.

13. Provider-declared business rejection transitions the commitment to `REJECTED`.

14. `COMMITTED` and `REJECTED` are not automatically retried.

15. `RETRYABLE_FAILURE` becomes eligible for retry according to `next_retry_at`.

16. Retry uses the same Procurement business-operation identity.

17. Enterprise IntegrationLifecycle records request/result/failure events correctly.

18. Enterprise integration audit records are produced correctly.

19. Provider-declared failure and technical delivery failure remain distinguishable.

20. No Finance-owned repository is accessed directly by Procurement.

21. No Procurement-owned repository is accessed directly by Finance.

22. No cross-module Finance/Procurement foreign keys are introduced.

23. No distributed transaction is introduced.

24. Inventory ownership remains unchanged.

25. Expense Management ownership remains unchanged.

26. Finance accounting state remains Finance-owned.

27. Procurement Finance commitment state remains Procurement-owned.

28. Existing enterprise Integration Framework behavior remains regression-safe.

29. Existing Procurement Purchase Order approval behavior remains regression-safe.

30. Existing core execution and integration tests remain regression-safe.

---

## 50. Procurement ↔ Inventory Relationship

Procurement and Inventory remain separate bounded capabilities.

Procurement owns:

- suppliers;
- Purchase Requests;
- Purchase Orders;
- Procurement approvals;
- Procurement lifecycle;
- Procurement transactions.

Inventory owns:

- stock items;
- locations;
- stock balances;
- stock movements;
- transfers;
- physical receipt effects.

A Procurement Finance commitment does not create Inventory state.

Likewise, Inventory receipt processing does not create or modify the Procurement Finance commitment unless a separately approved integration contract requires such behavior.

The established distinction remains:

```text
Procurement Commitment
        ≠
Physical Inventory Receipt
```

---

## 51. Expense Management Relationship

Expense Management remains separate from both Procurement and Finance.

Expense Management owns:

- expense records;
- expense classifications;
- expense lifecycle;
- expense-specific business rules.

The Procurement Finance commitment shall not be reused as an Expense Management record.

Future Finance communication from Expense Management shall require a separately approved contract.

The distinction remains:

```text
Procurement Purchase Order
        ≠
Expense Record
        ≠
Finance Accounting Record
```

---

## 52. Reporting Relationship

Reporting remains a read-oriented consumer of business and integration information.

Reporting shall not become the owner of:

- Procurement Purchase Orders;
- Procurement Finance commitments;
- Finance accounting records;
- Inventory stock;
- Expense records.

Reporting may consume approved read models or reporting projections representing:

- Purchase Order status;
- Procurement Finance commitment status;
- integration outcomes;
- retry state;
- relevant Finance-owned information made available through approved reporting contracts.

Reporting shall not directly mutate Procurement or Finance operational state.

---

## 53. Architectural Decision Statement

CDCS-EMP Procurement shall communicate an approved Procurement commitment to future Finance through the existing enterprise Integration Framework.

The Procurement Purchase Order approval remains the authoritative Procurement business fact.

The Procurement Finance commitment shall be durably registered within the same Procurement transaction as the approved Purchase Order.

Actual Finance communication shall occur only after that Procurement transaction commits.

The Procurement Finance commitment shall preserve the business-operation identity of the approved Procurement commitment and shall support controlled retry without rerunning Procurement approval.

Finance remains responsible for:

- financial processing;
- financial treatment;
- accounting;
- ledger activity;
- invoices;
- payments;
- receipts;
- settlement.

Procurement remains responsible for:

- Purchase Orders;
- approvals;
- Procurement lifecycle;
- Procurement business facts;
- Procurement-owned integration-delivery state.

No direct cross-module persistence, shared financial ledger, distributed transaction, or duplicated Finance implementation shall be introduced.

Integration failure shall not automatically alter the already-approved Procurement Purchase Order.

---

## 54. Final Locked Architecture

The final locked Procurement ↔ Finance architecture is:

```text
                  PROCUREMENT
                       │
                       ▼
             Purchase Order APPROVED
                       │
                       ▼
        ProcurementFinanceCommitment
                   PENDING
                       │
                       ▼
             Procurement COMMIT
                       │
                       ▼
              Post-Commit Executor
                       │
                       ▼
       Procurement Finance Integration
                  Service/Adapter
                       │
                       ▼
             IntegrationLifecycle
                       │
                       ▼
             IntegrationService
                       │
                       ▼
          Finance Integration Provider
                       │
                       ▼
                    FINANCE
                       │
                       ▼
          Finance-owned processing
```

Technical delivery failure follows:

```text
Finance Delivery Failure
        │
        ▼
RETRYABLE_FAILURE
        │
        ▼
Retry Eligibility
        │
        ▼
New Integration Attempt
        │
        ├── same idempotency key
        └── new request_id
        │
        ▼
Finance Provider
```

Provider-declared business rejection follows:

```text
Finance Provider
        │
        ▼
IntegrationResponse(success=False)
        │
        ▼
REJECTED
```

Successful delivery follows:

```text
Finance Provider
        │
        ▼
Successful IntegrationResponse
        │
        ▼
COMMITTED
```

The complete architecture therefore separates:

```text
Procurement Business State
        ≠
Procurement Integration-Delivery State
        ≠
Enterprise Integration Attempt State
        ≠
Finance Financial State
```

The final architectural boundary remains:

```text
Procurement
   │
   │ Enterprise Integration Framework
   ▼
Finance
```

with no direct database ownership sharing and no distributed transaction.

---

## 55. Governance and Future Stages

Future implementation shall preserve the approved architecture and shall not introduce Finance functionality into Procurement merely to satisfy integration tests.

Subsequent stages shall focus on:

- implementation of the approved Stage 5 commitment/retry architecture;
- security verification;
- audit verification;
- governance verification;
- complete end-to-end integration verification.

Any material change to:

- ownership;
- transaction boundary;
- Finance provider contract;
- business-operation identity;
- idempotency model;
- retry semantics;
- cancellation communication;
- financial effect communication;

shall require an explicit architecture decision before implementation.

---

## 56. Approval Record

**Decision Status:** APPROVED / ACTIVE / LOCKED

**Architecture Scope:** Procurement ↔ Finance Integration

**Completed Implementation Stages:**

- Stage 1 — Integration Contract Foundation — COMPLETED
- Stage 2 — Post-Commit Execution Capability — COMPLETED
- Stage 3 — Procurement Approval Integration — COMPLETED
- Stage 4 — Response and Failure Handling — COMPLETED

**Current Stage:**

- Stage 5 — Retry and Idempotency — Architecture Approved / Implementation Pending

**Approved Stage 5 Architecture:**

- Procurement-owned durable Finance commitment state;
- transactional `PENDING` commitment registration;
- deterministic business-operation idempotency;
- unique idempotency key;
- same idempotency key across retries;
- new enterprise request identity per attempt;
- technical delivery failures eligible for retry;
- provider-declared business rejection represented separately;
- terminal `COMMITTED` and `REJECTED` states;
- no rerunning of Procurement approval during retry;
- no distributed transaction;
- no Finance-owned persistence introduced into Procurement.

The implementation shall remain subject to the controlled CDCS-EMP development workflow and verification requirements defined by the project.

---

## 57. Authoritative Architecture Document

This document remains the authoritative Procurement ↔ Finance integration architecture and contract for Phase 2.2.

Implementation changes affecting the Procurement ↔ Finance integration shall be reconciled against this document.

The authoritative document location is:

```text
docs/architecture/decisions/PHASE-2.2-PROCUREMENT-FINANCE-INTEGRATION-CONTRACT.md
```

No separate Stage 5 architecture document is required for retry and idempotency unless a future architecture decision explicitly establishes one.

This parent document remains the authoritative record for Stages 1–5 of the Procurement ↔ Finance integration.

---

## 58. Related Architecture Decisions

This decision shall be read together with the relevant CDCS-EMP architecture decisions governing:

- enterprise execution;
- authorization;
- integration framework;
- lifecycle events;
- audit;
- Procurement;
- Inventory;
- Expense Management;
- Reporting;
- Phase 2.2 Purchasing & Expense Management.

The parent Phase 2.2 Procurement ↔ Finance integration contract takes precedence for Procurement ↔ Finance-specific ownership, integration boundaries, transaction separation, response semantics, retry, and idempotency decisions.

Future Finance architecture decisions shall remain Finance-owned and shall not override Procurement ownership established by this contract without an explicit architecture reconciliation.

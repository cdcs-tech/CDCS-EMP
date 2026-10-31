# SSRC-IBMS Catering UAT — CATERING-UAT-IDEMP-001 Acceptance Checklist

**Document status:** APPROVED
**Scenario ID:** `CATERING-UAT-IDEMP-001`
**Environment:** `CDCS_EMP_UAT` on SQL Server `KASONGO`
**Primary verification target:** Inventory receipt idempotency
**Secondary verification targets:** End-to-end Catering workflow, revenue, and profitability

## 1. Purpose

This checklist defines the acceptance criteria for a new end-to-end Catering UAT scenario, beginning with Customer registration and continuing through Catering Request, Event, quotation, procurement, inventory receipt, operational consumption, revenue, and profitability.

The primary objective is to prove inventory receipt idempotency using persisted SQL Server evidence. The wider workflow is used to establish realistic business context and identify additional functional or documentation gaps.

Approval of this checklist does not mean any test has been executed or passed.

## 2. Test environment and isolation

- [ ] Confirm SQL Server is `KASONGO` and the database is `CDCS_EMP_UAT`.
- [ ] Record the scenario identifier and ensure every new test record is distinguishable from existing UAT data.
- [ ] Capture relevant baseline quantities, receipt counts, and existing identifiers.
- [ ] Confirm the workflow does not require resetting tables or modifying existing workshop records.

## 3. Customer and Catering workflow

- [ ] Register a new test customer and verify the saved record.
- [ ] Create a Catering Request and verify its initial status and customer relationship.
- [ ] Progress the request through the supported Event creation workflow.
- [ ] Create a quotation and verify its amount, requirements, and event relationship.
- [ ] Accept the quotation and complete the supported event confirmation steps.

## 4. Procurement and purchase order

- [ ] Create a Catering Purchase Requirement with a traceable link to the event.
- [ ] Verify the procurement handoff and generated purchase requirement reference.
- [ ] Progress the Purchase Request through the supported approval process.
- [ ] Create an approved PO with a known item, quantity, unit, unit price, and currency.
- [ ] Verify the approved PO line and remaining quantity before receipt.

## 5. Inventory receipt idempotency — primary acceptance gate

- [ ] Record the pre-test stock balance and existing receipt/movement counts.
- [ ] Post a new receipt using a unique idempotency key and capture the returned movement identifier.
- [ ] Retry the same receipt with the same key but deliberately conflicting valuation data.
- [ ] Verify the retry returns the original movement rather than creating another movement.
- [ ] Verify the original quantity, unit price, currency, valuation basis, and PO/line provenance remain unchanged.
- [ ] Read persisted records through a fresh SQLAlchemy session and verify exactly one idempotency record for the key.
- [ ] Verify stock increased only once and PO receiving totals reflect only the original receipt.
- [ ] Record transaction, constraint, and cleanup behavior without removing or rewriting historical movements.

## 6. Catering operations and consumption

- [ ] Progress the event through supported production and delivery steps.
- [ ] Verify the event's recorded operational status and delivery evidence.
- [ ] Record or identify valid consumed-cost records supported by the current workflow.
- [ ] Verify only eligible consumed costs contribute to the event's cost context.

## 7. Revenue and profitability

- [ ] Verify the available revenue workflow and the event's recognized revenue evidence.
- [ ] Verify revenue and costs refer to the same event and use consistent financial assumptions.
- [ ] Check whether the profitability view becomes available when its prerequisites are satisfied.
- [ ] Reconcile displayed revenue, eligible consumed costs, and resulting profitability where supported.
- [ ] Record any missing revenue, cost-recognition, or profitability functionality as a separate gap.

## 8. Evidence and closure

- [ ] Record expected and actual results at each checkpoint.
- [ ] Capture test keys, record identifiers, relevant statuses, and database verification results.
- [ ] Classify failures as defects, unsupported workflow steps, or documentation gaps.
- [ ] Confirm no unrelated UAT records or working-tree changes were altered.
- [ ] Prepare a concise UAT execution report and follow-up remediation list.

## 9. Acceptance rules

### Primary acceptance gate

Inventory receipt idempotency is proven only when the live SQL Server test confirms that:

1. The initial receipt creates one successfully posted stock movement.
2. A retry using the same idempotency key returns the original movement.
3. The retry does not overwrite the original valuation snapshot.
4. Exactly one idempotency record exists for the test key.
5. The stock balance reflects only one application of the receipt quantity.
6. The purchase order's receiving totals and status remain consistent with a single receipt.
7. Persisted results are verified through a fresh database session.

Sequential retry behavior and concurrent retry behavior are separate verification claims. Passing the sequential test does not, by itself, prove concurrent retry safety.

### Secondary workflow acceptance

The end-to-end workflow is evaluated against the supported functionality available in the current system. Unsupported steps, missing capabilities, and failures must be documented explicitly rather than marked as passed.

### Safety requirements

- Use new, clearly identifiable test records and a unique receipt key.
- Do not reuse existing receipt keys or modify existing workshop receipts.
- Verify the target database before any write operation.
- Do not use broad database reset or table-drop fixtures.
- Preserve historical stock movement and audit records.
- Perform cleanup only where it is supported and safe under the application's data-integrity rules.
- Preserve unrelated tracked and untracked working-tree changes.

## 10. Execution status

**Initial status:** NOT STARTED

This document defines the approved acceptance criteria. Test results, evidence, and final acceptance status must be recorded during execution in a separate scenario execution log.

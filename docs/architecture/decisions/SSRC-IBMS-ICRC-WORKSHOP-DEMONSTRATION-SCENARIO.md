# SSRC-IBMS ICRC Workshop Demonstration Scenario

**Document status:** Approved demonstration baseline
**Document type:** Supporting architecture decision and business-flow demonstration scenario
**Project:** CDCS-EMP — SSRC Integrated Business Management System (SSRC-IBMS)
**Host organisation:** South Sudan Red Cross (SSRC)
**Customer:** International Committee of the Red Cross (ICRC)
**Demonstration venue:** SSRC Juba premises
**Event dates:** 19–23 October 2026
**Participants:** 35
**Currency:** United States Dollar (USD)

---

## 1. Purpose

This document establishes the agreed scenario for demonstrating the SSRC-IBMS business flow using a five-day ICRC workshop hosted at the SSRC Juba premises.

It provides a consistent business scenario against which the team can verify the existing application screens, data-entry forms, business rules, permissions, and module hand-offs.

The scenario is a demonstration baseline. It does not establish that every business capability described below is already implemented in the application.

The actual browser walkthrough must distinguish between:

- Capabilities available and verified in the application.
- Capabilities available but not yet verified.
- Capabilities requiring configuration or further implementation.
- Business assumptions requiring confirmation before real operational use.

## 2. Scenario Overview

ICRC is conducting a five-day workshop at the SSRC Juba premises. SSRC provides the venue and the agreed workshop catering and related operational support.

The demonstration will follow the supported business flow from customer identification and catering request through event planning, quotation, requirements identification, purchasing where required, inventory effects where applicable, expense recording, and available financial reporting.

The demonstration must respect the ownership boundaries of each business module and must not treat a business request, procurement transaction, physical stock movement, expense, invoice, or payment as interchangeable records.

### 2.1 Scenario Details

| Field | Demonstration value |
|---|---|
| Customer | International Committee of the Red Cross (ICRC) |
| Host | South Sudan Red Cross (SSRC) |
| Venue | SSRC Juba premises |
| Event start date | 19 October 2026 |
| Event end date | 23 October 2026 |
| Duration | 5 calendar days, inclusive |
| Participants | 35 |
| Contact telephone | +211925511252 |
| Currency | USD |

The customer contact number is provided for this scenario and should be confirmed before the information is used operationally.

## 3. Catering and Venue Commercial Requirements

The following rates and quantities form the agreed demonstration inputs.

| Service or item | Quantity basis | Unit rate | Five-day illustrative amount |
|---|---|---:|---:|
| Hall hire | 1 hall × 5 days | $50 per day | $250.00 |
| Breakfast | 35 participants × 5 days | $5 per participant/day | $875.00 |
| Lunch | 35 participants × 5 days | $20 per participant/day | $3,500.00 |
| Water | 35 participants × 5 days × 4 bottles | $1 per bottle | $700.00 |
| Soda | 35 participants × 5 days × 2 bottles | $2 per bottle | $700.00 |
| **Illustrative quotation total** | | | **$6,025.00** |

### 3.1 Calculation Notes

**Hall hire**

5 days × $50 per day = **$250.00**

**Breakfast**

35 participants × 5 days × $5 = **$875.00**

**Lunch**

35 participants × 5 days × $20 = **$3,500.00**

**Water**

35 participants × 5 days × 4 bottles × $1 = **$700.00**

**Soda**

35 participants × 5 days × 2 bottles × $2 = **$700.00**

**Illustrative total**

$250 + $875 + $3,500 + $700 + $700 = **$6,025.00**

The calculation assumes that water and soda are charged separately from breakfast and lunch. This is a demonstration assumption, not confirmation of the actual ICRC commercial agreement.

The total excludes any unpriced services, taxes, discounts, additional requirements, or other charges not listed above.

## 4. Demonstration-Only Quotation Assumptions

The following terms are proposed solely to support the demonstration of quotation preparation and must not be represented as actual agreed ICRC contract terms.

| Term | Demonstration assumption |
|---|---|
| Quotation issue date | 11 October 2026 |
| Quotation validity | 7 calendar days |
| Illustrative validity end date | 18 October 2026 |
| Advance payment | 50% |
| Balance payment | 50% within 7 calendar days after the event |
| Illustrative advance | $3,012.50 |
| Illustrative balance | $3,012.50 |
| Illustrative quotation total | $6,025.00 |

The two illustrative payment portions are calculated as:

$6,025 × 50% = **$3,012.50** each.

These figures demonstrate a possible quotation configuration only. They do not prove that a quotation has been issued, accepted, invoiced, or paid.

If the application does not support a particular commercial term, the walkthrough must record that limitation rather than imply that the term was successfully configured.

## 5. Kitchen and Operational Requirements

The following quantities are provided as requirements for planning the workshop. They are not, by themselves, purchase orders, proof of stock availability, confirmed deliveries, or recorded expenses.

| Requirement | Quantity | Unit | Validation note |
|---|---:|---|---|
| Posho | 500 | kg | Confirm the quantity against the approved menu and expected consumption. |
| Beans | 200 | kg | Confirm against the final menu and portions. |
| Cooking oil | 50 | litres | Confirm expected consumption and available stock. |
| Onions | 3 | basins | Basin size and weight are unspecified; establish the standard unit before operational procurement. |
| Rice | 200 | kg | Confirm against the approved menu and expected consumption. |
| Sugar | 100 | kg | Confirm expected use for the workshop. |
| Meat | 50 | kg | Confirm type, menu allocation, and whether the quantity is additional to chicken. |
| Chicken | 50 | whole chickens, assumed | Confirm that “50 chickens” means 50 whole birds and establish expected size. |
| Vehicle fuel | 1,000 | litres | Confirm the requirement, purpose, vehicle allocation, authorisation, and calculation basis before any purchase. |
| Other approved requirements | To be determined | As applicable | Record only after the requirement is identified, justified, and approved. |

### 5.1 Requirement Validation

Before real operational use, the responsible staff should confirm:

1. Whether 500 kg of posho is correct for 35 participants over five days.
2. Whether 1,000 litres of fuel is justified and approved for the intended vehicle and operational activities.
3. The standard size or weight of an onion basin.
4. Whether the chicken quantity means whole chickens and what size is expected.
5. Whether meat and chicken are separate menu requirements.
6. Whether additional requirements have been approved and whether their costs are included in the quotation.

These checks must not be bypassed merely to make the demonstration appear complete.

## 6. Business Module Ownership and Boundaries

The demonstration must preserve the established SSRC-IBMS module responsibilities.

### 6.1 Catering

Catering owns the customer-facing and event-related business concepts, including:

- Customer.
- Catering Request.
- Catering Event.
- Quotation.
- Event Requirement.
- Catering Purchase Requirement.
- Catering production and delivery business processes.
- Catering-related financial context and costing support, to the extent implemented.

Catering requirements identify what the event needs. They do not automatically create procurement transactions, change stock balances, or recognise financial transactions.

### 6.2 Procurement

Procurement owns the purchasing process, including:

- Purchase Request.
- Sourcing and supplier-related activities.
- Purchase Order creation and approval.
- Procurement transaction progression.
- Receiving processes under the implemented procurement workflow.

A Catering Purchase Requirement is not a Purchase Request. A Purchase Request is not a Purchase Order. The demonstration must preserve these distinctions.

### 6.3 Inventory

Inventory owns physical stock records and stock effects, including:

- Stock items.
- Inventory locations.
- Stock balances.
- Stock movements.
- Stock transfers.
- Inventory effects arising from supported receiving or transfer workflows.

A requirement or approved purchase does not, by itself, establish that stock has been received or is available.

Stock balances must change only through the applicable authorised inventory workflow.

### 6.4 Expense Management

Expense Management owns expense recording, classification, and lifecycle management to the extent implemented.

A purchase order or inventory receipt must not automatically be treated as a fully recorded expense unless the applicable business rules explicitly establish that relationship.

### 6.5 Finance and Reporting

Finance is intended to support financial processing and integration as those capabilities become available. Reporting consumes supported records and read models.

The demonstration must not claim that the quotation total is recognised revenue or that the payment assumptions represent posted financial transactions.

Any revenue recognition, invoice, receipt, payment, commitment, or expense status must be verified against the actual application and its applicable rules.

## 7. Proposed Demonstration Sequence

The following sequence is the intended business walkthrough. Each step must be verified against the actual application before it is presented as an available capability.

| Stage | Business activity | Expected owner | Verification objective |
|---|---|---|---|
| 1 | Identify or create the ICRC customer | Catering | Verify customer fields, permissions, validation, and duplicate-handling rules. |
| 2 | Register the catering request | Catering | Verify the supported request fields and lifecycle. |
| 3 | Register or associate the workshop event | Catering | Verify dates, venue, participants, and request-to-event relationship. |
| 4 | Prepare the quotation | Catering | Verify available pricing fields, calculations, and quotation status handling. |
| 5 | Record event and catering requirements | Catering | Verify that kitchen and operational requirements can be represented accurately. |
| 6 | Identify requirements requiring external purchasing | Catering and Procurement | Verify the supported hand-off without confusing a requirement with a Purchase Request. |
| 7 | Demonstrate procurement, if supported | Procurement | Verify the actual Purchase Request, approval, Purchase Order, and receiving workflow. |
| 8 | Demonstrate physical stock effects, if applicable | Inventory | Verify receiving, stock movement, and balance changes using the authorised workflow. |
| 9 | Record eligible expenses, if supported | Expense Management | Verify expense classification and lifecycle without double-counting procurement or inventory records. |
| 10 | Review available financial information | Finance and Reporting | Verify which figures and statuses are genuinely supported by the application. |

This is a verification plan, not a claim that all stages have already been implemented.

If a stage is unavailable, the walkthrough should document the limitation and continue only through the supported paths. It must not manufacture records or statuses to simulate functionality that does not exist.

## 8. Financial Interpretation and Controls

The illustrative quotation total of **$6,025.00** is a calculated commercial scenario value.

It must not be interpreted automatically as:

- A quotation accepted by ICRC.
- An invoice issued to ICRC.
- Cash received.
- Revenue recognised in the accounts.
- A procurement commitment.
- An expense.
- Profit.

Actual profit cannot be determined from the information currently available. It requires the relevant eligible costs and revenue to be identified and calculated according to the implemented business and accounting rules.

The demonstration must also avoid double-counting costs. For example, a Purchase Order, receiving transaction, inventory movement, and expense may be related records representing different stages of a business process. They must not be added together as if each were a separate expense.

## 9. Demonstration Data and Change Control

The agreed scenario provides the business inputs for the demonstration. It does not authorise the creation of real operational records or the alteration of existing customer, procurement, inventory, or financial data.

Before entering records into the application:

1. Verify the actual screen and route for each stage.
2. Confirm required fields and supported relationships.
3. Confirm the correct permissions and user role.
4. Check whether ICRC or related demonstration records already exist.
5. Confirm whether the environment is suitable for demonstration data.
6. Distinguish demonstration-only assumptions from verified business facts.
7. Do not create invoices, payments, purchase orders, stock movements, or expenses unless the corresponding stage has been verified and its creation is authorised.

Any changes made during the demonstration should follow the project's normal testing, review, and change-control practices.

## 10. Assumptions and Open Questions

The following items remain subject to confirmation before the scenario can be used for real operational processing:

- Whether the water and soda charges are additional to the breakfast and lunch rates.
- Whether the proposed quotation date, validity period, and payment terms reflect an actual agreement.
- Whether the contact telephone number is current and authorised for use.
- Whether 500 kg of posho and 1,000 litres of vehicle fuel are correct.
- The standard weight or volume represented by one basin of onions.
- The intended size of the chickens and whether meat is a separate requirement.
- Whether additional approved workshop requirements must be priced.
- Which financial and reporting capabilities are implemented and available in the demonstration environment.

Until confirmed, these matters must remain explicitly identified as assumptions or open questions.

## 11. Acceptance Criteria for the Demonstration

The demonstration scenario is considered successfully demonstrated only when:

1. The customer and event information can be represented using supported application fields.
2. The request-to-event relationship, where implemented, is verified.
3. The quotation calculations are reproducible and the pricing assumptions are visible.
4. Catering requirements are distinguished from procurement transactions.
5. Procurement, receiving, inventory, and expense stages are demonstrated only where supported.
6. Permissions and validation behave as expected.
7. Financial figures are described according to their actual status and are not overstated.
8. Unsupported stages and unresolved assumptions are documented clearly.
9. No unintended or unauthorised operational records are created.
10. The walkthrough provides a reliable account of what the current application can and cannot do.

## 12. Document Status

This document establishes the agreed scenario baseline for the SSRC-IBMS ICRC workshop demonstration.

The scenario is intended to guide a controlled, evidence-based browser walkthrough of the current CDCS-EMP implementation. It does not supersede existing architecture decisions, module contracts, or implementation requirements.

Any subsequent changes to business assumptions should be recorded explicitly so the demonstration remains reproducible and the distinction between confirmed facts and demonstration-only assumptions is preserved.

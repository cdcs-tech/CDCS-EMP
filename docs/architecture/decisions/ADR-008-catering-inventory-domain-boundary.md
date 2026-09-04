
# ADR-008 — Catering Inventory Domain Boundary

* **Status:** Approved — Retrospective
* **Decision Date:** 4 September 2026
* **Documentation Date:** 5 September 2026
* **Decision Type:** Architectural
* **Phase:** Phase 2 — Business Modules
* **Module:** Catering
* **Scope:** Catering inventory domain ownership, stock lifecycle, stock-state management, and boundaries with adjacent business capabilities
* **Related ADRs:** ADR-001, ADR-002, ADR-003, ADR-005, ADR-007

---

## 1. Context

The Catering module requires an inventory capability to manage the organization's stock and inventory lifecycle.

The implemented inventory foundation introduces domain concepts for:

* stock items;
* inventory locations;
* stock balances;
* stock movements; and
* stock transfers.

The inventory capability must establish a clear business boundary so that stock ownership and stock-state management are not duplicated across other Catering capabilities.

The existing Catering Product remains the authoritative product master. Inventory does not create a second product registry or replace the Product domain.

Inventory is responsible for managing stock as an operational business capability. It must therefore distinguish between:

* the definition of a product;
* the configuration of an item for inventory management;
* where stock is held;
* the current stock state;
* the immutable history of stock changes; and
* the controlled movement of stock between locations.

The inventory boundary must also remain distinct from adjacent capabilities such as purchasing, expenses, income, invoicing, suppliers, sales, and broader Catering operations.

This ADR formalizes the inventory domain boundary established during the implementation of the Catering Inventory foundation.

---

## 2. Decision

Catering Inventory shall be a bounded business capability responsible for the management of stock and inventory state.

Inventory owns the operational stock lifecycle within the Catering module while consuming the existing Catering Product master and enterprise platform capabilities.

Inventory shall not become a generalized procurement, finance, sales, invoicing, or product-master subsystem.

The inventory boundary is defined by the following decisions.

### 2.1 Inventory owns stock management

Inventory owns the business concepts and operations required to manage stock, including:

* inventory-enabled stock items;
* inventory locations;
* current stock balances;
* stock movements;
* stock transfers;
* opening stock;
* receipts into stock;
* issues/consumption from stock;
* stock adjustments;
* transfer effects between locations;
* stock-level thresholds; and
* stock-state evaluation.

Inventory is authoritative for the operational quantity of stock represented by its balances and movement history.

---

### 2.2 Product remains the authoritative product master

Inventory shall reuse the existing Catering Product entity.

Inventory shall not create a parallel product or enterprise item master.

The relationship is:

```text
Catering Product
       │
       │ 0..1
       ▼
   Stock Item
```

A Product may therefore exist without being inventory-managed.

A StockItem identifies a Product that has been configured for inventory management.

Inventory-specific attributes such as minimum level and reorder level belong to StockItem rather than Product.

---

### 2.3 StockItem defines inventory participation

StockItem represents the inventory configuration of an existing Catering Product.

StockItem owns inventory-specific configuration and identity, including:

* product association;
* minimum stock level;
* reorder level;
* active/inactive state; and
* inventory participation.

StockItem shall not store the current quantity as an independent authoritative value.

Current quantity belongs to StockBalance.

A StockItem shall be associated with at most one Product and shall not duplicate Product master attributes unnecessarily.

---

### 2.4 Inventory locations are inventory-owned

Inventory owns the concept of a stock-holding location.

An InventoryLocation identifies where stock is held and provides inventory-specific attributes such as:

* unique location code;
* location name;
* description; and
* active state.

The initial inventory architecture uses a flat location model.

Location hierarchy, warehouse management, bin management, or advanced physical-location structures are not introduced unless a future business requirement establishes the need.

---

### 2.5 StockBalance represents current stock state

StockBalance is the authoritative persisted representation of current stock quantity for a StockItem at an InventoryLocation.

The conceptual key is:

```text
StockItem + InventoryLocation = StockBalance
```

A StockItem may therefore have separate balances at different locations.

The architecture requires a unique StockItem/Location combination.

A quantity of zero is valid and represents a known stock state.

Negative persisted stock balances are prohibited.

Current stock state shall not be inferred solely by repeatedly replaying the movement ledger during normal operational queries when a maintained balance is available.

---

### 2.6 StockMovement is the inventory ledger

StockMovement represents an inventory event/effect that changes stock quantity.

Supported movement types are:

* `OPENING_BALANCE`;
* `RECEIPT`;
* `ISSUE`;
* `ADJUSTMENT`; and
* `TRANSFER`.

Movement quantity is signed according to its stock effect.

The movement ledger provides an immutable business history of posted stock changes.

Posted movements shall not be destructively edited or deleted.

Corrections shall be represented through appropriate compensating or corrective movements rather than mutation of historical posted effects.

---

### 2.7 Movement posting changes stock state

A stock movement becomes authoritative only when posted.

Draft movements do not alter the authoritative current stock balance.

Posting a movement shall:

1. validate the stock item and location;
2. validate the movement type and quantity semantics;
3. determine the current stock balance;
4. calculate the resulting quantity;
5. reject operations that would produce an invalid negative balance;
6. create or update the StockBalance as appropriate;
7. create the posted StockMovement; and
8. complete the operation atomically within the established transaction boundary.

The inventory service owns this business orchestration in accordance with ADR-005.

---

### 2.8 Transfer is an inventory operation

StockTransfer represents the controlled movement of stock between two inventory locations.

A transfer shall have:

* a source location;
* a destination location;
* a stock item;
* a positive quantity;
* transfer status;
* optional reference/reason information; and
* relevant lifecycle timestamps.

Posting a transfer produces the corresponding stock effects at the source and destination locations.

Conceptually:

```text
Source Location
      │
      │ negative stock effect
      ▼
 Stock Balance
      │
      │ transfer
      ▼
Destination Location
      │
      │ positive stock effect
      ▼
 Stock Balance
```

Transfer posting and its associated stock effects shall be coordinated atomically.

Transfer is therefore an Inventory capability and shall not be implemented as an informal pair of unrelated manual movements.

---

### 2.9 Stock status is derived

Stock status shall be evaluated from current stock quantity and configured thresholds rather than persisted as an independent authoritative status field.

The relevant concepts include:

* current quantity;
* minimum level; and
* reorder level.

This avoids multiple authoritative representations of the same stock state.

Future status classifications may be introduced if justified by business requirements, but they shall remain derived from authoritative inventory state unless a separate architectural decision establishes otherwise.

---

### 2.10 Inventory owns stock lifecycle, not purchasing

Inventory may record stock receipts, but Inventory does not own purchasing transactions.

A stock receipt represents an inventory effect.

Purchasing, when introduced, shall own procurement concepts such as:

* suppliers;
* purchase requests;
* purchase orders;
* procurement approvals;
* purchasing commitments; and
* supplier-facing transactions.

A future Purchasing capability may integrate with Inventory to cause an inventory receipt, but Purchasing shall not be embedded into the Inventory domain.

The inventory boundary therefore remains:

```text
Purchasing
    │
    │ integration
    ▼
Inventory Receipt
```

rather than:

```text
Inventory
    └── Purchasing subsystem
```

---

### 2.11 Inventory does not own financial transactions

Inventory does not own:

* expenses;
* income;
* accounts payable;
* accounts receivable;
* invoices;
* receipts as financial documents;
* payments;
* general ledger transactions; or
* financial accounting rules.

Inventory may provide stock information required by future financial or operational capabilities, but those capabilities remain independently owned.

The physical/operational stock effect is distinct from any financial transaction that may accompany it.

---

### 2.12 Inventory does not own sales or catering operations

Inventory does not own broader Catering operational processes such as:

* customer sales;
* catering orders;
* menus;
* event operations;
* hall hire;
* customer invoicing;
* catering service delivery; or
* operational scheduling.

Such capabilities may consume inventory information or generate inventory effects through explicit interfaces.

They shall not be absorbed into the Inventory domain.

---

### 2.13 Inventory does not own supplier or party master data

Inventory does not establish a parallel supplier, customer, employee, organization, or general-party master.

Where supplier or other party information becomes necessary, Inventory shall integrate with the authoritative capability responsible for that information.

The inventory domain may store references required for inventory operations without becoming the owner of the corresponding master-data domain.

---

### 2.14 Cross-domain integration uses explicit interfaces

Inventory shall integrate with adjacent business capabilities through explicit interfaces or established enterprise integration mechanisms.

Inventory shall not directly absorb another business domain merely because an operational process crosses the boundary.

The architectural direction is:

```text
Adjacent Business Capability
            │
            │ explicit integration
            ▼
        Inventory
```

The reverse direction may also apply where Inventory publishes information required by another capability.

Cross-module dependencies shall remain explicit and controlled.

---

### 2.15 Enterprise platform capabilities remain outside Inventory ownership

Inventory shall consume existing CDCS-EMP platform capabilities for:

* application architecture;
* configuration;
* module discovery and lifecycle;
* data access;
* repositories;
* CRUD;
* validation;
* transactions;
* authentication;
* authorization;
* security;
* governance;
* audit;
* reporting;
* notifications; and
* other reusable enterprise services.

Inventory shall not introduce parallel enterprise infrastructure for these concerns.

---

## 3. Domain Ownership Summary

| Concern                               | Authoritative owner                     |
| ------------------------------------- | --------------------------------------- |
| Product definition                    | Catering Product                        |
| Inventory participation/configuration | StockItem                               |
| Stock-holding location                | Inventory                               |
| Current stock quantity                | StockBalance                            |
| Historical stock effects              | StockMovement                           |
| Stock movement between locations      | StockTransfer                           |
| Stock-level thresholds                | StockItem                               |
| Procurement                           | Future Purchasing capability            |
| Supplier master                       | Authoritative supplier/party capability |
| Expenses                              | Future Finance/Expenses capability      |
| Income                                | Future Finance/Income capability        |
| Invoicing                             | Future Invoicing capability             |
| Sales/customer operations             | Future Catering/Sales capability        |
| Authentication                        | Enterprise Security                     |
| Authorization                         | Enterprise Security                     |
| Audit                                 | Enterprise Governance/Audit             |
| Transactions                          | Enterprise Transaction Infrastructure   |

---

## 4. Dependency Direction

The Inventory domain shall depend on established enterprise infrastructure and the authoritative Catering Product domain where required.

Conceptually:

```text
Enterprise Platform
        ↑
        │
     Catering
        │
        ├── Product
        │
        └── Inventory
              │
              ├── StockItem
              ├── Location
              ├── Balance
              ├── Movement
              └── Transfer
```

Inventory shall not create reverse dependencies from enterprise platform infrastructure into Inventory.

Adjacent business modules shall integrate with Inventory through explicit contracts rather than direct ownership of Inventory state.

---

## 5. Business Invariants

The inventory boundary establishes the following principal invariants:

1. A StockItem references an authoritative Catering Product.
2. A StockItem does not independently represent a second product master.
3. A StockItem may have inventory balances at multiple locations.
4. A StockItem/Location combination has at most one current StockBalance.
5. Zero stock is valid.
6. Persisted negative stock balances are invalid.
7. StockMovement quantities are non-zero.
8. RECEIPT movements increase stock.
9. ISSUE movements decrease stock.
10. OPENING_BALANCE and ADJUSTMENT movements may represent signed stock effects.
11. TRANSFER effects are controlled by the transfer-posting operation.
12. Draft movements do not change authoritative stock balances.
13. Posted movements are immutable.
14. Transfer quantities are positive.
15. A transfer source and destination must represent distinct locations.
16. Transfer posting coordinates the resulting stock effects atomically.
17. Stock-level status is derived from current quantity and configured thresholds.
18. Stock state is not duplicated as independent authoritative data across adjacent domains.

These invariants are enforced through the appropriate combination of domain/service validation and database constraints.

---

## 6. Consequences

### Positive consequences

* Inventory has a clear and enforceable business boundary.
* Product remains the authoritative product master.
* Current stock state and historical stock effects have distinct responsibilities.
* Stock transfers are represented explicitly rather than as informal manual operations.
* Posted inventory history remains auditable and immutable.
* Purchasing and finance concerns remain decoupled from operational stock management.
* Future business modules can integrate with Inventory without taking ownership of its state.
* The architecture supports reuse of Inventory across future Catering processes.
* The domain avoids premature generalization into a universal enterprise inventory system.

### Trade-offs

* Some future workflows will require explicit integration between Inventory and other business modules.
* Inventory may need references to concepts owned elsewhere without owning those concepts.
* More complex cross-domain processes will require explicit contracts rather than direct database manipulation.
* Some business processes will initially remain outside the Inventory implementation until their own bounded capability is established.

These trade-offs are intentional and preserve clear business ownership.

---

## 7. Scope

This ADR covers the Catering Inventory domain boundary, including:

* StockItem;
* InventoryLocation;
* StockBalance;
* StockMovement;
* StockTransfer;
* opening stock;
* receipts;
* issues/consumption;
* adjustments;
* transfers;
* stock-level thresholds;
* current stock state;
* movement posting; and
* boundaries with adjacent Catering capabilities.

---

## 8. Explicit Exclusions

This ADR does not establish:

* a Purchasing module;
* a supplier-management module;
* an Expenses module;
* an Income module;
* an Invoicing module;
* a Sales module;
* a Customer/Party master;
* a warehouse-management system;
* advanced warehouse/bin hierarchy;
* accounting or general-ledger integration;
* automated procurement;
* demand forecasting;
* automated replenishment;
* batch/lot tracking;
* serial-number tracking;
* expiry management;
* barcode architecture;
* distributed inventory;
* cross-organization inventory;
* a generalized enterprise inventory framework; or
* a new enterprise data, transaction, security, or integration framework.

Such capabilities shall require their own business or architectural decisions where needed.

---

## 9. Relationship to Other ADRs

### ADR-001 — Phase 2 Business Module Architecture & Strategy

ADR-001 establishes the overall bounded business-module architecture. ADR-008 applies that principle to the Catering Inventory capability.

### ADR-002 — Catering Model Registration Boundary

ADR-002 establishes ownership of Catering Product and ProductCategory. ADR-008 explicitly preserves Product as the authoritative product master consumed by Inventory.

### ADR-003 — Catering Relationships & Database Constraints

ADR-003 establishes the Catering product relationships and persistence constraints that Inventory builds upon.

### ADR-005 — Catering Service Architecture

ADR-005 establishes service ownership of business rules, orchestration, and transaction coordination. Inventory posting and transfer operations follow this service boundary.

### ADR-007 — Catering Application Surface Architecture

ADR-007 establishes the application boundary through which Inventory functionality is exposed to authorized users. ADR-008 defines the business domain exposed through that surface.

---

## 10. Implementation Alignment

The Inventory domain is implemented within the Catering module under the established module boundary:

```text
app/modules/catering/models/
app/modules/catering/repositories/
app/modules/catering/services/
app/modules/catering/security/
app/modules/catering/routes/
app/modules/catering/forms/
```

The inventory-specific domain components include:

```text
StockItem
InventoryLocation
StockBalance
StockMovement
StockTransfer
```

The implementation reuses the established CDCS-EMP enterprise architecture for:

* ORM and model foundations;
* repositories;
* QueryOptions;
* services;
* validation;
* transactions;
* security;
* authorization;
* governance; and
* application integration.

This ADR documents the business-domain boundary represented by that implementation.

---

## 11. Decision Rationale

Inventory requires a distinct bounded capability because stock is a business state with its own lifecycle, operational rules, and historical record.

Separating Inventory from Product prevents duplication of product master data.

Separating Inventory from Purchasing and Finance prevents physical stock state from becoming entangled with procurement or accounting transactions.

Separating current balances from the movement ledger provides both efficient operational state and an immutable historical record.

Explicit transfer modeling provides a controlled and atomic mechanism for moving stock between locations.

The resulting architecture establishes Inventory as a focused operational stock capability that can later integrate with Purchasing, Expenses, Income, Invoicing, Sales, and other Catering capabilities without absorbing their responsibilities.

The architecture deliberately favors clear domain ownership, explicit integration, reuse of enterprise infrastructure, and incremental evolution over premature creation of a generalized enterprise inventory platform.

---

## 12. Status

**Approved — Retrospective**

This ADR formally records the Catering Inventory domain boundary established during implementation of the Inventory foundation.

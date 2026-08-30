# CDCS-EMP — Phase 2 Project Decision Record

## Phase 2.1.5.4 — Relationships & Database Constraints

**Status:** Approved / Complete
**Decision Date:** 30 August 2026
**Module:** Catering
**Phase:** Phase 2 — Business Modules

---

## 1. Decision

The Catering master-data foundation will use the existing
ProductCategory -> Product relationship as the authoritative
master-data relationship.

Product.category_id is a required foreign key referencing
ProductCategory.id.

No additional database migration is required for Phase 2.1.5.4 because
the required relationship and constraints were already materialized by
the Phase 2.1.5.3 migration and were verified against the live SQL Server
database.

---

## 2. Approved Relationship

The relationship is:

`	ext
ProductCategory
      ¦
      ¦ 1
      ¦
      ¦ *
      |>
    Product

The database relationship is:

products.category_id
        ¦
        +-- FOREIGN KEY ? product_categories.id

The SQLAlchemy ORM exposes the relationship bidirectionally:

Product.category
ProductCategory.products

using back_populates.

3. Database Constraints

The following constraints are authoritative:

ProductCategory
Primary key: id
Unique: code
Unique: guid
code: NOT NULL
Product
Primary key: id
Foreign key: category_id ? product_categories.id
Unique: code
Unique: guid
category_id: NOT NULL
code: NOT NULL

The guid uniqueness is inherited from the enterprise BaseModel
foundation.

4. Verification

The Catering model test suite provides focused verification for:

Bidirectional ORM relationships
Foreign-key target correctness
Required category_id
Product code uniqueness
Product-category code uniqueness
Primary-key inheritance
Relationship mapper targets
ORM unique-constraint materialization

Focused verification result:

12 passed

The live SQL Server database was also inspected at Alembic revision:

1419ef8d0e4d (head)

The database inspection confirmed:

Both Catering tables exist
Both tables have primary keys on id
Both code columns are uniquely constrained
Both guid columns are uniquely constrained
products.category_id has the required foreign key
products.category_id is NOT NULL
products.code is NOT NULL
product_categories.code is NOT NULL
5. Migration Decision

No new Alembic migration will be created for Phase 2.1.5.4.

The existing migration:

1419ef8d0e4d_add_catering_product_master_data.py

already materializes the required Product/ProductCategory relationship
and constraints.

Creating a second migration without a genuine schema change would
introduce unnecessary migration history and provide no architectural
benefit.

6. Architectural Boundary

The Catering module continues to consume the enterprise platform's
existing persistence foundation.

The master-data relationship remains entirely within the Catering
business domain:

Catering
+-- ProductCategory
+-- Product
    +-- category_id ? ProductCategory.id

No duplicate Organization, Tenant, or other platform identity model is
introduced.

Organization and tenant scoping remain responsibilities of the existing
CDCS-EMP platform architecture and are not duplicated inside these
master-data entities at this stage.

7. Completion

Phase 2.1.5.4 — Relationships & Database Constraints is hereby recorded
as complete.

The approved implementation is:

ORM relationship: complete
Foreign-key relationship: verified
Required nullability: verified
Primary keys: verified
Unique constraints: verified
Live SQL Server schema: verified
Focused test coverage: 12 passed
Additional migration: not required

This decision remains authoritative unless superseded by a subsequent
approved Architecture Decision Record.


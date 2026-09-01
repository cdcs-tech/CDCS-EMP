"""
Catering application-surface and verification tests.
"""

from app.core.platform.lifecycle import (
    ApplicationLifecycle,
)

from app.models.role_permission import (
    RolePermission,
)

from app.models.user_role import (
    UserRole,
)

from app.modules.catering import (
    CateringModule,
)

from app.modules.catering.security import (
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
)

from tests.factories.permission_factory import (
    PermissionFactory,
)

from tests.factories.role_factory import (
    RoleFactory,
)

from tests.utils.assertions import (
    assert_forbidden,
    assert_redirect,
    assert_success,
)


def test_authenticated_dashboard_renders(
    authenticated_client,
):
    """
    The established authenticated enterprise frontend must render
    successfully for an authorized administrator.
    """

    response = authenticated_client.get("/")

    assert_success(response)
    assert b"Executive Dashboard" in response.data
    assert (
        b"CDCS Enterprise Management Platform"
        in response.data
    )


def test_authenticated_navigation_contains_catering(
    authenticated_client,
):
    """
    Catering must appear in the enterprise navigation with
    a live application endpoint.
    """

    response = authenticated_client.get("/")

    assert_success(response)
    assert b"Catering" in response.data
    assert b'href="/catering/"' in response.data



def test_catering_route_is_registered(app):
    """
    The Catering blueprint must expose the module landing route
    through the enterprise application.
    """

    catering_rules = [
        rule
        for rule in app.url_map.iter_rules()
        if rule.rule == "/catering/"
        and rule.endpoint == "catering.index"
    ]

    assert len(catering_rules) == 1
    assert "GET" in catering_rules[0].methods


def test_catering_route_requires_authentication(
    client,
):
    """
    Anonymous users must not access the Catering landing page.
    """

    response = client.get("/catering/")

    assert_redirect(
        response,
        "/auth/login",
    )


def test_catering_route_denies_user_without_permission(
    client,
    regular_user,
):
    """
    An authenticated user without the Catering read permission
    must receive a forbidden response.
    """

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.get("/catering/")

    assert_forbidden(response)


def test_catering_route_allows_user_with_read_permission(
    client,
    session,
):
    """
    An authenticated user with the Catering product-category READ
    permission must be allowed to access the Catering landing page.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="catering_user",
        email="catering@test.local",
        first_name="Catering",
        last_name="User",
        password="Catering@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Catering Viewer",
        description="Catering read-only role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_READ.name,
        module="CATERING",
        description=(
            "View Catering product categories."
        ),
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Catering@123",
        },
        follow_redirects=True,
    )

    response = client.get("/catering/")

    assert_success(response)
    assert b"Catering" in response.data


def test_catering_module_remains_initialized(
    app,
):
    """
    Catering must remain registered through the enterprise
    application lifecycle.
    """

    lifecycle = ApplicationLifecycle.from_app(app)

    assert lifecycle.is_ready is True
    assert lifecycle.module_manager is not None

    module = lifecycle.module_manager.get_module(
        "CATERING"
    )

    assert isinstance(
        module,
        CateringModule,
    )

def test_product_category_list_requires_authentication(
    client,
):
    """
    Anonymous users must not access the Product Category list.
    """

    response = client.get(
        "/catering/categories/"
    )

    assert_redirect(
        response,
        "/auth/login",
    )


def test_product_category_list_denies_user_without_permission(
    client,
    regular_user,
):
    """
    Authenticated users without Product Category READ permission
    must receive a forbidden response.
    """

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/categories/"
    )

    assert_forbidden(response)


def test_product_category_list_allows_user_with_read_permission(
    client,
    session,
):
    """
    A user with Product Category READ permission can access
    the Product Category list.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="category_viewer",
        email="category.viewer@test.local",
        first_name="Category",
        last_name="Viewer",
        password="Category@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Category Viewer",
        description="Product Category read-only role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_READ.name,
        module="CATERING",
        description="View Catering product categories.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Category@123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/categories/"
    )

    assert_success(response)


def test_product_category_create_requires_create_permission(
    client,
    regular_user,
):
    """
    Authenticated users without Product Category CREATE permission
    must receive a forbidden response.
    """

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/categories/create"
    )

    assert_forbidden(response)


def test_product_category_create_allows_user_with_create_permission(
    client,
    session,
):
    """
    A user with Product Category CREATE permission can access
    the Product Category creation form.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="category_creator",
        email="category.creator@test.local",
        first_name="Category",
        last_name="Creator",
        password="Category@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Category Creator",
        description="Product Category creation role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_CREATE.name,
        module="CATERING",
        description="Create Catering product categories.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Category@123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/categories/create"
    )

    assert_success(response)

def test_product_category_create_persists_and_redirects(
    client,
    session,
):
    """
    A user with Product Category CREATE and READ permissions
    can create a Product Category and see it in the list.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="category_manager",
        email="category.manager@test.local",
        first_name="Category",
        last_name="Manager",
        password="Category@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Category Manager",
        description="Product Category create and read role",
        is_system=False,
        commit=False,
    )

    create_permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_CREATE.name,
        module="CATERING",
        description="Create Catering product categories.",
        commit=False,
    )

    read_permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_READ.name,
        module="CATERING",
        description="View Catering product categories.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=create_permission,
        )
    )

    session.add(
        RolePermission(
            role=role,
            permission=read_permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Category@123",
        },
        follow_redirects=True,
    )

    response = client.post(
        "/catering/categories/create",
        data={
            "name": "Beverages",
            "code": "BEV",
            "description": "Beverages and drinking water.",
        },
        follow_redirects=True,
    )

    assert_success(response)
    assert b"Product Categories" in response.data
    assert b"BEV" in response.data
    assert b"Beverages" in response.data
    assert b"Beverages and drinking water." in response.data
    assert b"Product category created successfully." in response.data

    category = (
        session.query(
            __import__(
                "app.modules.catering.models",
                fromlist=["ProductCategory"],
            ).ProductCategory
        )
        .filter_by(
            code="BEV"
        )
        .first()
    )

    assert category is not None
    assert category.name == "Beverages"
    assert category.description == (
        "Beverages and drinking water."
    )

def test_product_list_requires_authentication(
    client,
):
    """
    Anonymous users must not access the Product list.
    """

    response = client.get(
        "/catering/products/"
    )

    assert_redirect(
        response,
        "/auth/login",
    )


def test_product_list_denies_user_without_permission(
    client,
    regular_user,
):
    """
    Authenticated users without Product READ permission
    must receive a forbidden response.
    """

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/products/"
    )

    assert_forbidden(response)


def test_product_list_allows_user_with_read_permission(
    client,
    session,
):
    """
    A user with Product READ permission can access
    the Product list.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="product_viewer",
        email="product.viewer@test.local",
        first_name="Product",
        last_name="Viewer",
        password="Product@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Viewer",
        description="Product read-only role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_READ.name,
        module="CATERING",
        description="View Catering products.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Product@123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/products/"
    )

    assert_success(response)
    assert b"Products" in response.data


def test_product_create_requires_create_permission(
    client,
    regular_user,
):
    """
    Authenticated users without Product CREATE permission
    must receive a forbidden response.
    """

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/products/create"
    )

    assert_forbidden(response)


def test_product_create_allows_user_with_create_permission(
    client,
    session,
):
    """
    A user with Product CREATE permission can access
    the Product creation form.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="product_creator",
        email="product.creator@test.local",
        first_name="Product",
        last_name="Creator",
        password="Product@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Creator",
        description="Product creation role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CREATE.name,
        module="CATERING",
        description="Create Catering products.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Product@123",
        },
        follow_redirects=True,
    )

    response = client.get(
        "/catering/products/create"
    )

    assert_success(response)
    assert b"New Product" in response.data
    assert b"Category" in response.data
    assert b"Name" in response.data
    assert b"Code" in response.data
    assert b"Description" in response.data
    assert b"Unit" in response.data


def test_product_create_persists_and_redirects(
    client,
    session,
):
    """
    A user with Product CREATE and READ permissions
    can create a Product and see it in the list.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
        description="Beverages and drinking water.",
    )

    session.add(category)
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="product_manager",
        email="product.manager@test.local",
        first_name="Product",
        last_name="Manager",
        password="Product@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Manager",
        description="Product create and read role",
        is_system=False,
        commit=False,
    )

    create_permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CREATE.name,
        module="CATERING",
        description="Create Catering products.",
        commit=False,
    )

    read_permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_READ.name,
        module="CATERING",
        description="View Catering products.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=create_permission,
        )
    )

    session.add(
        RolePermission(
            role=role,
            permission=read_permission,
        )
    )

    session.add(
        UserRole(
            user=user,
            role=role,
        )
    )

    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": user.username,
            "password": "Product@123",
        },
        follow_redirects=True,
    )

    response = client.post(
        "/catering/products/create",
        data={
            "category_id": str(category.id),
            "name": "Bottled Water",
            "code": "WATER-500",
            "description": "500ml bottled drinking water.",
            "unit": "Bottle",
        },
        follow_redirects=True,
    )

    assert_success(response)
    assert b"Products" in response.data
    assert b"WATER-500" in response.data
    assert b"Bottled Water" in response.data
    assert b"Beverages" in response.data
    assert b"500ml bottled drinking water." in response.data
    assert b"Bottle" in response.data

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    product = (
        session.query(Product)
        .filter_by(
            code="WATER-500"
        )
        .first()
    )

    assert product is not None
    assert product.name == "Bottled Water"
    assert product.category_id == category.id
    assert product.description == (
        "500ml bottled drinking water."
    )
    assert product.unit == "Bottle"

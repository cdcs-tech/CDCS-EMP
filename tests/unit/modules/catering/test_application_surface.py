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
    CATERING_PRODUCT_CATEGORY_UPDATE,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
    CATERING_PRODUCT_UPDATE,
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

def _login_catering_read_user(
    client,
    session,
    *,
    username,
    email,
    password,
    permission,
):
    """
    Create and authenticate a user with the specified Catering READ
    permission for application-surface query tests.
    """

    UserFactory = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory

    user = UserFactory.create(
        session=session,
        username=username,
        email=email,
        first_name="Catering",
        last_name="Query Tester",
        password=password,
    )

    role = RoleFactory.create(
        session=session,
        name=f"{username} Role",
        description="Catering query test role",
        is_system=False,
        commit=False,
    )

    permission_record = PermissionFactory.create(
        session=session,
        name=permission.name,
        module="CATERING",
        description=f"{permission.name} query test permission.",
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission_record,
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
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )

    return user


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

def test_catering_landing_page_displays_management_navigation(
    client,
    session,
):
    """
    A user with Catering category and product READ permissions
    must see navigation to both management surfaces.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="catering_manager",
        email="catering-manager@test.local",
        first_name="Catering",
        last_name="Manager",
        password="Catering@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Catering Manager",
        description="Catering management role",
        is_system=False,
        commit=False,
    )

    category_permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_READ.name,
        module="CATERING",
        description="View Catering product categories.",
        commit=False,
    )

    product_permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_READ.name,
        module="CATERING",
        description="View Catering products.",
        commit=False,
    )

    session.add_all(
        [
            RolePermission(
                role=role,
                permission=category_permission,
            ),
            RolePermission(
                role=role,
                permission=product_permission,
            ),
            UserRole(
                user=user,
                role=role,
            ),
        ]
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
    assert b"Product Categories" in response.data
    assert b"Products" in response.data
    assert b"Manage Categories" in response.data
    assert b"Manage Products" in response.data
    assert b'href="/catering/categories/"' in response.data
    assert b'href="/catering/products/"' in response.data
    assert (
        b"Catering operations management is being prepared."
        not in response.data
    )


def test_catering_landing_page_hides_products_without_product_read_permission(
    client,
    session,
):
    """
    The Catering landing page must respect the existing Product
    READ permission when displaying Product navigation.
    """

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="catering_viewer",
        email="catering-viewer@test.local",
        first_name="Catering",
        last_name="Viewer",
        password="Catering@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Catering Category Viewer",
        description="Catering category read-only role",
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
            "password": "Catering@123",
        },
        follow_redirects=True,
    )

    response = client.get("/catering/")

    assert_success(response)
    assert b"Product Categories" in response.data
    assert b"Manage Categories" in response.data
    assert b'href="/catering/categories/"' in response.data
    assert b"Products" not in response.data
    assert b'href="/catering/products/"' not in response.data

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

def test_product_category_list_defaults_to_active_records(
    client,
    session,
):
    """
    The Product Category list must show active records by default
    and exclude inactive records.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    active_category = ProductCategory(
        name="Active Beverages",
        code="ACTIVE-BEV",
        description="Active category.",
        is_active=True,
    )

    inactive_category = ProductCategory(
        name="Archived Meals",
        code="ARCH-MEAL",
        description="Inactive category.",
        is_active=False,
    )

    session.add_all(
        [
            active_category,
            inactive_category,
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="category_default_query",
        email="category.default.query@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/"
    )

    assert_success(response)
    assert b"ACTIVE-BEV" in response.data
    assert b"Active Beverages" in response.data
    assert b"ARCH-MEAL" not in response.data
    assert b"Archived Meals" not in response.data


def test_product_category_list_search_filters_records(
    client,
    session,
):
    """
    Product Category search must return records matching the search
    term and exclude unrelated records.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    session.add_all(
        [
            ProductCategory(
                name="Cold Beverages",
                code="COLD-BEV",
                description="Drinks and refreshments.",
            ),
            ProductCategory(
                name="Dry Goods",
                code="DRY-GDS",
                description="Food storage items.",
            ),
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="category_search_query",
        email="category.search.query@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/?search=beverages"
    )

    assert_success(response)
    assert b"COLD-BEV" in response.data
    assert b"Cold Beverages" in response.data
    assert b"DRY-GDS" not in response.data
    assert b"Dry Goods" not in response.data


def test_product_category_list_status_all_includes_inactive_records(
    client,
    session,
):
    """
    Explicit status=all must include both active and inactive
    Product Category records.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    session.add_all(
        [
            ProductCategory(
                name="Active Catering",
                code="ACTIVE-CAT",
                is_active=True,
            ),
            ProductCategory(
                name="Inactive Catering",
                code="INACTIVE-CAT",
                is_active=False,
            ),
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="category_status_query",
        email="category.status.query@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/?status=all"
    )

    assert_success(response)
    assert b"ACTIVE-CAT" in response.data
    assert b"INACTIVE-CAT" in response.data


def test_product_category_list_supports_sorting(
    client,
    session,
):
    """
    Product Category sorting must change the ordering of returned
    records according to the controlled sort parameters.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    first = ProductCategory(
        name="Alpha Category",
        code="ALPHA",
    )

    second = ProductCategory(
        name="Zulu Category",
        code="ZULU",
    )

    session.add_all(
        [
            first,
            second,
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="category_sort_query",
        email="category.sort.query@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/?sort=name&direction=desc"
    )

    assert_success(response)

    zulu_position = response.data.index(
        b"Zulu Category"
    )
    alpha_position = response.data.index(
        b"Alpha Category"
    )

    assert zulu_position < alpha_position


def test_product_category_list_supports_pagination(
    client,
    session,
):
    """
    Product Category pagination must return only the requested page
    using a supported page size.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    categories = [
        ProductCategory(
            name=f"Category {index:02d}",
            code=f"CAT-{index:02d}",
        )
        for index in range(1, 12)
    ]

    session.add_all(categories)
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="category_pagination_query",
        email="category.pagination.query@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/?page=2&page_size=10&sort=name"
    )

    assert_success(response)

    assert b"Category 11" in response.data

    assert b"Category 01" not in response.data
    assert b"Category 02" not in response.data

def test_product_category_list_renders_query_controls(
    client,
    session,
):
    """
    The Product Category list must render the complete query-control
    surface defined by the 2.1.6.5.6A UX contract.
    """

    _login_catering_read_user(
        client,
        session,
        username="category_query_ui",
        email="category.query.ui@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/"
    )

    assert_success(response)

    assert b'id="category-search"' in response.data
    assert b'name="search"' in response.data

    assert b'id="category-status"' in response.data
    assert b'name="status"' in response.data
    assert b'value="active"' in response.data
    assert b'value="inactive"' in response.data
    assert b'value="all"' in response.data

    assert b'id="category-sort"' in response.data
    assert b'name="sort"' in response.data

    assert b'id="category-direction"' in response.data
    assert b'name="direction"' in response.data

    assert b'id="category-page-size"' in response.data
    assert b'name="page_size"' in response.data

    assert b'Apply' in response.data
    assert b'Clear' in response.data


def test_product_category_list_preserves_query_control_state(
    client,
    session,
):
    """
    The Product Category query controls must reflect the current
    request parameters when a filtered/sorted page is rendered.
    """

    _login_catering_read_user(
        client,
        session,
        username="category_query_state",
        email="category.query.state@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/"
        "?search=beverages"
        "&status=all"
        "&sort=code"
        "&direction=desc"
        "&page_size=50"
    )

    assert_success(response)

    assert b'value="beverages"' in response.data

    assert (
        b'<option value="all" selected>'
        in response.data
    )

    assert (
        b'<option value="code" selected>'
        in response.data
    )

    assert (
        b'<option value="desc" selected>'
        in response.data
    )

    assert (
        b'<option value="50" selected>'
        in response.data
    )


def test_product_category_list_pagination_preserves_query_parameters(
    client,
    session,
):
    """
    Category pagination links must preserve the active query state
    when navigating between pages.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    categories = [
        ProductCategory(
            name=f"Query Category {index:02d}",
            code=f"QUERY-{index:02d}",
        )
        for index in range(1, 12)
    ]

    session.add_all(categories)
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="category_query_pagination",
        email="category.query.pagination@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/"
        "?page=1"
        "&page_size=10"
        "&search=query"
        "&status=all"
        "&sort=code"
        "&direction=desc"
    )

    assert_success(response)

    assert b'/catering/categories/?' in response.data
    assert b'page=2' in response.data
    assert b'page_size=10' in response.data
    assert b'search=query' in response.data
    assert b'status=all' in response.data
    assert b'sort=code' in response.data
    assert b'direction=desc' in response.data


def test_product_category_list_renders_filtered_empty_state(
    client,
    session,
):
    """
    A valid query that returns no records must render the filtered
    empty-state message rather than the initial database empty state.
    """

    _login_catering_read_user(
        client,
        session,
        username="category_query_empty",
        email="category.query.empty@test.local",
        password="Category@123",
        permission=CATERING_PRODUCT_CATEGORY_READ,
    )

    response = client.get(
        "/catering/categories/?search=does-not-exist"
    )

    assert_success(response)

    assert (
        b"No product categories match the current query."
        in response.data
    )

    assert (
        b"No product categories have been created yet."
        not in response.data
    )

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

def test_product_list_search_filters_records(
    client,
    session,
):
    """
    Product search must return matching products and exclude
    unrelated products.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    session.add_all(
        [
            Product(
                category_id=category.id,
                name="Bottled Water",
                code="WATER-500",
                description="Drinking water.",
                unit="Bottle",
            ),
            Product(
                category_id=category.id,
                name="Rice",
                code="RICE-25",
                description="White rice.",
                unit="Bag",
            ),
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_search_query",
        email="product.search.query@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/?search=water"
    )

    assert_success(response)
    assert b"WATER-500" in response.data
    assert b"Bottled Water" in response.data
    assert b"RICE-25" not in response.data
    assert b"Rice" not in response.data


def test_product_list_category_filter(
    client,
    session,
):
    """
    Product category filtering must return only products belonging
    to the requested category.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    beverages = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    food = ProductCategory(
        name="Food",
        code="FOOD",
    )

    session.add_all(
        [
            beverages,
            food,
        ]
    )
    session.commit()

    session.add_all(
        [
            Product(
                category_id=beverages.id,
                name="Bottled Water",
                code="WATER",
                unit="Bottle",
            ),
            Product(
                category_id=food.id,
                name="Rice",
                code="RICE",
                unit="Bag",
            ),
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_category_query",
        email="product.category.query@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        f"/catering/products/?category_id={beverages.id}"
    )

    assert_success(response)
    assert b"WATER" in response.data
    assert b"Bottled Water" in response.data
    assert b"RICE" not in response.data
    assert b"Rice" not in response.data


def test_product_list_status_all_includes_inactive_records(
    client,
    session,
):
    """
    Explicit status=all must include both active and inactive
    Products.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    session.add_all(
        [
            Product(
                category_id=category.id,
                name="Active Water",
                code="ACTIVE-WATER",
                unit="Bottle",
                is_active=True,
            ),
            Product(
                category_id=category.id,
                name="Archived Juice",
                code="ARCH-JUICE",
                unit="Bottle",
                is_active=False,
            ),
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_status_query",
        email="product.status.query@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/?status=all"
    )

    assert_success(response)
    assert b"ACTIVE-WATER" in response.data
    assert b"ARCH-JUICE" in response.data


def test_product_list_supports_sorting(
    client,
    session,
):
    """
    Product sorting must order the returned records according to
    the controlled sort parameters.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    session.add_all(
        [
            Product(
                category_id=category.id,
                name="Alpha Product",
                code="ALPHA",
                unit="Bottle",
            ),
            Product(
                category_id=category.id,
                name="Zulu Product",
                code="ZULU",
                unit="Bottle",
            ),
        ]
    )
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_sort_query",
        email="product.sort.query@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/?sort=name&direction=desc"
    )

    assert_success(response)

    zulu_position = response.data.index(
        b"Zulu Product"
    )
    alpha_position = response.data.index(
        b"Alpha Product"
    )

    assert zulu_position < alpha_position


def test_product_list_supports_pagination(
    client,
    session,
):
    """
    Product pagination must return only the requested page
    using a supported page size.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    products = [
        Product(
            category_id=category.id,
            name=f"Product {index:02d}",
            code=f"PROD-{index:02d}",
            unit="Bottle",
        )
        for index in range(1, 12)
    ]

    session.add_all(products)
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_pagination_query",
        email="product.pagination.query@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/?page=2&page_size=10&sort=name"
    )

    assert_success(response)

    assert b"Product 11" in response.data

    assert b"Product 01" not in response.data
    assert b"Product 02" not in response.data

def test_product_list_renders_query_controls(
    client,
    session,
):
    """
    Product list must render all controls defined by the
    2.1.6.5.6A Query UI Contract.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    categories = [
        ProductCategory(
            name="Beverages",
            code="BEV",
        ),
        ProductCategory(
            name="Food",
            code="FOOD",
        ),
    ]

    session.add_all(categories)
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_query_ui_controls",
        email="product.query.ui.controls@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/"
    )

    assert_success(response)

    # Search control.
    assert b'id="product-search"' in response.data
    assert b'name="search"' in response.data

    # Category filter.
    assert b'id="product-category"' in response.data
    assert b'name="category_id"' in response.data
    assert b"All Categories" in response.data
    assert b"Beverages" in response.data
    assert b"Food" in response.data

    # Status filter.
    assert b'id="product-status"' in response.data
    assert b'name="status"' in response.data
    assert b'value="active"' in response.data
    assert b'value="inactive"' in response.data
    assert b'value="all"' in response.data

    # Sorting controls.
    assert b'id="product-sort"' in response.data
    assert b'name="sort"' in response.data
    assert b'id="product-direction"' in response.data
    assert b'name="direction"' in response.data

    # Page-size control.
    assert b'id="product-page-size"' in response.data
    assert b'name="page_size"' in response.data

    # Query actions.
    assert b"Apply" in response.data
    assert b"Clear" in response.data


def test_product_list_preserves_query_control_state(
    client,
    session,
):
    """
    Product query controls must preserve the submitted search,
    category, status, sorting, direction, and page-size values.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_query_ui_state",
        email="product.query.ui.state@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/"
        f"?search=water"
        f"&category_id={category.id}"
        "&status=all"
        "&sort=code"
        "&direction=desc"
        "&page_size=50"
    )

    assert_success(response)

    # Normalize HTML whitespace so the assertions verify the
    # rendered control state without depending on template formatting.
    html = b" ".join(response.data.split())

    assert b'value="water"' in html

    category_option_start = (
        f'<option value="{category.id}"'.encode()
    )

    category_option_index = html.find(
        category_option_start
    )

    assert category_option_index != -1

    category_option_end = html.find(
        b"</option>",
        category_option_index,
    )

    assert category_option_end != -1

    category_option = html[
        category_option_index:category_option_end
    ]

    assert b"selected" in category_option

    assert b'<option value="all" selected>' in html
    assert b'<option value="code" selected>' in html
    assert b'<option value="desc" selected>' in html
    assert b'<option value="50" selected>' in html


def test_product_list_pagination_preserves_query_parameters(
    client,
    session,
):
    """
    Product pagination links must preserve the active query state.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    products = [
        Product(
            category_id=category.id,
            name=f"Product {index:02d}",
            code=f"PROD-{index:02d}",
            unit="Bottle",
        )
        for index in range(1, 12)
    ]

    session.add_all(products)
    session.commit()

    _login_catering_read_user(
        client,
        session,
        username="product_query_ui_pagination",
        email="product.query.ui.pagination@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/"
        f"?page=1"
        f"&page_size=10"
        f"&search=Product"
        f"&category_id={category.id}"
        "&status=all"
        "&sort=code"
        "&direction=desc"
    )

    assert_success(response)

    assert b"/catering/products/?" in response.data
    assert b"page=2" in response.data
    assert b"page_size=10" in response.data
    assert b"search=Product" in response.data
    assert (
        f"category_id={category.id}".encode()
        in response.data
    )
    assert b"status=all" in response.data
    assert b"sort=code" in response.data
    assert b"direction=desc" in response.data


def test_product_list_renders_filtered_empty_state(
    client,
    session,
):
    """
    A valid Product query with no matching records must render
    the filtered empty state rather than the initial empty state.
    """

    _login_catering_read_user(
        client,
        session,
        username="product_query_ui_empty",
        email="product.query.ui.empty@test.local",
        password="Product@123",
        permission=CATERING_PRODUCT_READ,
    )

    response = client.get(
        "/catering/products/?search=does-not-exist"
    )

    assert_success(response)

    assert (
        b"No products match the current query."
        in response.data
    )

    assert (
        b"No products have been created yet."
        not in response.data
    )

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

def test_product_category_deactivate_changes_active_state(
    client,
    session,
):
    """
    A user with Product Category UPDATE permission can deactivate
    an active Product Category through the lifecycle endpoint.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
        description="Beverages and drinking water.",
        is_active=True,
    )

    session.add(category)
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="category_lifecycle_manager",
        email="category.lifecycle@test.local",
        first_name="Category",
        last_name="Lifecycle",
        password="Category@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Category Lifecycle Manager",
        description="Product Category lifecycle management role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_UPDATE.name,
        module="CATERING",
        description="Update Catering product categories.",
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

    response = client.post(
        f"/catering/categories/{category.id}/deactivate",
    )

    assert_redirect(
        response,
        "/catering/categories/",
        )

    session.refresh(category)

    assert category.is_active is False


def test_product_category_activate_changes_active_state(
    client,
    session,
):
    """
    A user with Product Category UPDATE permission can activate
    an inactive Product Category through the lifecycle endpoint.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
        description="Beverages and drinking water.",
        is_active=False,
    )

    session.add(category)
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="category_activation_manager",
        email="category.activation@test.local",
        first_name="Category",
        last_name="Activation",
        password="Category@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Category Activation Manager",
        description="Product Category activation role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_CATEGORY_UPDATE.name,
        module="CATERING",
        description="Update Catering product categories.",
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

    response = client.post(
        f"/catering/categories/{category.id}/activate",
    )

    assert_redirect(
        response,
        "/catering/categories/",
    )

    session.refresh(category)

    assert category.is_active is True


def test_product_deactivate_changes_active_state(
    client,
    session,
):
    """
    A user with Product UPDATE permission can deactivate
    an active Product through the lifecycle endpoint.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
        description="Beverages and drinking water.",
    )

    session.add(category)
    session.commit()

    product = Product(
        category_id=category.id,
        name="Bottled Water",
        code="WATER-500",
        description="500ml bottled drinking water.",
        unit="Bottle",
        is_active=True,
    )

    session.add(product)
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="product_lifecycle_manager",
        email="product.lifecycle@test.local",
        first_name="Product",
        last_name="Lifecycle",
        password="Product@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Lifecycle Manager",
        description="Product lifecycle management role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_UPDATE.name,
        module="CATERING",
        description="Update Catering products.",
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

    response = client.post(
        f"/catering/products/{product.id}/deactivate",
    )

    assert_redirect(
        response,
        "/catering/products/",
    )

    session.refresh(product)

    assert product.is_active is False


def test_product_activate_changes_active_state(
    client,
    session,
):
    """
    A user with Product UPDATE permission can activate
    an inactive Product through the lifecycle endpoint.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
        description="Beverages and drinking water.",
    )

    session.add(category)
    session.commit()

    product = Product(
        category_id=category.id,
        name="Bottled Water",
        code="WATER-500",
        description="500ml bottled drinking water.",
        unit="Bottle",
        is_active=False,
    )

    session.add(product)
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="product_activation_manager",
        email="product.activation@test.local",
        first_name="Product",
        last_name="Activation",
        password="Product@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Activation Manager",
        description="Product activation role",
        is_system=False,
        commit=False,
    )

    permission = PermissionFactory.create(
        session=session,
        name=CATERING_PRODUCT_UPDATE.name,
        module="CATERING",
        description="Update Catering products.",
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

    response = client.post(
        f"/catering/products/{product.id}/activate",
    )

    assert_redirect(
        response,
        "/catering/products/",
    )

    session.refresh(product)

    assert product.is_active is True


def test_category_lifecycle_routes_require_authentication(
    client,
    session,
):
    """
    Anonymous users must not access Product Category lifecycle
    endpoints.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    response = client.post(
        f"/catering/categories/{category.id}/deactivate",
    )

    assert_redirect(
        response,
        "/auth/login",
    )


def test_product_lifecycle_routes_require_authentication(
    client,
    session,
):
    """
    Anonymous users must not access Product lifecycle endpoints.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    product = Product(
        category_id=category.id,
        name="Bottled Water",
        code="WATER-500",
        unit="Bottle",
    )

    session.add(product)
    session.commit()

    response = client.post(
        f"/catering/products/{product.id}/deactivate",
    )

    assert_redirect(
        response,
        "/auth/login",
    )


def test_category_lifecycle_requires_update_permission(
    client,
    regular_user,
    session,
):
    """
    An authenticated user without Product Category UPDATE
    permission must receive a forbidden response.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.post(
        f"/catering/categories/{category.id}/deactivate",
    )

    assert_forbidden(response)

    session.refresh(category)

    assert category.is_active is True


def test_product_lifecycle_requires_update_permission(
    client,
    regular_user,
    session,
):
    """
    An authenticated user without Product UPDATE permission
    must receive a forbidden response.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    product = Product(
        category_id=category.id,
        name="Bottled Water",
        code="WATER-500",
        unit="Bottle",
    )

    session.add(product)
    session.commit()

    client.post(
        "/auth/login",
        data={
            "username": regular_user.username,
            "password": "Password123",
        },
        follow_redirects=True,
    )

    response = client.post(
        f"/catering/products/{product.id}/deactivate",
    )

    assert_forbidden(response)

    session.refresh(product)

    assert product.is_active is True


def test_category_lifecycle_routes_reject_get(
    authenticated_client,
    session,
):
    """
    Product Category lifecycle state changes must use POST and
    must not be exposed through GET requests.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    response = authenticated_client.get(
        f"/catering/categories/{category.id}/deactivate",
    )

    assert response.status_code == 405

    session.refresh(category)

    assert category.is_active is True


def test_product_lifecycle_routes_reject_get(
    authenticated_client,
    session,
):
    """
    Product lifecycle state changes must use POST and must not
    be exposed through GET requests.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    product = Product(
        category_id=category.id,
        name="Bottled Water",
        code="WATER-500",
        unit="Bottle",
    )

    session.add(product)
    session.commit()

    response = authenticated_client.get(
        f"/catering/products/{product.id}/deactivate",
    )

    assert response.status_code == 405

    session.refresh(product)

    assert product.is_active is True


def test_category_list_exposes_lifecycle_controls(
    client,
    session,
):
    """
    The Product Category management surface must expose the
    appropriate lifecycle controls for active and inactive records.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    active_category = ProductCategory(
        name="Beverages",
        code="BEV",
        is_active=True,
    )

    inactive_category = ProductCategory(
        name="Archived Meals",
        code="MEALS",
        is_active=False,
    )

    session.add_all(
        [
            active_category,
            inactive_category,
        ]
    )
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="category_lifecycle_viewer",
        email="category.lifecycle.viewer@test.local",
        first_name="Category",
        last_name="Lifecycle Viewer",
        password="Category@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Category Lifecycle Viewer",
        description="View Product Category lifecycle controls",
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
        "/catering/categories/?status=all"
    )

    assert_success(response)

    assert b"Deactivate" in response.data
    assert b"Activate" in response.data

    assert (
        f"/catering/categories/{active_category.id}/deactivate".encode()
        in response.data
    )

    assert (
        f"/catering/categories/{inactive_category.id}/activate".encode()
        in response.data
    )


def test_product_list_exposes_lifecycle_controls(
    client,
    session,
):
    """
    The Product management surface must expose the appropriate
    lifecycle controls for active and inactive records.
    """

    ProductCategory = __import__(
        "app.modules.catering.models",
        fromlist=["ProductCategory"],
    ).ProductCategory

    Product = __import__(
        "app.modules.catering.models",
        fromlist=["Product"],
    ).Product

    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    session.add(category)
    session.commit()

    active_product = Product(
        category_id=category.id,
        name="Bottled Water",
        code="WATER-500",
        unit="Bottle",
        is_active=True,
    )

    inactive_product = Product(
        category_id=category.id,
        name="Archived Juice",
        code="JUICE-OLD",
        unit="Bottle",
        is_active=False,
    )

    session.add_all(
        [
            active_product,
            inactive_product,
        ]
    )
    session.commit()

    user = __import__(
        "tests.factories.user_factory",
        fromlist=["UserFactory"],
    ).UserFactory.create(
        session=session,
        username="product_lifecycle_viewer",
        email="product.lifecycle.viewer@test.local",
        first_name="Product",
        last_name="Lifecycle Viewer",
        password="Product@123",
    )

    role = RoleFactory.create(
        session=session,
        name="Product Lifecycle Viewer",
        description="View Product lifecycle controls",
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
        "/catering/products/?status=all"
    )

    assert_success(response)

    assert b"Deactivate" in response.data
    assert b"Activate" in response.data

    assert (
        f"/catering/products/{active_product.id}/deactivate".encode()
        in response.data
    )

    assert (
        f"/catering/products/{inactive_product.id}/activate".encode()
        in response.data
    )

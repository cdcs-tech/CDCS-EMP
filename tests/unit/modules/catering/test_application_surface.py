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
    CATERING_PRODUCT_CATEGORY_READ,
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
    Catering must appear in the enterprise navigation while
    its dedicated application surface is being introduced.
    """

    response = authenticated_client.get("/")

    assert_success(response)
    assert b"Catering" in response.data
    assert b"Soon" in response.data


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

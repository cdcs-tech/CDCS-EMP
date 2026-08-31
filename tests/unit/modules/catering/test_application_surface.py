"""
Catering application-surface and verification baseline tests.
"""

from app.core.platform.lifecycle import (
    ApplicationLifecycle,
)
from app.modules.catering import (
    CateringModule,
)


def test_authenticated_dashboard_renders(authenticated_client):
    """
    The established authenticated enterprise frontend must render
    successfully for an authorized administrator.
    """

    response = authenticated_client.get("/")

    assert response.status_code == 200
    assert b"Executive Dashboard" in response.data
    assert b"CDCS Enterprise Management Platform" in response.data


def test_authenticated_navigation_contains_catering(
    authenticated_client,
):
    """
    Catering must appear in the enterprise navigation while
    remaining intentionally disabled until its frontend is implemented.
    """

    response = authenticated_client.get("/")

    assert response.status_code == 200
    assert b"Catering" in response.data
    assert b"Soon" in response.data


def test_catering_has_no_http_endpoint_in_current_baseline(app):
    """
    Catering must not expose an HTTP endpoint before its frontend
    blueprint is intentionally introduced.
    """

    catering_rules = [
        rule
        for rule in app.url_map.iter_rules()
        if rule.rule == "/catering"
        or rule.rule.startswith("/catering/")
        or (
            rule.endpoint
            and rule.endpoint.lower().startswith("catering.")
        )
    ]

    assert catering_rules == []


def test_catering_module_remains_initialized(app):
    """
    Catering must remain registered through the enterprise
    application lifecycle even though it has no HTTP surface yet.
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

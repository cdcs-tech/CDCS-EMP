"""
Reusable Test Assertions
"""


def assert_redirect(response, expected_location):
    """
    Verify redirect response.
    """

    assert response.status_code == 302
    assert expected_location in response.headers["Location"]


def assert_success(response):
    """
    Verify successful HTTP response.
    """

    assert response.status_code == 200


def assert_forbidden(response):
    """
    Verify forbidden response.
    """

    assert response.status_code == 403


def assert_unauthorized(response):
    """
    Verify unauthorized response.
    """

    assert response.status_code == 401

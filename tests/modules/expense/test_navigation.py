"""
Expense Management application navigation tests.
"""

from tests.utils.assertions import assert_success


def test_authenticated_navigation_contains_expense(
    authenticated_client,
):
    """
    Expense Management must appear in the enterprise navigation
    with its live application endpoint.
    """

    response = authenticated_client.get("/")

    assert_success(response)
    assert b"Expense Management" in response.data
    assert b'href="/expense/expenses/"' in response.data

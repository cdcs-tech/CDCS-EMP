"""
Authentication Test Helpers
"""


def login(
    client,
    username,
    password,
    follow_redirects=True,
):
    """
    Login helper.
    """

    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=follow_redirects,
    )


def logout(
    client,
    follow_redirects=True,
):
    """
    Logout helper.
    """

    return client.get(
        "/auth/logout",
        follow_redirects=follow_redirects,
    )

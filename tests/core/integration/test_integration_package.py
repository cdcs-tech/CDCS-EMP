"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Package foundation tests.
"""

import importlib


def test_integration_package_imports():
    """
    Verify that the enterprise integration
    package can be imported successfully.
    """

    module = importlib.import_module(
        "app.core.integration"
    )

    assert module is not None


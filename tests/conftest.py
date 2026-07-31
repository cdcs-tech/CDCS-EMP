"""
CDCS Enterprise Management Platform (CDCS-EMP)

Pytest Configuration
"""

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(scope="function")
def app():

    app = create_app("testing")

    with app.app_context():

        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):

    return app.test_client()

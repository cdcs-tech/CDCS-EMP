from app.extensions import db
from app.models import User


def seed_admin():

    admin = User.query.filter_by(

        email="admin@cdcs.local"

    ).first()

    if admin:

        return

    admin = User(

        username="admin",

        email="admin@cdcs.local",

        first_name="System",

        last_name="Administrator",

        is_active=True,

    )

    admin.set_password("Admin@123")

    db.session.add(admin)

    db.session.commit()

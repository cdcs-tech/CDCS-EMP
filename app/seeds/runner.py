"""
CDCS Enterprise Management Platform (CDCS-EMP)

Production Seed Runner
"""


from app import create_app

from .seed import SeedManager



def run():

    app = create_app()


    with app.app_context():

        print()

        print("=" * 60)

        print(
            "CDCS-EMP Database Seeder"
        )

        print("=" * 60)


        results = SeedManager().run()


        print()

        print("=" * 60)

        print(
            "Seed Summary"
        )

        print("=" * 60)



        for name, result in results.items():

            print()

            print(name)

            print(
                f"Created : {result['created']}"
            )

            print(
                f"Skipped : {result['skipped']}"
            )



        print()

        print("=" * 60)

        print(
            "Database seeding completed successfully."
        )

        print("=" * 60)

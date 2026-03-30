from src import create_app
from src.extensions import db
from src.models import User, Role

app = create_app()

with app.app_context():
    if not User.find_one("admin@digimarket.com"):
        admin = User(
            email="admin@digimarket.com",
            nom="Admin",
            role=Role.ADMIN
        )
        admin.set_password("admin1234")
        db.session.add(admin)
        db.session.commit()
        print("Admin créé avec succès.")
    else:
        print("Un admin existe déjà avec cet email.")

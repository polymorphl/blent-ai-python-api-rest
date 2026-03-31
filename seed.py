from src import create_app
from src.extensions import db
from src.models import User, Role, Product, Order, OrderLine, OrderStatus

app = create_app()

with app.app_context():
    # --- Admin ---
    if not User.find_one("admin@digimarket.com"):
        admin = User(email="admin@digimarket.com",
                     nom="Admin", role=Role.ADMIN)
        admin.set_password("admin1234")
        db.session.add(admin)
        db.session.commit()
        print("Admin créé : admin@digimarket.com / admin1234")
    else:
        print("Admin déjà présent.")

    # --- Client de test ---
    client_user = User.find_one("client@digimarket.com")
    if not client_user:
        client_user = User(
            email="client@digimarket.com",
            nom="Client Test",
            role=Role.CLIENT
        )
        client_user.set_password("client1234")
        db.session.add(client_user)
        db.session.commit()
        print("Client créé : client@digimarket.com / client1234")
    else:
        print("Client de test déjà présent.")

    # --- Produits ---
    if Product.query.count() == 0:
        produits = [
            Product(
                nom="Clavier mécanique Cherry MX",
                description="Clavier gaming mécanique - switches Cherry MX Red",  # noqa: E501
                categorie="Périphériques",
                prix=89.99,
                quantite_stock=15,
            ),
            Product(
                nom="Souris gaming Logitech G502",
                description="Souris filaire haute précision 25 600 DPI",
                categorie="Périphériques",
                prix=59.99,
                quantite_stock=20,
            ),
            Product(
                nom="SSD Samsung 1 To",
                description="Disque SSD NVMe M.2",
                categorie="Stockage",
                prix=129.99,
                quantite_stock=10,
            ),
            Product(
                nom="RAM DDR5 32 Go",
                description="Kit mémoire vive DDR5 32 Go (2x16 Go) 5600 MHz.",
                categorie="Mémoire",
                prix=149.99,
                quantite_stock=8,
            ),
            Product(
                nom="Écran 27 pouces 4K",
                description="Moniteur IPS 27 pouces résolution 3840x2160",
                categorie="Écrans",
                prix=349.99,
                quantite_stock=5,
            ),
            Product(
                nom="Carte graphique RTX 4060",
                description="GPU NVIDIA RTX 4060 8 Go GDDR6",
                categorie="Composants",
                prix=399.99,
                quantite_stock=3,
            ),
        ]
        db.session.add_all(produits)
        db.session.commit()
        print(f"{len(produits)} produits créés.")
    else:
        produits = Product.query.all()
        print("Produits déjà présents.")

    # --- Commande de test ---
    if Order.query.filter_by(utilisateur_id=client_user.id).count() == 0:
        order = Order(
            utilisateur_id=client_user.id,
            adresse_livraison="42 avenue de la Technologie, 75001 Paris",
            statut=OrderStatus.VALIDEE,
        )
        db.session.add(order)
        db.session.flush()

        # Ligne 1 : clavier
        clavier = Product.query.filter_by(
            nom="Clavier mécanique Cherry MX").first()
        # Ligne 2 : SSD
        ssd = Product.query.filter_by(nom="SSD Samsung 1 To").first()

        db.session.add(OrderLine(
            commande_id=order.id,
            produit_id=clavier.id,
            quantite=1,
            prix_unitaire=clavier.prix,
        ))
        clavier.quantite_stock -= 1

        db.session.add(OrderLine(
            commande_id=order.id,
            produit_id=ssd.id,
            quantite=2,
            prix_unitaire=ssd.prix,
        ))
        ssd.quantite_stock -= 2

        db.session.commit()
        print("Commande de test créée pour le client.")
    else:
        print("Commande de test déjà présente.")

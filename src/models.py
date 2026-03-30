from datetime import datetime, timezone
from typing import Optional
from .extensions import db, bcrypt
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum


class Role(PyEnum):
    CLIENT = 'client'
    ADMIN = 'admin'


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    mot_de_passe = db.Column(db.String, nullable=False)
    nom = db.Column(db.String, nullable=False)
    role = db.Column(SAEnum(Role), default=Role.CLIENT, nullable=False)
    date_creation = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def set_password(self, password: str) -> None:
        self.mot_de_passe = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.mot_de_passe, password)

    @classmethod
    def find_one(cls, email: str) -> Optional['User']:
        return cls.query.filter_by(email=email).first()


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    categorie = db.Column(db.String, nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, nullable=False, default=0)
    date_creation = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class OrderStatus(PyEnum):
    EN_ATTENTE = 'en_attente'
    VALIDEE = 'validée'
    EXPEDIEE = 'expédiée'
    ANNULEE = 'annulée'


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey('users.id'),
        nullable=False
    )
    date_commande = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    adresse_livraison = db.Column(db.String, nullable=False)
    statut = db.Column(
        SAEnum(OrderStatus),
        default=OrderStatus.EN_ATTENTE, nullable=False
    )

    user = db.relationship('User', backref='orders')
    lines = db.relationship(
        'OrderLine',
        backref='order',
        cascade='all, delete-orphan'
    )


class OrderLine(db.Model):
    __tablename__ = "order_lines"

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(
        db.Integer, db.ForeignKey('orders.id'),
        nullable=False
    )
    produit_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id'),
        nullable=False
    )
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)

    produit = db.relationship('Product')

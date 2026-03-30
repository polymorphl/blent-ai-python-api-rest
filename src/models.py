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


class Product:
    pass


class Order:
    pass


class OrderLine:
    pass

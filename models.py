from dataclasses import dataclass
from datetime import date


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    price: float
    quantity: int

    def to_dict(self):
        return {
            "id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
        }


@dataclass
class CartItem:
    product_id: int
    name: str
    price: float
    quantity: int

    @property
    def total(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            "id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "total": self.total,
        }


@dataclass
class SaleLine:
    product_id: int
    product_name: str
    quantity: int
    amount: float
    sale_date: str = date.today().isoformat()

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "amount": self.amount,
            "date": self.sale_date,
        }


@dataclass
class User:
    username: str
    password: str
    role: str

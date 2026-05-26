import csv
from datetime import date, datetime
from pathlib import Path

from .linked_list import LinkedList
from .models import CartItem, Product, SaleLine, User


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECEIPT_DIR = BASE_DIR / "receipts"


class VendoraStore:
    def __init__(self):
        self.products = LinkedList()
        self.cart = LinkedList()
        self.sales = LinkedList()
        self.users = LinkedList()
        self.low_stock_threshold = 10
        DATA_DIR.mkdir(exist_ok=True)
        RECEIPT_DIR.mkdir(exist_ok=True)

    def load_all(self):
        self.load_products()
        self.load_sales()
        self.load_users()
        self.seed_if_empty()

    def seed_if_empty(self):
        if len(self.products) == 0:
            for product in [
                Product(1001, "Golden Penny Spaghetti", "Groceries", 950, 42),
                Product(1002, "Peak Milk Tin", "Dairy", 850, 28),
                Product(1003, "Eva Water 75cl", "Beverages", 250, 80),
                Product(1004, "Indomie Chicken Pack", "Groceries", 220, 96),
                Product(1005, "Molfix Diapers Small", "Baby Care", 4500, 7),
                Product(1006, "Dettol Antiseptic 500ml", "Health", 3100, 14),
                Product(1007, "Nivea Body Lotion", "Beauty", 3900, 9),
                Product(1008, "Sunlight Detergent 900g", "Household", 1800, 23),
            ]:
                self.products.append(product)
            self.save_products()

        if len(self.users) == 0:
            self.users.append(User("admin", "admin123", "Admin"))
            self.users.append(User("cashier", "cashier123", "Cashier"))
            self.save_users()

    def load_products(self):
        self.products.clear()
        path = DATA_DIR / "products.csv"
        if not path.exists():
            return
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                self.products.append(Product(
                    int(row["id"]),
                    row["name"],
                    row["category"],
                    float(row["price"]),
                    int(row["quantity"]),
                ))

    def save_products(self):
        with (DATA_DIR / "products.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "category", "price", "quantity"])
            for product in self.products:
                writer.writerow([product.product_id, product.name, product.category, product.price, product.quantity])

    def load_sales(self):
        self.sales.clear()
        path = DATA_DIR / "sales.csv"
        if not path.exists():
            return
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                self.sales.append(SaleLine(
                    int(row["product_id"]),
                    row["product_name"],
                    int(row["quantity"]),
                    float(row["amount"]),
                    row["date"],
                ))

    def save_sales(self):
        with (DATA_DIR / "sales.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["product_id", "product_name", "quantity", "amount", "date"])
            for sale in self.sales:
                writer.writerow([sale.product_id, sale.product_name, sale.quantity, sale.amount, sale.sale_date])

    def load_users(self):
        self.users.clear()
        path = DATA_DIR / "users.csv"
        if not path.exists():
            return
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                self.users.append(User(row["username"], row["password"], row["role"]))

    def save_users(self):
        with (DATA_DIR / "users.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password", "role"])
            for user in self.users:
                writer.writerow([user.username, user.password, user.role])

    def authenticate(self, username, password):
        return self.users.find(lambda user: user.username == username and user.password == password)

    def product_list(self, query=""):
        query = query.lower().strip()
        products = self.products.to_list()
        if query:
            products = [
                product for product in products
                if query in product.name.lower() or query in product.category.lower()
            ]
        return products

    def find_product(self, product_id):
        return self.products.find(lambda product: product.product_id == product_id)

    def add_product(self, name, category, price, quantity):
        next_id = max([product.product_id for product in self.products] or [1000]) + 1
        product = Product(next_id, name, category, float(price), int(quantity))
        self.products.append(product)
        self.save_products()
        return product

    def add_to_cart(self, product_id, quantity=1):
        product = self.find_product(product_id)
        if product is None or product.quantity < quantity:
            return False
        product.quantity -= quantity
        existing = self.cart.find(lambda item: item.product_id == product_id)
        if existing:
            existing.quantity += quantity
        else:
            self.cart.append(CartItem(product.product_id, product.name, product.price, quantity))
        self.save_products()
        return True

    def remove_from_cart(self, product_id):
        item = self.cart.remove_if(lambda cart_item: cart_item.product_id == product_id)
        if item:
            product = self.find_product(product_id)
            if product:
                product.quantity += item.quantity
            self.save_products()
        return item is not None

    def cart_items(self):
        return self.cart.to_list()

    def cart_total(self):
        return sum(item.total for item in self.cart)

    def checkout(self, cashier):
        if len(self.cart) == 0:
            return None

        sale_date = date.today().isoformat()
        receipt_lines = []
        for item in self.cart:
            self.sales.append(SaleLine(item.product_id, item.name, item.quantity, item.total, sale_date))
            receipt_lines.append(f"{item.name} x{item.quantity} @ NGN {item.price:,.2f} = NGN {item.total:,.2f}")

        total = self.cart_total()
        receipt_name = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        receipt_path = RECEIPT_DIR / receipt_name
        receipt_path.write_text(
            "\n".join([
                "VENDORA POS RECEIPT",
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Cashier: {cashier}",
                "-" * 42,
                *receipt_lines,
                "-" * 42,
                f"TOTAL: NGN {total:,.2f}",
                "Thank you for shopping with Vendora.",
            ]),
            encoding="utf-8",
        )

        self.cart.clear()
        self.save_sales()
        return {"receipt": receipt_name, "total": total}

    def sales_summary(self):
        today = date.today().isoformat()
        todays_sales = [sale for sale in self.sales if sale.sale_date == today]
        if not todays_sales:
            todays_sales = self.sales.to_list()
        revenue = sum(sale.amount for sale in todays_sales)
        sold = sum(sale.quantity for sale in todays_sales)
        totals = {}
        for sale in todays_sales:
            totals[sale.product_name] = totals.get(sale.product_name, 0) + sale.quantity
        most_sold = max(totals, key=totals.get) if totals else "No sales yet"
        return {"revenue": revenue, "sold": sold, "most_sold": most_sold}

    def low_stock(self):
        return [product for product in self.products if product.quantity < self.low_stock_threshold]

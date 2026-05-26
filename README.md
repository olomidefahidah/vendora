# Vendora Python

Vendora Python is a web-based Inventory and Point-of-Sale System built with Python, Flask, HTML, CSS, and JavaScript.

## Features

- Login page with admin and cashier demo accounts
- Dashboard with revenue, products sold, cart total, and low-stock count
- Product catalogue with search by name or category
- Add products to the catalogue
- Cart and checkout workflow
- Receipt preview and receipt text download after checkout
- Sales report with revenue, quantity sold, and most sold product
- Low-stock alert page
- CSV file persistence
- Python OOP with a custom linked list implementation

## Demo Accounts

```text
admin / admin123
cashier / cashier123
```

## Run

```bat
cd vendora_python
python run.py
```

Then open:

```text
http://127.0.0.1:5005
```

## Structure

```text
vendora_python/
  app/
    __init__.py
    linked_list.py
    models.py
    routes.py
    store.py
  data/
    products.csv
    sales.csv
    users.csv
  receipts/
  static/
    css/styles.css
    js/app.js
  templates/
    index.html
    login.html
  run.py
```

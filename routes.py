from flask import Blueprint, current_app, jsonify, redirect, render_template, request, send_from_directory, session, url_for

from .store import RECEIPT_DIR


main = Blueprint("main", __name__)


def store():
    return current_app.config["STORE"]


@main.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("main.login"))
    return render_template("index.html", user=session["user"])


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = store().authenticate(request.form["username"], request.form["password"])
        if user:
            session["user"] = {"username": user.username, "role": user.role}
            return redirect(url_for("main.index"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@main.route("/api/state")
def api_state():
    query = request.args.get("q", "")
    products = [product.to_dict() for product in store().product_list(query)]
    cart = [item.to_dict() for item in store().cart_items()]
    summary = store().sales_summary()
    return jsonify({
        "products": products,
        "cart": cart,
        "cart_total": store().cart_total(),
        "summary": summary,
        "low_stock": [product.to_dict() for product in store().low_stock()],
        "sales": [sale.to_dict() for sale in store().sales],
        "user": session.get("user"),
    })


@main.route("/api/products", methods=["POST"])
def api_add_product():
    product = store().add_product(
        request.form["name"],
        request.form["category"],
        request.form["price"],
        request.form["quantity"],
    )
    return jsonify(product.to_dict())


@main.route("/api/cart/add", methods=["POST"])
def api_add_to_cart():
    ok = store().add_to_cart(int(request.form["product_id"]), int(request.form.get("quantity", 1)))
    return jsonify({"ok": ok})


@main.route("/api/cart/remove", methods=["POST"])
def api_remove_from_cart():
    ok = store().remove_from_cart(int(request.form["product_id"]))
    return jsonify({"ok": ok})


@main.route("/api/checkout", methods=["POST"])
def api_checkout():
    cashier = session.get("user", {}).get("username", "cashier")
    result = store().checkout(cashier)
    return jsonify({"ok": result is not None, "result": result})


@main.route("/receipts/<path:filename>")
def receipt_file(filename):
    return send_from_directory(RECEIPT_DIR, filename, as_attachment=True)

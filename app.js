const money = new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" });
const pageTitles = {
  dashboard: ["Inventory & Point-of-Sale", "Professional retail management workspace"],
  products: ["Product Management", "Manage catalogue records and add new stock items"],
  cart: ["Cart & Checkout", "Add products to cart and complete customer sales"],
  sales: ["Sales Report", "Track revenue, products sold, and best-selling items"],
  stock: ["Low Stock Alerts", "Identify products that need restocking"],
};

let state = {};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, options);
  return response.json();
}

async function loadState() {
  const query = $("search").value;
  state = await api(`/api/state?q=${encodeURIComponent(query)}`);
  render();
}

function toast(message) {
  $("toast").textContent = message;
  $("toast").classList.add("show");
  setTimeout(() => $("toast").classList.remove("show"), 1800);
}

function renderStats(target = "stats") {
  const html = [
    ["Total Revenue", money.format(state.summary.revenue)],
    ["Products Sold", state.summary.sold],
    ["Cart Total", money.format(state.cart_total)],
    ["Low Stock", state.low_stock.length],
  ].map(([label, value]) => `<div class="stat"><span>${label}</span><strong>${value}</strong></div>`).join("");
  $(target).innerHTML = html;
}

function productRows(products, columns = "full") {
  if (!products.length) return `<tr><td colspan="6" class="empty">No products found.</td></tr>`;
  return products.map(product => `
    <tr>
      <td>${product.id}</td>
      <td>${product.name}</td>
      ${columns === "full" ? `<td>${product.category}</td>` : ""}
      <td>${money.format(product.price)}</td>
      <td>${product.quantity < 10 ? `<span class="pill low">${product.quantity} low</span>` : product.quantity}</td>
      <td><button class="secondary" data-add="${product.id}" ${product.quantity < 1 ? "disabled" : ""}>Add</button></td>
    </tr>
  `).join("");
}

function renderProducts() {
  $("dashboard-products").innerHTML = productRows(state.products.slice(0, 6));
  $("products-table").innerHTML = productRows(state.products);
  $("cart-products").innerHTML = productRows(state.products, "cart");
  $("stock-alert").textContent = state.low_stock.length
    ? `Low stock notification: ${state.low_stock.map(item => item.name).join(", ")} need restocking.`
    : "All products are above the low-stock threshold.";
}

function cartMarkup() {
  if (!state.cart.length) return `<div class="empty">Cart is empty. Add products from the catalogue.</div>`;
  return `
    <div class="cart">
      ${state.cart.map(item => `
        <div class="cart-line">
          <div>${item.name}<small>${item.quantity} x ${money.format(item.price)}</small></div>
          <div class="cart-actions">
            <strong>${money.format(item.total)}</strong>
            <button class="danger" data-remove="${item.id}">Remove</button>
          </div>
        </div>
      `).join("")}
      <div class="total"><span>Total</span><span>${money.format(state.cart_total)}</span></div>
      <div class="checkout-actions">
        <button class="primary" id="checkout">Checkout</button>
        <button class="secondary" id="receipt-preview">Receipt</button>
      </div>
    </div>
  `;
}

function renderCart() {
  $("cart-box").innerHTML = cartMarkup();
  $("cart-page-box").innerHTML = cartMarkup();
}

function renderSales() {
  renderStats("sales-stats");
  $("sales-table").innerHTML = state.sales.length
    ? state.sales.map(sale => `<tr><td>${sale.date}</td><td>${sale.product_name}</td><td>${sale.quantity}</td><td>${money.format(sale.amount)}</td></tr>`).join("")
    : `<tr><td colspan="4" class="empty">No sales yet.</td></tr>`;
  const max = Math.max(...state.sales.map(sale => sale.amount), 1);
  $("analytics").innerHTML = `<div class="cart">
    <p><strong>Most sold product:</strong> ${state.summary.most_sold}</p>
    ${state.sales.slice(-6).map(sale => `
      <div class="bar">
        <span>${sale.product_name}</span>
        <div class="track"><div class="fill" style="width:${Math.max(8, sale.amount / max * 100)}%"></div></div>
        <strong>${sale.quantity}</strong>
      </div>
    `).join("")}
  </div>`;
}

function renderLowStock() {
  $("low-stock-table").innerHTML = state.low_stock.length
    ? state.low_stock.map(product => `<tr><td>${product.id}</td><td>${product.name}</td><td>${product.category}</td><td><span class="pill low">${product.quantity} left</span></td><td>Restock recommended</td></tr>`).join("")
    : `<tr><td colspan="5" class="empty">All products are above the threshold.</td></tr>`;
}

function render() {
  renderStats();
  renderProducts();
  renderCart();
  renderSales();
  renderLowStock();
}

function openModal(title, body) {
  $("modal-title").textContent = title;
  $("modal-body").innerHTML = body;
  $("modal").classList.add("show");
}

function receiptPreview() {
  if (!state.cart.length) return toast("Cart is empty.");
  const lines = state.cart.map(item => `${item.name} x${item.quantity} = ${money.format(item.total)}`).join("\n");
  openModal("Receipt Preview", `<div class="receipt">VENDORA POS RECEIPT\n${new Date().toLocaleString()}\n------------------------------\n${lines}\n------------------------------\nTOTAL: ${money.format(state.cart_total)}</div>`);
}

document.addEventListener("click", async (event) => {
  const nav = event.target.closest("nav button");
  const add = event.target.closest("[data-add]");
  const remove = event.target.closest("[data-remove]");

  if (nav) {
    document.querySelectorAll(".page").forEach(page => page.classList.toggle("active", page.id === nav.dataset.page));
    document.querySelectorAll("nav button").forEach(button => button.classList.toggle("active", button === nav));
    $("page-title").textContent = pageTitles[nav.dataset.page][0];
    $("page-subtitle").textContent = pageTitles[nav.dataset.page][1];
  }

  if (add) {
    const form = new FormData();
    form.append("product_id", add.dataset.add);
    await api("/api/cart/add", { method: "POST", body: form });
    toast("Item added to cart.");
    await loadState();
  }

  if (remove) {
    const form = new FormData();
    form.append("product_id", remove.dataset.remove);
    await api("/api/cart/remove", { method: "POST", body: form });
    toast("Item removed from cart.");
    await loadState();
  }

  if (event.target.id === "checkout") {
    const result = await api("/api/checkout", { method: "POST" });
    if (!result.ok) return toast("Cart is empty.");
    toast("Checkout completed.");
    openModal("Checkout Complete", `<p>Sale saved successfully.</p><p><strong>Total:</strong> ${money.format(result.result.total)}</p><a class="primary" href="/receipts/${result.result.receipt}">Download Receipt</a>`);
    await loadState();
  }

  if (event.target.id === "receipt-preview") receiptPreview();
  if (event.target.id === "modal-close" || event.target.id === "modal") $("modal").classList.remove("show");
});

$("product-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await api("/api/products", { method: "POST", body: new FormData(event.target) });
  event.target.reset();
  toast("Product added.");
  await loadState();
});

$("search").addEventListener("input", loadState);
$("theme-toggle").addEventListener("click", () => {
  document.body.dataset.theme = document.body.dataset.theme === "dark" ? "" : "dark";
});

loadState();

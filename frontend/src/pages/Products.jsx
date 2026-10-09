import React, { useEffect, useState } from "react";
import client from "../api/client";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ name: "", category: "", unit: "", selling_price: "", cost_price: "", stock_qty: "", low_stock_threshold: 5 });
  const [showForm, setShowForm] = useState(false);

  const load = () => client.get("/api/v1/products").then((res) => setProducts(res.data));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await client.post("/api/v1/products", {
      ...form,
      selling_price: parseFloat(form.selling_price),
      cost_price: parseFloat(form.cost_price || 0),
      stock_qty: parseInt(form.stock_qty || 0),
      low_stock_threshold: parseInt(form.low_stock_threshold || 5),
    });
    setForm({ name: "", category: "", unit: "", selling_price: "", cost_price: "", stock_qty: "", low_stock_threshold: 5 });
    setShowForm(false);
    load();
  };

  const adjustStock = async (id, delta) => {
    const qty = prompt(delta > 0 ? "Quantity to add (new purchase from wholesaler):" : "Quantity to remove (adjustment / damage):");
    if (!qty) return;
    const signedQty = delta > 0 ? Math.abs(parseInt(qty)) : -Math.abs(parseInt(qty));
    await client.post(`/api/v1/products/${id}/stock-transactions`, {
      type: delta > 0 ? "PURCHASE" : "ADJUSTMENT",
      quantity: signedQty,
      note: delta > 0 ? "Restock from wholesaler" : "Manual adjustment",
    });
    load();
  };

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <div className="eyebrow">Inventory</div>
          <h2>Products</h2>
        </div>
        <button onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "+ Add product"}</button>
      </div>

      {showForm && (
        <div className="card">
          <h3>New product</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid-2">
              <div>
                <label>Name</label>
                <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div>
                <label>Category</label>
                <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} placeholder="Electronics, Household…" />
              </div>
              <div>
                <label>Unit</label>
                <input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} placeholder="pcs, box, carton…" />
              </div>
              <div>
                <label>Selling price (₹)</label>
                <input required type="number" step="0.01" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })} />
              </div>
              <div>
                <label>Cost price (₹)</label>
                <input type="number" step="0.01" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })} />
              </div>
              <div>
                <label>Opening stock qty</label>
                <input type="number" value={form.stock_qty} onChange={(e) => setForm({ ...form, stock_qty: e.target.value })} />
              </div>
              <div>
                <label>Low stock threshold</label>
                <input type="number" value={form.low_stock_threshold} onChange={(e) => setForm({ ...form, low_stock_threshold: e.target.value })} />
              </div>
            </div>
            <button type="submit" style={{ marginTop: 16 }}>Save product</button>
          </form>
        </div>
      )}

      <div className="card">
        {products.length === 0 ? (
          <p className="empty-state">No products yet — add your first one above.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th></th></tr>
            </thead>
            <tbody>
              {products.map((p) => {
                const low = p.stock_qty <= p.low_stock_threshold;
                return (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td style={{ color: "var(--text-muted)" }}>{p.category || "—"}</td>
                    <td className="num">₹{p.selling_price}</td>
                    <td>
                      <span className={`num ${low ? "due" : ""}`}>{p.stock_qty}</span>{" "}
                      <span style={{ color: "var(--text-faint)", fontSize: 12 }}>{p.unit}</span>
                      {low && <span className="pill pill-debit" style={{ marginLeft: 8 }}>Low</span>}
                    </td>
                    <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                      <button className="secondary" onClick={() => adjustStock(p.id, 1)} style={{ marginRight: 6 }}>+ Stock</button>
                      <button className="secondary" onClick={() => adjustStock(p.id, -1)}>Adjust</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

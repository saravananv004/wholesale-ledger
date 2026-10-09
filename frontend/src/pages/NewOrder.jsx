import React, { useEffect, useState } from "react";
import client from "../api/client";
import { useNavigate } from "react-router-dom";

export default function NewOrder() {
  const [retailers, setRetailers] = useState([]);
  const [products, setProducts] = useState([]);
  const [retailerId, setRetailerId] = useState("");
  const [items, setItems] = useState([{ product_id: "", quantity: 1 }]);
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    client.get("/api/v1/retailers").then((res) => setRetailers(res.data));
    client.get("/api/v1/products").then((res) => setProducts(res.data));
  }, []);

  const updateItem = (idx, field, value) => {
    const next = [...items];
    next[idx][field] = value;
    setItems(next);
  };

  const addRow = () => setItems([...items, { product_id: "", quantity: 1 }]);
  const removeRow = (idx) => setItems(items.filter((_, i) => i !== idx));

  const total = items.reduce((sum, item) => {
    const p = products.find((p) => p.id === parseInt(item.product_id));
    return sum + (p ? p.selling_price * item.quantity : 0);
  }, 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await client.post("/api/v1/orders", {
        retailer_id: parseInt(retailerId),
        items: items.filter((i) => i.product_id).map((i) => ({ product_id: parseInt(i.product_id), quantity: parseInt(i.quantity) })),
        note,
      });
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create order");
    }
  };

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <div className="eyebrow">Sales</div>
          <h2>New order</h2>
        </div>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <label>Retailer</label>
          <select required value={retailerId} onChange={(e) => setRetailerId(e.target.value)}>
            <option value="">Select a shop…</option>
            {retailers.map((r) => <option key={r.id} value={r.id}>{r.shop_name}</option>)}
          </select>

          <label style={{ marginTop: 18 }}>Items</label>
          {items.map((item, idx) => (
            <div className="form-row" key={idx}>
              <div style={{ flex: 2 }}>
                <select value={item.product_id} onChange={(e) => updateItem(idx, "product_id", e.target.value)}>
                  <option value="">Select product…</option>
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} — ₹{p.selling_price} (stock: {p.stock_qty})</option>
                  ))}
                </select>
              </div>
              <div style={{ width: 90 }}>
                <input type="number" min="1" value={item.quantity} onChange={(e) => updateItem(idx, "quantity", e.target.value)} />
              </div>
              {items.length > 1 && (
                <button type="button" className="danger" onClick={() => removeRow(idx)} style={{ flexShrink: 0 }}>✕</button>
              )}
            </div>
          ))}
          <button type="button" className="secondary" onClick={addRow}>+ Add item</button>

          <label style={{ marginTop: 18 }}>Note (optional)</label>
          <input value={note} onChange={(e) => setNote(e.target.value)} />

          <div className="stat-card" style={{ marginTop: 18, marginBottom: 0 }}>
            <h4>Order total</h4>
            <div className="value">₹{total.toFixed(2)}</div>
          </div>

          {error && <p style={{ color: "var(--danger)", marginTop: 12 }}>{error}</p>}
          <button type="submit" style={{ marginTop: 18 }}>Confirm order</button>
        </form>
      </div>
    </div>
  );
}

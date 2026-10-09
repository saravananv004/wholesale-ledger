import React, { useEffect, useState } from "react";
import client from "../api/client";

// Public, no-login page. Shared as: yourapp.com/catalog?business=1
export default function Catalog() {
  const params = new URLSearchParams(window.location.search);
  const businessId = params.get("business") || "1";

  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({});
  const [shopName, setShopName] = useState("");
  const [phone, setPhone] = useState("");
  const [note, setNote] = useState("");
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    client.get(`/api/v1/public/catalog?business_id=${businessId}`).then((res) => setProducts(res.data));
  }, [businessId]);

  const setQty = (productId, qty) => setCart({ ...cart, [productId]: parseInt(qty) || 0 });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const items = Object.entries(cart).filter(([, qty]) => qty > 0).map(([product_id, quantity]) => ({ product_id: parseInt(product_id), quantity }));
    if (items.length === 0) return alert("Please select at least one item.");
    await client.post(`/api/v1/public/order-requests?business_id=${businessId}`, { shop_name: shopName, contact_phone: phone, note, items });
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--paper)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="card" style={{ maxWidth: 420, textAlign: "center" }}>
          <div className="login-mark" style={{ margin: "0 auto 16px" }}>✓</div>
          <h3>Request sent</h3>
          <p style={{ color: "var(--text-muted)" }}>The owner will contact you shortly to confirm your order.</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--paper)" }}>
      <div style={{ background: "var(--ink-900)", padding: "18px 0" }}>
        <div className="container" style={{ padding: "0 32px" }}>
          <span className="mark" style={{ marginRight: 8 }}>WL</span>
          <span style={{ color: "#fff", fontWeight: 700, fontSize: 15 }}>Product Catalog</span>
        </div>
      </div>

      <div className="container">
        <div className="card">
          {products.length === 0 ? (
            <p className="empty-state">No products available right now.</p>
          ) : (
            <table>
              <thead><tr><th>Product</th><th>Price</th><th>Availability</th><th>Qty</th></tr></thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td className="num">₹{p.selling_price}</td>
                    <td>
                      <span className={`pill ${p.in_stock ? "pill-credit" : "pill-debit"}`}>
                        {p.in_stock ? "In stock" : "Out of stock"}
                      </span>
                    </td>
                    <td>
                      <input type="number" min="0" disabled={!p.in_stock} style={{ width: 70 }} onChange={(e) => setQty(p.id, e.target.value)} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 12 }}>Submit order request</h4>
          <form onSubmit={handleSubmit}>
            <div className="grid-2">
              <div>
                <label>Shop name</label>
                <input required value={shopName} onChange={(e) => setShopName(e.target.value)} />
              </div>
              <div>
                <label>Phone</label>
                <input required value={phone} onChange={(e) => setPhone(e.target.value)} />
              </div>
            </div>
            <label>Note (optional)</label>
            <input value={note} onChange={(e) => setNote(e.target.value)} />
            <button type="submit" style={{ marginTop: 18 }}>Submit request</button>
          </form>
        </div>
      </div>
    </div>
  );
}

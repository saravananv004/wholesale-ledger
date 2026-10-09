import React, { useEffect, useState } from "react";
import client from "../api/client";
import { Link } from "react-router-dom";

export default function Retailers() {
  const [retailers, setRetailers] = useState([]);
  const [form, setForm] = useState({ shop_name: "", owner_name: "", phone: "", address: "", opening_balance: 0 });
  const [showForm, setShowForm] = useState(false);

  const load = () => client.get("/api/v1/retailers").then((res) => setRetailers(res.data));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await client.post("/api/v1/retailers", { ...form, opening_balance: parseFloat(form.opening_balance || 0) });
    setForm({ shop_name: "", owner_name: "", phone: "", address: "", opening_balance: 0 });
    setShowForm(false);
    load();
  };

  const remind = (retailer) => {
    const msg = encodeURIComponent(
      `Hi ${retailer.shop_name}, this is a reminder that your current due amount is ₹${retailer.current_balance}. Please arrange payment at your convenience. Thank you!`
    );
    window.open(`https://wa.me/${retailer.phone}?text=${msg}`, "_blank");
  };

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <div className="eyebrow">Customers</div>
          <h2>Retailers</h2>
        </div>
        <button onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "+ Add retailer"}</button>
      </div>

      {showForm && (
        <div className="card">
          <h3>New retailer</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid-2">
              <div>
                <label>Shop name</label>
                <input required value={form.shop_name} onChange={(e) => setForm({ ...form, shop_name: e.target.value })} />
              </div>
              <div>
                <label>Owner name</label>
                <input value={form.owner_name} onChange={(e) => setForm({ ...form, owner_name: e.target.value })} />
              </div>
              <div>
                <label>Phone (with country code, e.g. 91XXXXXXXXXX)</label>
                <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              </div>
              <div>
                <label>Address</label>
                <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
              </div>
              <div>
                <label>Opening balance — existing due from notebook (₹)</label>
                <input type="number" step="0.01" value={form.opening_balance} onChange={(e) => setForm({ ...form, opening_balance: e.target.value })} />
              </div>
            </div>
            <button type="submit" style={{ marginTop: 16 }}>Save retailer</button>
          </form>
        </div>
      )}

      <div className="card">
        {retailers.length === 0 ? (
          <p className="empty-state">No retailers yet — add your first shop above.</p>
        ) : (
          <table>
            <thead><tr><th>Shop</th><th>Phone</th><th>Balance due</th><th></th></tr></thead>
            <tbody>
              {retailers.map((r) => (
                <tr key={r.id}>
                  <td><Link to={`/retailers/${r.id}`}>{r.shop_name}</Link></td>
                  <td style={{ color: "var(--text-muted)" }}>{r.phone || "—"}</td>
                  <td className="num due">₹{Number(r.current_balance).toFixed(2)}</td>
                  <td style={{ textAlign: "right" }}>
                    {r.phone && <button className="secondary" onClick={() => remind(r)}>Send reminder</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

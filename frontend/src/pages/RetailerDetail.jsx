import React, { useEffect, useState } from "react";
import client from "../api/client";
import { Link } from "react-router-dom";

const emptyForm = { shop_name: "", owner_name: "", phone: "", address: "", opening_balance: 0 };

export default function Retailers() {
  const [retailers, setRetailers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const load = () => client.get("/api/v1/retailers").then((res) => setRetailers(res.data));
  useEffect(() => { load(); }, []);

  const closeForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setShowForm(false);
    setError("");
  };

  const startAdd = () => {
    if (showForm) return closeForm();
    setForm(emptyForm);
    setEditingId(null);
    setError("");
    setShowForm(true);
  };

  const startEdit = (r) => {
    setForm({
      shop_name: r.shop_name || "",
      owner_name: r.owner_name || "",
      phone: r.phone || "",
      address: r.address || "",
      opening_balance: r.opening_balance ?? 0,
    });
    setEditingId(r.id);
    setError("");
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const body = { ...form, opening_balance: parseFloat(form.opening_balance || 0) };
    try {
      if (editingId) {
        await client.patch(`/api/v1/retailers/${editingId}`, body);
      } else {
        await client.post("/api/v1/retailers", body);
      }
      closeForm();
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    }
  };

  const handleDelete = async (r) => {
    if (!window.confirm(`Delete "${r.shop_name}"? This cannot be undone.`)) return;
    try {
      await client.delete(`/api/v1/retailers/${r.id}`);
      if (editingId === r.id) closeForm();
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Could not delete this retailer.");
    }
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
        <button onClick={startAdd}>{showForm ? "Cancel" : "+ Add retailer"}</button>
      </div>

      {showForm && (
        <div className="card">
          <h3>{editingId ? "Edit retailer" : "New retailer"}</h3>
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
                {editingId && (
                  <small style={{ color: "var(--text-muted)" }}>
                    Can only be changed before any orders or payments are recorded.
                  </small>
                )}
              </div>
            </div>
            {error && <p style={{ color: "#b42318", marginTop: 12 }}>{error}</p>}
            <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
              <button type="submit">{editingId ? "Save changes" : "Save retailer"}</button>
              {editingId && <button type="button" className="secondary" onClick={closeForm}>Cancel</button>}
            </div>
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
                    <div style={{ display: "inline-flex", gap: 8 }}>
                      {r.phone && <button className="secondary" onClick={() => remind(r)}>Send reminder</button>}
                      <button className="secondary" onClick={() => startEdit(r)}>Edit</button>
                      <button className="secondary" style={{ color: "#b42318" }} onClick={() => handleDelete(r)}>Delete</button>
                    </div>
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
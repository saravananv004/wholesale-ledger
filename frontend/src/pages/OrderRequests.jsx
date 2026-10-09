import React, { useEffect, useState } from "react";
import client from "../api/client";

export default function OrderRequests() {
  const [requests, setRequests] = useState([]);

  const load = () => client.get("/api/v1/order-requests?status=NEW").then((res) => setRequests(res.data));
  useEffect(() => { load(); }, []);

  const confirm = async (id) => {
    if (!window.confirm("Confirm this request? It will create a real order and update stock and the ledger.")) return;
    try {
      await client.patch(`/api/v1/order-requests/${id}/confirm`);
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to confirm");
    }
  };

  const reject = async (id) => {
    await client.patch(`/api/v1/order-requests/${id}/reject`);
    load();
  };

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <div className="eyebrow">Public catalog</div>
          <h2>Pending order requests</h2>
        </div>
      </div>

      {requests.length === 0 ? (
        <div className="card"><p className="empty-state">No new requests right now.</p></div>
      ) : (
        requests.map((r) => (
          <div className="card" key={r.id}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h3 style={{ marginBottom: 2 }}>{r.shop_name}</h3>
                <p style={{ color: "var(--text-muted)", margin: 0, fontSize: 13 }}>{r.contact_phone}</p>
              </div>
              <span className="pill pill-pending">NEW</span>
            </div>
            {r.note && <p style={{ marginTop: 10 }}>{r.note}</p>}
            <table style={{ marginTop: 10 }}>
              <thead><tr><th>Product ID</th><th>Quantity</th></tr></thead>
              <tbody>
                {r.items.map((i) => (
                  <tr key={i.id}><td className="num">#{i.product_id}</td><td className="num">{i.quantity}</td></tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: 14 }}>
              <button onClick={() => confirm(r.id)} style={{ marginRight: 8 }}>Confirm</button>
              <button className="danger" onClick={() => reject(r.id)}>Reject</button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

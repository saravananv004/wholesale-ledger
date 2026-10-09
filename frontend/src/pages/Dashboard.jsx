import React, { useEffect, useState } from "react";
import client from "../api/client";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    client.get("/api/v1/dashboard/today").then((res) => setData(res.data));
  }, []);

  if (!data) return <div className="container">Loading…</div>;

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <div className="eyebrow">Overview</div>
          <h2>Dashboard</h2>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <h4>Today's sales</h4>
          <div className="value">₹{data.todays_sales.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <h4>Total outstanding dues</h4>
          <div className="value danger">₹{data.total_outstanding_dues.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <h4>Pending order requests</h4>
          <div className="value" style={{ color: data.pending_order_requests > 0 ? "var(--amber)" : "var(--ink-900)" }}>
            {data.pending_order_requests}
          </div>
        </div>
      </div>

      {data.pending_order_requests > 0 && (
        <div className="card" style={{ background: "var(--amber-bg)", borderColor: "#e8cfa8" }}>
          <strong style={{ color: "var(--amber)" }}>
            {data.pending_order_requests} new order request{data.pending_order_requests > 1 ? "s" : ""} waiting for review.
          </strong>{" "}
          <Link to="/order-requests">Review now →</Link>
        </div>
      )}

      <div className="card">
        <h4 style={{ marginBottom: 12 }}>Low stock items</h4>
        {data.low_stock_items.length === 0 ? (
          <p className="empty-state" style={{ padding: "16px 0" }}>Everything is well stocked.</p>
        ) : (
          <table>
            <thead><tr><th>Product</th><th>Stock qty</th></tr></thead>
            <tbody>
              {data.low_stock_items.map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td className="num due">{p.stock_qty}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h4 style={{ marginBottom: 12 }}>Top 5 shops by amount owed</h4>
        {data.top_debtors.length === 0 ? (
          <p className="empty-state" style={{ padding: "16px 0" }}>No dues yet.</p>
        ) : (
          <table>
            <thead><tr><th>Shop</th><th>Balance due</th></tr></thead>
            <tbody>
              {data.top_debtors.map((d) => (
                <tr key={d.retailer_id}>
                  <td><Link to={`/retailers/${d.retailer_id}`}>{d.shop_name}</Link></td>
                  <td className="num due">₹{d.balance.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

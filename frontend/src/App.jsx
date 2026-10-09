import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate, Link, useNavigate, useLocation } from "react-router-dom";
import client from "./api/client";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Products from "./pages/Products.jsx";
import Retailers from "./pages/Retailers.jsx";
import RetailerDetail from "./pages/RetailerDetail.jsx";
import NewOrder from "./pages/NewOrder.jsx";
import OrderRequests from "./pages/OrderRequests.jsx";
import Catalog from "./pages/Catalog.jsx";

function isLoggedIn() {
  return !!localStorage.getItem("token");
}

function ProtectedRoute({ children }) {
  return isLoggedIn() ? children : <Navigate to="/login" />;
}

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [pending, setPending] = useState(0);

  useEffect(() => {
    if (!isLoggedIn()) return;
    client
      .get("/api/v1/order-requests?status=NEW")
      .then((res) => setPending(res.data.length))
      .catch(() => {});
  }, [location.pathname]);

  if (!isLoggedIn()) return null;

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const links = [
    { to: "/", label: "Dashboard" },
    { to: "/products", label: "Products" },
    { to: "/retailers", label: "Retailers" },
    { to: "/orders/new", label: "New order" },
    { to: "/order-requests", label: "Order requests", count: pending },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <span className="mark">WL</span>
        <span className="title">Wholesale Ledger</span>
        <div className="subtitle">Distribution &amp; khata</div>
      </div>
      <div className="sidebar-nav">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={location.pathname === link.to ? "active" : ""}
          >
            {link.label}
            {!!link.count && <span className="badge">{link.count}</span>}
          </Link>
        ))}
      </div>
      <div className="sidebar-footer">
        <button className="secondary" style={{ width: "100%" }} onClick={logout}>
          Log out
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const location = useLocation();
  const isPublic = location.pathname === "/login" || location.pathname === "/catalog";

  if (isPublic) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/catalog" element={<Catalog />} />
      </Routes>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main">
        <Routes>
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
          <Route path="/retailers" element={<ProtectedRoute><Retailers /></ProtectedRoute>} />
          <Route path="/retailers/:id" element={<ProtectedRoute><RetailerDetail /></ProtectedRoute>} />
          <Route path="/orders/new" element={<ProtectedRoute><NewOrder /></ProtectedRoute>} />
          <Route path="/order-requests" element={<ProtectedRoute><OrderRequests /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </div>
  );
}

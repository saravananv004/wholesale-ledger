import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await client.post("/api/v1/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      navigate("/");
    } catch (err) {
      setError("Incorrect email or password.");
    }
  };

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-mark">WL</div>
        <h2 style={{ marginBottom: 2 }}>Wholesale Ledger</h2>
        <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 0, marginBottom: 20 }}>
          Sign in to manage orders, stock and dues.
        </p>
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required autoFocus />
          <label>Password</label>
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
          {error && (
            <p style={{ color: "var(--danger)", fontSize: 13, marginTop: 10, marginBottom: 0 }}>{error}</p>
          )}
          <button type="submit" style={{ width: "100%", marginTop: 18 }}>
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
}

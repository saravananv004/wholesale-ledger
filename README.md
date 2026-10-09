# Wholesale Distribution & Ledger System

Built from the project handbook (React + FastAPI + PostgreSQL). This version is for **Windows** (PowerShell).

## What's included

**backend/**: FastAPI app implementing everything from the handbook:
- Full DB schema (Section 6): businesses, users, products, retailers, orders,
  order_items, ledger_transactions, stock_transactions, order_requests, order_request_items
- The atomic Order -> Stock -> Ledger transaction (Section 7) in `app/services/order_service.py`
- All API endpoints from Section 10
- JWT auth, public catalog (no login), order request -> confirm flow
- Email notification hook for new order requests

**frontend/**: React (Vite) app with:
- Login, Dashboard, Products, Retailers (+ ledger/statement view), New Order,
  Order Requests, and the public Catalog page

## Prerequisites (Windows)

- Python 3.11 (check with `python --version`)
- Node.js (check with `node --version`)
- PostgreSQL for Windows, with the **password you set for the `postgres` user during installation**
- PowerShell (all commands below are PowerShell)

## First-time setup

### 1. Put the project in place

Copy the `backend` and `frontend` folders into:

```
C:\Users\acer\project\wholesale-ledger\
```

replacing what is there.

### 2. Create the database

Open **SQL Shell (psql)** from the Start menu. Press Enter through the prompts (server, database, port, username) and type your `postgres` password when asked. Then run:

```sql
CREATE DATABASE wholesale_ledger;
```

Type `\q` to exit. (Skip this if the database already exists. `\l` lists databases.)

### 3. Backend setup

```powershell
cd C:\Users\acer\project\wholesale-ledger\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install "psycopg[binary]"
```

If PowerShell blocks the activate script ("running scripts is disabled"), run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Create your real `.env` from the template:

```powershell
copy .env.example .env
notepad .env
```

Set these values in `.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/wholesale_ledger
JWT_SECRET=any-long-random-string
```

Notes on `DATABASE_URL`:
- **The password is required.** Without it you get `fe_sendauth: no password supplied`.
- Use `postgresql+psycopg://` (psycopg 3). If you use plain `postgresql://` you need `pip install psycopg2-binary` instead.
- If your password contains special characters, URL-encode them: `@` -> `%40`, `#` -> `%23`, `/` -> `%2F`, `:` -> `%3A`.

### 4. Create the database tables

```powershell
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

This creates all 10 tables from Section 6 in your `wholesale_ledger` database.

### 5. Seed the first owner login

```powershell
python seed.py
```

This creates the login `owner@example.com` / `changeme123`.
**Change this password after your first real login.** There is no "change password" screen yet.

### 6. Start the backend

```powershell
uvicorn app.main:app --reload
```

Runs at http://127.0.0.1:8000. API docs are at http://127.0.0.1:8000/docs

### 7. Start the frontend (open a NEW PowerShell window)

```powershell
cd C:\Users\acer\project\wholesale-ledger\frontend
npm install
npm run dev
```

Runs at http://localhost:5173. Log in with the seed credentials.

### 8. Try the public catalog

Visit: http://localhost:5173/catalog?business=1
(`business=1` is the first business created by `seed.py`)

## Every time you come back to the project

```powershell
# Terminal 1: backend
cd C:\Users\acer\project\wholesale-ledger\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: frontend
cd C:\Users\acer\project\wholesale-ledger\frontend
npm run dev
```

## Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'psycopg'` | `pip install "psycopg[binary]"` (with the venv active) |
| `fe_sendauth: no password supplied` | Add the password to `DATABASE_URL` in `.env` (see step 3) |
| `password authentication failed for user "postgres"` | Wrong password. Test it in SQL Shell (psql). To reset it, see below |
| `database "wholesale_ledger" does not exist` | Run `CREATE DATABASE wholesale_ledger;` in SQL Shell (psql) |
| `alembic` or `uvicorn` not recognized | The venv isn't active. Run `.\venv\Scripts\Activate.ps1` |
| `python seed .py` can't open file | Remove the space: `python seed.py` |
| Port 5432 connection refused | Make sure the PostgreSQL service is running (Win+R, `services.msc`, find `postgresql-x64-xx`) |

### Resetting a forgotten postgres password

1. Open `C:\Program Files\PostgreSQL\<version>\data\pg_hba.conf` in Notepad **as Administrator**.
2. On the lines for `127.0.0.1/32` and `::1/128`, change `scram-sha-256` (or `md5`) to `trust`.
3. In PowerShell (Admin), restart the service: `Restart-Service postgresql-x64-<version>`
4. Run `psql -U postgres`, then: `ALTER USER postgres WITH PASSWORD 'newpassword';`
5. Change `pg_hba.conf` back to `scram-sha-256` and restart the service again.
6. Update the password in `.env`.

## What to do next (Phase 10 in the handbook)

- Enter your real notebook balances as retailer `opening_balance` values
- Add your real products and stock quantities
- Run this alongside your paper notebook for about a week before switching over fully
- Set `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` / `NOTIFY_EMAIL` in `.env` if you want
  real email alerts for new order requests (Gmail SMTP or Brevo/Resend work well)

## Not yet built

- Order cancel/edit UI on the frontend (the backend endpoint exists: `PATCH /orders/{id}/cancel`)
- Excel/PDF export (Section 9, "Reports & Export"): backend endpoints not yet built
- "Change password" screen
- Production deployment (Vercel/Render/Supabase from Section 15): everything is local-only right now
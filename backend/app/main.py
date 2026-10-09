from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, products, retailers, orders, order_requests, public, dashboard

app = FastAPI(title="Wholesale Distribution & Ledger API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(retailers.router)
app.include_router(orders.router)
app.include_router(order_requests.router)
app.include_router(public.router)
app.include_router(dashboard.router)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Wholesale Ledger API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

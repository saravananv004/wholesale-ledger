"""
One-time script to create the first business + owner login.
Run with:  python seed.py
"""
from app.database import SessionLocal
from app.models.business import Business
from app.models.user import User
from app.auth.security import hash_password

OWNER_EMAIL = "owner@example.com"
OWNER_PASSWORD = "changeme123"

db = SessionLocal()

business = db.query(Business).first()
if not business:
    business = Business(name="My Wholesale Business", phone="", address="")
    db.add(business)
    db.flush()
    print(f"Created business: {business.name} (id={business.id})")
else:
    print(f"Business already exists: {business.name} (id={business.id})")

user = db.query(User).filter(User.email == OWNER_EMAIL).first()
if not user:
    user = User(
        business_id=business.id,
        email=OWNER_EMAIL,
        password_hash=hash_password(OWNER_PASSWORD),
        role="OWNER",
    )
    db.add(user)
    print(f"Created owner login -> email: {OWNER_EMAIL}  password: {OWNER_PASSWORD}")
else:
    print(f"Owner login already exists: {user.email}")

db.commit()
db.close()
print("Seed complete. IMPORTANT: change this password after first login.")

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="🎯 Mini CRM API - Production")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mini-crm-frontend-q2xw.onrender.com",  # Your actual frontend URL
        "https://*.onrender.com",
        "http://localhost:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./crm_data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    total_spend = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    message_template = Column(String)
    audience_type = Column(String, default="All Customers")
    status = Column(String, default="active")
    audience_size = Column(Integer, default=0)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_value = Column(Float)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    product_category = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str
    message_template: str
    audience_type: Optional[str] = "All Customers"
    created_by: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize sample data
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    if db.query(Customer).count() == 0:
        # Create sample customers
        customers = [
            Customer(name="Rahul Sharma", email="rahul@example.com", phone="+91-9876543210", total_spend=25000, total_orders=5),
            Customer(name="Priya Patel", email="priya@example.com", phone="+91-9876543211", total_spend=45000, total_orders=8),
            Customer(name="Arjun Kumar", email="arjun@example.com", phone="+91-9876543212", total_spend=15000, total_orders=3),
        ]
        for customer in customers:
            db.add(customer)
        
        # Create sample campaigns
        campaigns = [
            Campaign(name="Welcome Campaign", message_template="Hi {name}, welcome! 🎉", audience_type="New Customers", created_by="admin@example.com", audience_size=100),
        ]
        for campaign in campaigns:
            db.add(campaign)
        
        db.commit()
    db.close()

# API Endpoints
@app.get("/")
def root():
    return {"message": "🎯 Mini CRM API is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "platform": "Render"}

# Customer endpoints
@app.get("/customers")
def get_customers(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Customer).filter(Customer.is_active == True)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_term)) | (Customer.email.ilike(search_term))
        )
    customers = query.all()
    return [
        {
            "id": c.id, "name": c.name, "email": c.email, "phone": c.phone,
            "total_spend": c.total_spend, "total_orders": c.total_orders,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "is_active": c.is_active
        }
        for c in customers
    ]

@app.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_customer = Customer(name=customer.name, email=customer.email, phone=customer.phone)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return {"id": db_customer.id, "message": "Customer created successfully"}

# Campaign endpoints
@app.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return [
        {
            "id": c.id, "name": c.name, "message_template": c.message_template,
            "audience_type": c.audience_type, "status": c.status, "audience_size": c.audience_size,
            "created_by": c.created_by, "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in campaigns
    ]

@app.post("/campaigns")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    # Calculate audience size
    if campaign.audience_type == "All Customers":
        audience_size = db.query(Customer).filter(Customer.is_active == True).count()
    else:
        audience_size = 50  # Default for other types
    
    db_campaign = Campaign(
        name=campaign.name, message_template=campaign.message_template,
        audience_type=campaign.audience_type, audience_size=audience_size,
        created_by=campaign.created_by
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return {"id": db_campaign.id, "message": "Campaign created successfully"}

# Analytics endpoints
@app.get("/analytics/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    campaigns = db.query(Campaign).all()
    
    total_customers = len(customers)
    total_campaigns = len(campaigns)
    total_revenue = sum(c.total_spend for c in customers)
    total_orders = sum(c.total_orders for c in customers)
    
    return {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_campaigns": total_campaigns,
        "total_revenue": total_revenue,
        "avg_spend": total_revenue / total_customers if total_customers > 0 else 0
    }

@app.get("/analytics/customer-segments")
def get_customer_segments(db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    segments = {
        "high_value_customers": len([c for c in customers if c.total_spend > 30000]),
        "recently_active": len([c for c in customers if c.total_orders > 0]),
        "inactive_customers": len([c for c in customers if c.total_orders == 0]),
        "new_customers": len([c for c in customers if c.total_orders <= 1])
    }
    return {"segments": segments}

@app.get("/ai/generate-message")
def generate_ai_message(objective: str = "increase sales"):
    templates = [
        f"Hi {{name}}, achieve {objective}! Special offer inside. 🎯",
        f"{{name}}, ready to {objective.lower()}? Exclusive deal for you! ✨",
        f"Hey {{name}}! Your journey to {objective.lower()} starts here! 🚀"
    ]
    return {"messages": templates}

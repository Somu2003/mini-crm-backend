from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os

app = FastAPI(title="🎯 Mini CRM Platform API", version="2.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mini-crm-frontend-q2xw.onrender.com",
        "https://*.onrender.com",
        "http://localhost:8501",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./crm_platform.db"
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
    last_order_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_value = Column(Float)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    product_category = Column(String, nullable=True)

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

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    total_spend: Optional[float] = None
    total_orders: Optional[int] = None

class OrderCreate(BaseModel):
    customer_id: int
    order_value: float
    product_category: Optional[str] = None

class OrderUpdate(BaseModel):
    order_value: float
    status: Optional[str] = "completed"
    product_category: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str
    message_template: str
    audience_type: Optional[str] = "All Customers"
    created_by: str

class CampaignUpdate(BaseModel):
    name: str
    message_template: str
    audience_type: Optional[str] = None
    status: Optional[str] = None

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize sample data
def init_sample_data():
    db = SessionLocal()
    
    # Check if data exists
    if db.query(Customer).count() > 0:
        db.close()
        return
    
    # Create sample customers
    customers = [
        Customer(name="Rahul Sharma", email="rahul@example.com", phone="+91-9876543210", total_spend=25000, total_orders=5, last_order_date=datetime.utcnow() - timedelta(days=5)),
        Customer(name="Priya Patel", email="priya@example.com", phone="+91-9876543211", total_spend=45000, total_orders=8, last_order_date=datetime.utcnow() - timedelta(days=2)),
        Customer(name="Arjun Kumar", email="arjun@example.com", phone="+91-9876543212", total_spend=15000, total_orders=3, last_order_date=datetime.utcnow() - timedelta(days=10)),
        Customer(name="Sneha Gupta", email="sneha@example.com", phone="+91-9876543213", total_spend=35000, total_orders=6, last_order_date=datetime.utcnow() - timedelta(days=1)),
        Customer(name="Vikram Singh", email="vikram@example.com", phone="+91-9876543214", total_spend=0, total_orders=0),
    ]
    
    for customer in customers:
        db.add(customer)
    db.commit()
    
    # Create sample orders
    orders = [
        Order(customer_id=1, order_value=5000, product_category="Electronics", order_date=datetime.utcnow() - timedelta(days=5)),
        Order(customer_id=1, order_value=3000, product_category="Fashion", order_date=datetime.utcnow() - timedelta(days=3)),
        Order(customer_id=2, order_value=12000, product_category="Electronics", order_date=datetime.utcnow() - timedelta(days=2)),
        Order(customer_id=3, order_value=8000, product_category="Books", order_date=datetime.utcnow() - timedelta(days=10)),
        Order(customer_id=4, order_value=15000, product_category="Home & Garden", order_date=datetime.utcnow() - timedelta(days=1)),
    ]
    
    for order in orders:
        db.add(order)
    db.commit()
    
    # Create sample campaigns
    campaigns = [
        Campaign(name="Welcome Campaign", message_template="Hi {name}, welcome to our platform! 🎉", audience_type="New Customers", created_by="admin@example.com", audience_size=100, status="active"),
        Campaign(name="Loyalty Program", message_template="Hey {name}, check out our exclusive loyalty rewards! 💎", audience_type="High Value Customers", created_by="admin@example.com", audience_size=25, status="active"),
        Campaign(name="Win Back Campaign", message_template="We miss you {name}! Come back for special offers! 🎯", audience_type="Inactive Customers", created_by="admin@example.com", audience_size=50, status="paused"),
    ]
    
    for campaign in campaigns:
        db.add(campaign)
    db.commit()
    
    db.close()
    print("✅ Sample data initialized successfully!")

@app.on_event("startup")
async def startup_event():
    init_sample_data()

# API Endpoints
@app.get("/")
def root():
    return {
        "message": "🎯 Mini CRM Platform API is running!",
        "status": "healthy",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "platform": "Render",
        "timestamp": datetime.utcnow().isoformat()
    }

# Customer Endpoints
@app.get("/customers")
def get_customers(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Customer).filter(Customer.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_term)) | 
            (Customer.email.ilike(search_term))
        )
    
    customers = query.order_by(Customer.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "total_spend": c.total_spend,
            "total_orders": c.total_orders,
            "last_order_date": c.last_order_date.isoformat() if c.last_order_date else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "is_active": c.is_active
        }
        for c in customers
    ]

@app.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")
    
    db_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return {
        "id": db_customer.id,
        "name": db_customer.name,
        "email": db_customer.email,
        "message": "Customer created successfully"
    }

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if email is taken by another customer
    if customer.email != db_customer.email:
        existing = db.query(Customer).filter(
            Customer.email == customer.email, 
            Customer.id != customer_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken by another customer")
    
    # Update fields
    db_customer.name = customer.name
    db_customer.email = customer.email
    db_customer.phone = customer.phone
    
    if customer.total_spend is not None:
        db_customer.total_spend = customer.total_spend
    if customer.total_orders is not None:
        db_customer.total_orders = customer.total_orders
        if customer.total_orders > 0:
            db_customer.last_order_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_customer)
    
    return {
        "id": db_customer.id,
        "name": db_customer.name,
        "email": db_customer.email,
        "message": "Customer updated successfully"
    }

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_name = db_customer.name
    
    # Delete related orders
    db.query(Order).filter(Order.customer_id == customer_id).delete()
    
    # Mark customer as inactive
    db_customer.is_active = False
    db.commit()
    
    return {"message": f"Customer '{customer_name}' deleted successfully"}

# Order Endpoints
@app.get("/orders")
def get_orders(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Order)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    orders = query.order_by(Order.order_date.desc()).all()
    return [
        {
            "id": o.id,
            "customer_id": o.customer_id,
            "order_value": o.order_value,
            "order_date": o.order_date.isoformat(),
            "status": o.status,
            "product_category": o.product_category
        }
        for o in orders
    ]

@app.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create order
    db_order = Order(
        customer_id=order.customer_id,
        order_value=order.order_value,
        product_category=order.product_category
    )
    db.add(db_order)
    
    # Update customer totals
    customer.total_spend += order.order_value
    customer.total_orders += 1
    customer.last_order_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    
    return {
        "id": db_order.id,
        "customer_id": db_order.customer_id,
        "order_value": db_order.order_value,
        "message": "Order created successfully"
    }

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_value = db_order.order_value
    
    # Update order
    db_order.order_value = order.order_value
    db_order.status = order.status
    db_order.product_category = order.product_category
    
    # Update customer total
    customer = db.query(Customer).filter(Customer.id == db_order.customer_id).first()
    if customer:
        customer.total_spend = customer.total_spend - old_value + order.order_value
    
    db.commit()
    db.refresh(db_order)
    
    return {
        "id": db_order.id,
        "order_value": db_order.order_value,
        "message": "Order updated successfully"
    }

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update customer totals
    customer = db.query(Customer).filter(Customer.id == db_order.customer_id).first()
    if customer:
        customer.total_spend -= db_order.order_value
        customer.total_orders -= 1
    
    db.delete(db_order)
    db.commit()
    
    return {"message": "Order deleted successfully"}

# Campaign Endpoints
@app.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "message_template": c.message_template,
            "audience_type": c.audience_type,
            "status": c.status,
            "audience_size": c.audience_size,
            "created_by": c.created_by,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in campaigns
    ]

@app.post("/campaigns")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    # Calculate audience size based on type
    if campaign.audience_type == "All Customers":
        audience_size = db.query(Customer).filter(Customer.is_active == True).count()
    elif campaign.audience_type == "High Value Customers":
        audience_size = db.query(Customer).filter(Customer.total_spend > 30000, Customer.is_active == True).count()
    elif campaign.audience_type == "Inactive Customers":
        audience_size = db.query(Customer).filter(Customer.total_orders == 0, Customer.is_active == True).count()
    elif campaign.audience_type == "New Customers":
        audience_size = db.query(Customer).filter(Customer.total_orders <= 1, Customer.is_active == True).count()
    else:
        audience_size = db.query(Customer).filter(Customer.is_active == True).count()
    
    db_campaign = Campaign(
        name=campaign.name,
        message_template=campaign.message_template,
        audience_type=campaign.audience_type,
        audience_size=audience_size,
        created_by=campaign.created_by,
        status="active"
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return {
        "id": db_campaign.id,
        "name": db_campaign.name,
        "audience_size": db_campaign.audience_size,
        "message": "Campaign created successfully"
    }

@app.put("/campaigns/{campaign_id}")
def update_campaign(campaign_id: int, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update fields
    db_campaign.name = campaign.name
    db_campaign.message_template = campaign.message_template
    if campaign.audience_type:
        db_campaign.audience_type = campaign.audience_type
    if campaign.status:
        db_campaign.status = campaign.status
    
    db.commit()
    db.refresh(db_campaign)
    
    return {
        "id": db_campaign.id,
        "name": db_campaign.name,
        "status": db_campaign.status,
        "message": "Campaign updated successfully"
    }

@app.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign_name = db_campaign.name
    db.delete(db_campaign)
    db.commit()
    
    return {"message": f"Campaign '{campaign_name}' deleted successfully"}

@app.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Mock stats - in real implementation, you'd track actual delivery metrics
    return {
        "total_sent": campaign.audience_size,
        "delivered": int(campaign.audience_size * 0.95),
        "failed": int(campaign.audience_size * 0.05),
        "delivery_rate": 95.0,
        "open_rate": 24.5,
        "click_rate": 3.2
    }

# Analytics Endpoints
@app.get("/analytics/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    orders = db.query(Order).all()
    campaigns = db.query(Campaign).all()
    
    total_customers = len(customers)
    total_orders = len(orders)
    total_campaigns = len(campaigns)
    total_revenue = sum(c.total_spend for c in customers)
    avg_spend = total_revenue / total_customers if total_customers > 0 else 0
    active_campaigns = len([c for c in campaigns if c.status == 'active'])
    
    return {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_campaigns": total_campaigns,
        "total_revenue": total_revenue,
        "avg_spend": avg_spend,
        "active_campaigns": active_campaigns
    }

@app.get("/analytics/customer-segments")
def get_customer_segments(db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    
    segments = {
        "high_value_customers": len([c for c in customers if c.total_spend > 30000]),
        "recently_active": len([c for c in customers if c.total_orders > 0 and c.last_order_date and (datetime.utcnow() - c.last_order_date).days <= 30]),
        "inactive_customers": len([c for c in customers if c.total_orders == 0]),
        "new_customers": len([c for c in customers if c.total_orders <= 1])
    }
    
    return {"segments": segments}

# AI Endpoints
@app.get("/ai/generate-message")
def generate_ai_message(objective: str = Query(default="increase sales", description="Campaign objective")):
    """Generate AI-powered marketing messages"""
    
    templates = [
        f"Hi {{name}}, achieve your goal to {objective}! Special offer inside. 🎯",
        f"{{name}}, ready to {objective.lower()}? Exclusive deal just for you! ✨",
        f"Hey {{name}}! Your journey to {objective.lower()} starts here! 🚀",
        f"{{name}}, don't miss out on this opportunity to {objective.lower()}! Limited time! ⏰",
        f"Exclusive for {{name}}: Help us help you {objective.lower()} with our premium service! 💎"
    ]
    
    return {
        "messages": templates,
        "objective": objective,
        "count": len(templates)
    }

# Bulk Operations
@app.delete("/bulk/customers")
def bulk_delete_customers(customer_ids: List[int], db: Session = Depends(get_db)):
    """Bulk delete customers"""
    count = 0
    for customer_id in customer_ids:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.is_active = False
            count += 1
    
    db.commit()
    return {"message": f"Successfully deactivated {count} customers"}

@app.post("/bulk/campaigns/pause")
def bulk_pause_campaigns(campaign_ids: List[int], db: Session = Depends(get_db)):
    """Bulk pause campaigns"""
    count = 0
    for campaign_id in campaign_ids:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.status = "paused"
            count += 1
    
    db.commit()
    return {"message": f"Successfully paused {count} campaigns"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Customer, Order, Campaign, init_sample_data
from pydantic import BaseModel
import uvicorn
from typing import Optional
from datetime import datetime

app = FastAPI(title="🎯 Mini CRM API - Full CRUD Operations")

# Enhanced Pydantic models
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

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Mini CRM Platform API with Full CRUD...")
    init_sample_data()
    print("✅ API startup complete!")

@app.get("/")
def root():
    return {"message": "🎯 Mini CRM API with Full CRUD Operations!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

# ================================
# CUSTOMER CRUD OPERATIONS
# ================================

@app.get("/customers")
def get_customers(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Customer)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_term)) | 
            (Customer.email.ilike(search_term))
        )
    
    customers = query.all()
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

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "total_spend": customer.total_spend,
        "total_orders": customer.total_orders,
        "last_order_date": customer.last_order_date.isoformat() if customer.last_order_date else None,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "is_active": customer.is_active
    }

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
        "phone": db_customer.phone,
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
    
    # Update customer fields
    db_customer.name = customer.name
    db_customer.email = customer.email
    db_customer.phone = customer.phone
    
    # Update financial data if provided
    if customer.total_spend is not None:
        db_customer.total_spend = customer.total_spend
    
    if customer.total_orders is not None:
        db_customer.total_orders = customer.total_orders
        # Update last order date if orders increased
        if customer.total_orders > 0:
            db_customer.last_order_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_customer)
    
    return {
        "id": db_customer.id,
        "name": db_customer.name,
        "email": db_customer.email,
        "phone": db_customer.phone,
        "total_spend": db_customer.total_spend,
        "total_orders": db_customer.total_orders,
        "message": "Customer updated successfully"
    }

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_name = db_customer.name
    
    # Delete related orders first
    db.query(Order).filter(Order.customer_id == customer_id).delete()
    
    # Delete customer
    db.delete(db_customer)
    db.commit()
    
    return {"message": f"Customer '{customer_name}' and all related orders deleted successfully"}

# ================================
# ORDER CRUD OPERATIONS
# ================================

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

@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "order_value": order.order_value,
        "order_date": order.order_date.isoformat(),
        "status": order.status,
        "product_category": order.product_category
    }

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
    
    # Get customer to update their totals
    customer = db.query(Customer).filter(Customer.id == db_order.customer_id).first()
    
    # Update customer total spend (remove old value, add new value)
    if customer:
        customer.total_spend = customer.total_spend - db_order.order_value + order.order_value
    
    # Update order fields
    db_order.order_value = order.order_value
    db_order.status = order.status
    db_order.product_category = order.product_category
    
    db.commit()
    db.refresh(db_order)
    
    return {
        "id": db_order.id,
        "order_value": db_order.order_value,
        "status": db_order.status,
        "product_category": db_order.product_category,
        "message": "Order updated successfully"
    }

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get customer to update their totals
    customer = db.query(Customer).filter(Customer.id == db_order.customer_id).first()
    
    if customer:
        # Update customer totals
        customer.total_spend -= db_order.order_value
        customer.total_orders = max(0, customer.total_orders - 1)
        
        # Update last order date if no orders left
        if customer.total_orders == 0:
            customer.last_order_date = None
        else:
            # Get the latest remaining order
            latest_order = db.query(Order).filter(
                Order.customer_id == customer.id,
                Order.id != order_id
            ).order_by(Order.order_date.desc()).first()
            
            if latest_order:
                customer.last_order_date = latest_order.order_date
    
    order_value = db_order.order_value
    
    # Delete order
    db.delete(db_order)
    db.commit()
    
    return {"message": f"Order of ₹{order_value:,.0f} deleted successfully"}

# ================================
# CAMPAIGN CRUD OPERATIONS
# ================================

@app.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "message_template": c.message_template,
            "audience_type": c.audience_type,
            "audience_size": c.audience_size,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "created_by": c.created_by
        }
        for c in campaigns
    ]

@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "message_template": campaign.message_template,
        "audience_type": campaign.audience_type,
        "audience_size": campaign.audience_size,
        "status": campaign.status,
        "created_at": campaign.created_at.isoformat(),
        "created_by": campaign.created_by
    }

@app.post("/campaigns")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    # Calculate audience size based on type
    if campaign.audience_type == "All Customers":
        audience_size = db.query(Customer).count()
    elif campaign.audience_type == "High Value Customers":
        audience_size = db.query(Customer).filter(Customer.total_spend > 30000).count()
    elif campaign.audience_type == "Inactive Customers":
        audience_size = db.query(Customer).filter(Customer.total_orders == 0).count()
    else:
        audience_size = 10  # Default
    
    # Create campaign in database
    db_campaign = Campaign(
        name=campaign.name,
        message_template=campaign.message_template,
        audience_type=campaign.audience_type,
        audience_size=audience_size,
        created_by=campaign.created_by
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return {
        "id": db_campaign.id,
        "name": db_campaign.name,
        "message_template": db_campaign.message_template,
        "audience_size": db_campaign.audience_size,
        "status": db_campaign.status,
        "created_at": db_campaign.created_at.isoformat(),
        "message": "Campaign created successfully"
    }

@app.put("/campaigns/{campaign_id}")
def update_campaign(campaign_id: int, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update campaign fields
    db_campaign.name = campaign.name
    db_campaign.message_template = campaign.message_template
    
    if campaign.audience_type:
        db_campaign.audience_type = campaign.audience_type
        
        # Recalculate audience size if audience type changed
        if campaign.audience_type == "All Customers":
            db_campaign.audience_size = db.query(Customer).count()
        elif campaign.audience_type == "High Value Customers":
            db_campaign.audience_size = db.query(Customer).filter(Customer.total_spend > 30000).count()
        elif campaign.audience_type == "Inactive Customers":
            db_campaign.audience_size = db.query(Customer).filter(Customer.total_orders == 0).count()
    
    if campaign.status:
        db_campaign.status = campaign.status
    
    db.commit()
    db.refresh(db_campaign)
    
    return {
        "id": db_campaign.id,
        "name": db_campaign.name,
        "message_template": db_campaign.message_template,
        "audience_type": db_campaign.audience_type,
        "audience_size": db_campaign.audience_size,
        "status": db_campaign.status,
        "message": "Campaign updated successfully"
    }

@app.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign_name = db_campaign.name
    
    # Delete campaign
    db.delete(db_campaign)
    db.commit()
    
    return {"message": f"Campaign '{campaign_name}' deleted successfully"}

# ================================
# DASHBOARD & ANALYTICS
# ================================

@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    total_customers = len(customers)
    total_revenue = sum(c.total_spend for c in customers)
    total_orders = sum(c.total_orders for c in customers)
    
    return {
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_spend": total_revenue / total_customers if total_customers > 0 else 0
    }

@app.get("/analytics/dashboard")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    campaigns = db.query(Campaign).all()
    
    return {
        "overview": {
            "total_customers": len(customers),
            "total_campaigns": len(campaigns),
            "total_orders": sum(c.total_orders for c in customers),
            "total_revenue": sum(c.total_spend for c in customers)
        },
        "recent_campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "audience_size": c.audience_size,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            }
            for c in campaigns[-5:]  # Last 5 campaigns
        ]
    }

@app.get("/analytics/customer-segments")
def get_customer_segments(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    
    high_value = len([c for c in customers if c.total_spend > 30000])
    active = len([c for c in customers if c.total_orders > 0])
    inactive = len([c for c in customers if c.total_orders == 0])
    new_customers = len([c for c in customers if c.total_orders <= 1])
    
    return {
        "segments": {
            "high_value_customers": high_value,
            "recently_active": active,
            "inactive_customers": inactive,
            "new_customers": new_customers
        }
    }

# AI endpoints
@app.get("/ai/generate-message")
def generate_ai_message(objective: str):
    if "welcome" in objective.lower():
        messages = [
            "Welcome {name}! Thanks for joining us. Enjoy 10% off! 🎉",
            "Hi {name}, glad to have you aboard! Special discount inside! 🎁",
            "{name}, welcome to our family! Your exclusive offer awaits! ✨"
        ]
    elif "inactive" in objective.lower():
        messages = [
            "We miss you {name}! Come back with 15% off! 💝",
            "{name}, your comeback offer is here! Limited time! ⏰",
            "Hello {name}! We've saved something special for you! 🌟"
        ]
    else:
        messages = [
            f"Hi {{name}}, {objective} - Special offer just for you! 🎯",
            f"{{name}}, exclusive {objective} deal inside! 🔥",
            f"Hello {{name}}! Your personalized {objective} offer awaits! 💎"
        ]
    
    return {"messages": messages}

@app.post("/segments/preview")
def preview_segment(rules_data: dict, db: Session = Depends(get_db)):
    customers = db.query(Customer).limit(5).all()  # Sample preview
    
    return {
        "audience_size": db.query(Customer).count(),
        "sample_customers": [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "total_spend": c.total_spend,
                "total_orders": c.total_orders,
                "last_order_date": c.last_order_date.isoformat() if c.last_order_date else None
            }
            for c in customers
        ]
    }

@app.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "total_sent": campaign.audience_size,
        "delivered": int(campaign.audience_size * 0.9),  # 90% delivery rate
        "failed": int(campaign.audience_size * 0.1),
        "pending": 0,
        "delivery_rate": 90.0
    }

if __name__ == "__main__":
    print("🚀 Starting Mini CRM Backend with Full CRUD Operations...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("✨ Features: Create, Read, Update, Delete for all entities")
    uvicorn.run(app, host="localhost", port=8000)

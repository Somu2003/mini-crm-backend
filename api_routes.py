from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database import get_db, Customer
import json

router = APIRouter()

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

@router.get("/customers/")
async def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
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

@router.get("/analytics/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_customers = db.query(Customer).count()
    return {
        "overview": {
            "total_customers": total_customers,
            "total_campaigns": 0,
            "total_orders": 0,
            "total_revenue": 0
        },
        "recent_campaigns": []
    }

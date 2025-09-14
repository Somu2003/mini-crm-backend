from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

os.makedirs("data", exist_ok=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/crm_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    total_spend = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    last_order_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    order_value = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="completed")
    product_category = Column(String(100))

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)
    audience_type = Column(String(100), default="All Customers")
    audience_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(150), nullable=False)
    status = Column(String(50), default="active")

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_sample_data():
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Customer).count() > 0:
            print("Sample data already exists.")
            return
        
        print("Initializing sample data...")
        
        # Sample customers
        customers = [
            Customer(
                name="Rahul Sharma", 
                email="rahul@example.com", 
                phone="+91-9876543210", 
                total_spend=25000.50, 
                total_orders=5, 
                last_order_date=datetime(2024, 8, 15)
            ),
            Customer(
                name="Priya Singh", 
                email="priya@example.com", 
                phone="+91-9876543211", 
                total_spend=45000.75, 
                total_orders=8, 
                last_order_date=datetime(2024, 9, 2)
            ),
            Customer(
                name="Amit Kumar", 
                email="amit@example.com", 
                phone="+91-9876543212", 
                total_spend=8000.00, 
                total_orders=2, 
                last_order_date=datetime(2023, 12, 10)
            ),
            Customer(
                name="Sneha Patel", 
                email="sneha@example.com", 
                phone="+91-9876543213", 
                total_spend=67000.25, 
                total_orders=12, 
                last_order_date=datetime(2024, 9, 5)
            )
        ]
        
        for customer in customers:
            db.add(customer)
        
        # Sample campaigns
        campaigns = [
            Campaign(
                name="Welcome Campaign",
                message_template="Welcome {name}! Thanks for joining us! 🎉",
                audience_type="New Customers",
                audience_size=15,
                created_by="admin@example.com"
            ),
            Campaign(
                name="Reactivation Campaign",
                message_template="We miss you {name}! Come back with 20% off! 💝",
                audience_type="Inactive Customers", 
                audience_size=8,
                created_by="admin@example.com"
            )
        ]
        
        for campaign in campaigns:
            db.add(campaign)
        
        db.commit()
        print(f"✅ Successfully initialized {len(customers)} customers and {len(campaigns)} campaigns!")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()
    print("✅ Database setup complete!")

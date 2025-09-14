"""
Authentication module for Mini CRM Platform
Simplified OAuth implementation for demo purposes
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

class AuthService:
    """Simplified authentication service for demo purposes"""
    
    def __init__(self):
        self.secret_key = Config.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 1440  # 24 hours
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def simulate_google_oauth(self, user_data: dict) -> dict:
        """
        Simulate Google OAuth flow for demo purposes
        In production, this would integrate with actual Google OAuth
        """
        
        # Demo user validation
        demo_users = {
            "demo@example.com": {
                "name": "Demo User",
                "google_id": "demo_google_123",
                "picture": "https://via.placeholder.com/150"
            },
            "admin@crm.com": {
                "name": "CRM Admin", 
                "google_id": "admin_google_456",
                "picture": "https://via.placeholder.com/150"
            }
        }
        
        email = user_data.get("email")
        if email in demo_users:
            user_info = demo_users[email]
            
            # Create access token
            token_data = {
                "sub": email,
                "name": user_info["name"],
                "google_id": user_info["google_id"],
                "iat": datetime.utcnow()
            }
            
            access_token = self.create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_info": {
                    "email": email,
                    "name": user_info["name"],
                    "google_id": user_info["google_id"],
                    "picture": user_info["picture"]
                }
            }
        else:
            raise ValueError("User not found in demo system")
    
    def get_current_user(self, token: str) -> Optional[dict]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if payload:
            return {
                "email": payload.get("sub"),
                "name": payload.get("name"),
                "google_id": payload.get("google_id")
            }
        return None

# Demo authentication functions for Streamlit
def demo_login(email: str = "demo@example.com") -> dict:
    """Demo login function for Streamlit frontend"""
    auth_service = AuthService()
    
    try:
        return auth_service.simulate_google_oauth({"email": email})
    except ValueError as e:
        return {"error": str(e)}

def validate_demo_user(user_data: dict) -> bool:
    """Validate demo user credentials"""
    required_fields = ["email", "name"]
    return all(field in user_data for field in required_fields)

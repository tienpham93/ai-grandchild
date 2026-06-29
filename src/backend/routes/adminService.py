import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Project Modules
from src.backend.database import AdminUser, get_db

router = APIRouter()

@router.post("/api/login")
def login(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
        
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = db.query(AdminUser).filter(
        AdminUser.username == username, 
        AdminUser.password_hash == password_hash
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    return {"status": "success", "message": "Login successful"}
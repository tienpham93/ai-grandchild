import os
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Project Modules
from src.database import get_db, Family, Member

router = APIRouter()

@router.get("/")
def health_check(request: Request):
    """Supports health verification and challenge-response protocols."""
    challenge = request.query_params.get("challenge")
    if challenge:
        return Response(content=challenge, media_type="text/plain")
    return {"status": "running", "service": "AI Grandchild Webhook API"}

@router.get("/api/families")
def list_families(db: Session = Depends(get_db)):
    return db.query(Family).all()

@router.post("/api/families")
def add_family(data: dict, db: Session = Depends(get_db)):
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Family name required")
    family = Family(name=name)
    db.add(family)
    try:
        db.commit()
        db.refresh(family)
        return family
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Family directories must be unique")

@router.delete("/api/families/{family_id}")
def remove_family(family_id: int, db: Session = Depends(get_db)):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family directory not found")
    db.delete(family)
    db.commit()
    return {"status": "deleted"}

@router.get("/api/members")
def list_members(db: Session = Depends(get_db)):
    return db.query(Member).all()

@router.post("/api/members")
def add_member(data: dict, db: Session = Depends(get_db)):
    try:
        member = Member(
            chat_id=str(data["chat_id"]),
            family_id=int(data["family_id"]),
            name=data["name"],
            member_type=data["member_type"],
            member_role=data["member_role"],
            bank_account=data.get("bank_account")
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database insertion failed: {e}")

@router.put("/api/members/{chat_id}")
def update_member(chat_id: str, data: dict, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.chat_id == chat_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member credentials not found")
    
    member.member_type = data.get("member_type", member.member_type)
    member.member_role = data.get("member_role", member.member_role)
    member.name = data.get("name", member.name)
    member.bank_account = data.get("bank_account", member.bank_account)
    
    try:
        db.commit()
        db.refresh(member)
        return member
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database update failed: {e}")

@router.delete("/api/members/{chat_id}")
def revoke_member(chat_id: str, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.chat_id == chat_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member credentials not found")
    db.delete(member)
    db.commit()
    return {"status": "deleted"}

@router.get("/{filename}")
def serve_verification_file(filename: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "static", filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
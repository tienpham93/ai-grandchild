from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from src.backend.database import AutomationJob, get_db

router = APIRouter()

@router.get("/api/automation")
def list_automation_jobs(db: Session = Depends(get_db)):
    return db.query(AutomationJob).all()

@router.post("/api/automation")
def create_automation_job(data: dict, db: Session = Depends(get_db)):
    try:
        job = AutomationJob(
            name=data["name"],
            job_type=data["job_type"],
            family_id=int(data["family_id"]),
            target_chat_id=str(data["target_chat_id"]),
            interval_minutes=data.get("interval_minutes"),
            alert_family=data.get("alert_family", False),
            cron_time=data.get("cron_time"),
            cron_day_of_week=data.get("cron_day_of_week")
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to configure automation: {e}")
    
@router.delete("/api/automation/{job_id}")
def delete_automation_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(AutomationJob).filter(AutomationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Automation job not found")
    db.delete(job)
    db.commit()
    return {"status": "deleted"}
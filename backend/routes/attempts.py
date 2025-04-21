from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Attempt
from sqlalchemy import func

router = APIRouter()

@router.get("/attempts")
async def get_attempts(db: Session = Depends(get_db)):
    results = (
        db.query(Attempt.task_id, func.sum(Attempt.attempts).label("attempts"))
        .group_by(Attempt.task_id)
        .order_by(Attempt.task_id)
        .all()
    )

    return {
        "attempts": [{"task": task_id, "attempts": total_attempts} for task_id, total_attempts in results]
    }


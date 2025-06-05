from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Team, TeamProgress, Task
from sqlalchemy import func
from datetime import datetime
router = APIRouter()

@router.get("/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    teams_with_progress = db.query(Team, TeamProgress).outerjoin(
        TeamProgress, Team.id == TeamProgress.team_id
    ).all() # Получаем команду и ее прогресс (если есть)

    leaderboard = []
    # Находим максимальный ID задачи один раз
    max_task_id = db.query(func.max(Task.id)).scalar() or 0

    for team, progress in teams_with_progress:
        solved_tasks_count = 0
        finished_at_timestamp = None

        if progress:
            finished_at_timestamp = progress.finished_at
            if finished_at_timestamp is not None: # Команда финишировала ранее
                solved_tasks_count = max_task_id
            elif progress.current_task_id is None: # Не начинали или ошибка
                 solved_tasks_count = 0
            # Если current_task_id > max_task_id, считаем что финишировали
            elif progress.current_task_id > max_task_id:
                 solved_tasks_count = max_task_id
            else:
                solved_tasks_count = db.query(Task).filter(Task.id < progress.current_task_id).count()

        leaderboard.append({
            "team_name": team.name,
            "solved_tasks": solved_tasks_count,
            "finished_at": finished_at_timestamp # время финиша
        })

    # Сортируем: сначала по решенным задачам (убывание), потом по времени финиша (возрастание)
    leaderboard.sort(key=lambda x: (
        -x["solved_tasks"],
        x["finished_at"] if x["finished_at"] else datetime.max
    ))

    return {"teams": leaderboard}

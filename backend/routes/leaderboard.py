from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Team, TeamProgress, Task
from sqlalchemy import func # Добавь func
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
            elif progress.current_task_id is None: # Не начинали или ошибка?
                 solved_tasks_count = 0
            # Если current_task_id > max_task_id, считаем что финишировали
            elif progress.current_task_id > max_task_id:
                 solved_tasks_count = max_task_id
                 # Можно обновить finished_at здесь на всякий случай, если в /submit не сработало
            else: # В процессе
                solved_tasks_count = db.query(Task).filter(Task.id < progress.current_task_id).count()

        leaderboard.append({
            "team_name": team.name,
            "solved_tasks": solved_tasks_count,
            "finished_at": finished_at_timestamp # Отправляем время финиша
        })

    # Сортируем: сначала по решенным задачам (убывание), потом по времени финиша (возрастание, null в конце)
    leaderboard.sort(key=lambda x: (
        -x["solved_tasks"],
        x["finished_at"] if x["finished_at"] else datetime.max # None/null считается позже всех
    ))

    return {"teams": leaderboard} # Возвращаем обновленную структуру
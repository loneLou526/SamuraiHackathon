from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Attempt, Team, Task, TeamProgress
from backend.utils import get_current_team 

router = APIRouter()


@router.get("/task")
async def get_current_task(
        request: Request,
        team: Team = Depends(get_current_team),
        db: Session = Depends(get_db)
):
    progress = db.query(TeamProgress).filter(TeamProgress.team_id == team.id).first()
    print(progress.current_task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Прогресс команды не найден.")

    if not progress.current_task_id:
        raise HTTPException(status_code=404, detail="Команда еще не начала решать задачи.")

    task = db.query(Task).filter(Task.id == progress.current_task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    base_url = str(request.base_url)
    image_url = None
    if task.image_filename:
        image_url = f"{base_url.rstrip('/')}/static/uploads/{task.image_filename}"

    download_url = None
    if task.download_filename:
        download_url = f"{base_url.rstrip('/')}/static/uploads/{task.download_filename}"

    return {
        "id": task.id,
        "text": task.question,
        "image_url": image_url,
        "download_url": download_url,
        "download_display_name": task.download_display_name
    }


@router.post("/submit")
async def submit_answer(answer_data: dict, team: Team = Depends(get_current_team), db: Session = Depends(get_db)):
    progress = db.query(TeamProgress).filter(TeamProgress.team_id == team.id).first()

    if not progress or not progress.current_task_id:

        finished_already = progress and progress.finished_at is not None  # Проверяем, если есть поле finished_at
        if finished_already:
            return {"correct": True, "finished": True}  # Повторный запрос после финиша
        else:
            raise HTTPException(status_code=404, detail="Не удалось определить текущее задание или прогресс команды.")

    task = db.query(Task).filter(Task.id == progress.current_task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Текущее задание не найдено.")

    attempt = db.query(Attempt).filter(Attempt.team_id == team.id, Attempt.task_id == task.id).first()
    if attempt:
        attempt.attempts += 1  # Увеличиваем счетчик на 1
    else:
        # Если это первая попытка команды для этой задачи, создаем запись
        attempt = Attempt(team_id=team.id, task_id=task.id, attempts=1)
        db.add(attempt)

    # Проверяем правильность ответа
    is_correct = answer_data["answer"].strip().lower() == task.answer.lower()

    if is_correct:
        # Переход к следующей задаче или финиш
        max_task_id = db.query(func.max(Task.id)).scalar() or 0  # Получаем макс ID

        next_task_id = progress.current_task_id + 1

        if next_task_id > max_task_id:
            # Финиш
            if progress.finished_at is None:
                progress.finished_at = datetime.utcnow()

            db.commit()  # Сохраняем и счетчик попыток, и время финиша
            return {"correct": True, "finished": True}
        else:

            progress.current_task_id = next_task_id
            db.commit()  
            return {"correct": True, "finished": False}
    else:
        # Ответ неверный, просто сохраняем обновленный счетчик попыток
        db.commit()
        return {"correct": False}

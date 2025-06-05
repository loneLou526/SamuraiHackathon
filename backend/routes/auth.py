from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.team import Team 
from backend.schemas import TeamLogin  
from backend.utils import verify_password, generate_token  

router = APIRouter()

@router.post("/login")
async def login(team: TeamLogin, db: Session = Depends(get_db)):
    team_db = db.query(Team).filter(Team.name == team.team_name).first()

    if not team_db:
        raise HTTPException(status_code=401, detail="Неверное имя команды или пароль.")

    # Проверяем пароль
    if not verify_password(team.password, team_db.password_hash):
        raise HTTPException(status_code=401, detail="Неверное имя команды или пароль.")

    token = generate_token(team_db.id)
    return {"success": True, "token": token}

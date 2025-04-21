from pydantic import BaseModel

class TeamLogin(BaseModel):
    team_name: str
    password: str

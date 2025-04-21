from backend.database import Base, engine
from backend.models.task import Task
from backend.models.team import Team
from backend.models.teamProgress import TeamProgress
from backend.models.attempt import Attempt

Base.metadata.create_all(bind=engine)
print("Таблицы успешно созданы!")

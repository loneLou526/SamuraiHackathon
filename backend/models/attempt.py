from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    attempts = Column(Integer, default=0)

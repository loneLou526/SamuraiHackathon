from sqlalchemy import Integer, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.database import Base


class TeamProgress(Base):
    __tablename__ = "team_progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))
    current_task_id = Column(Integer, ForeignKey("task.id", ondelete="SET NULL"))
    finished_at = Column(DateTime, nullable=True, default=None)

    team = relationship("Team", back_populates="progress")
    task = relationship("Task")

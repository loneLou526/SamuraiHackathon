from sqlalchemy import Integer, String, \
    Column
from sqlalchemy.orm import relationship

from backend.database import Base


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)


    progress = relationship("TeamProgress", uselist=False, back_populates="team")
from sqlalchemy import Integer, String, \
    Column

from backend.database import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    image_filename = Column(String, nullable=True, default=None)
    download_filename = Column(String, nullable=True, default=None)
    download_display_name = Column(String, nullable=True, default=None)


"""
id	question	answer
1	Ты лох?	Да
2	2 + 2=	хз
3	ты выиграл?	железно
4	ну че?	ниче
"""
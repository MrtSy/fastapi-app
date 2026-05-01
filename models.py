from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Todo(Base):
	__tablename__= "todos"
	id = Column(Integer, primary_key=True, index=True)
	baslik = Column(String)
	tamamlandi = Column(Boolean, default=False)

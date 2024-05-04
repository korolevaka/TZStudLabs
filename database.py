from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine('sqlite:///database_info.db')
Base = declarative_base()
class UserAction(Base):
    __tablename__ = 'user_actions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    username = Column(String)
    first_name = Column(String)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)  # Set default

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def log_user_action(session, user_id, username, first_name, text):
    action = UserAction(user_id=user_id, username=username, first_name=first_name, text=text)
    session.add(action)
    session.commit()




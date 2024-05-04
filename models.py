from sqlalchemy import Column, String
from database import Base

class UserSettings(Base):
    __tablename__ = 'user_settings'
    user_id = Column(String, primary_key=True)
    city = Column(String)
    joke_category = Column(String)
    news_category = Column(String)

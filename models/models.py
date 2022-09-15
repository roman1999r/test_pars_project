from sqlalchemy import Column, Integer, Date, String

from core.db import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True, unique=True)
    photo = Column(String)
    title = Column(String)
    location = Column(String)
    date_posted = Column(Date)
    beds = Column(String)
    description = Column(String)
    price = Column(String)

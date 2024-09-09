import uuid
from sqlalchemy import Column, String, DateTime, Float
from app.services.connectors.postgres import Base


class Events(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=uuid.uuid4)
    title = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    min_price = Column(Float)
    max_price = Column(Float)
    is_online = Column(String)

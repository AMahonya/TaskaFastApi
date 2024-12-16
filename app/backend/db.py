from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_url_db

engine = create_engine(get_url_db(), echo=True)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

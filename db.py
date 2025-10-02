import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./planx_itf.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    grade = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    city = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    venue = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    has_physio = Column(Boolean, nullable=True)
    gender = Column(String(50), nullable=True)
    itf_link = Column(Text, nullable=True)
    qualifying_start = Column(Date, nullable=True)
    qualifying_end = Column(Date, nullable=True)
    surface = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    __table_args__ = (UniqueConstraint("name","start_date","city", name="uq_tournament_identity"),)

def init_db():
    Base.metadata.create_all(bind=engine)

def upsert_tournament(session, data: dict) -> Tournament:
    obj = session.query(Tournament).filter(Tournament.name==data.get("name"),
                                           Tournament.start_date==data.get("start_date"),
                                           Tournament.city==data.get("city")).first()
    if obj is None:
        obj = Tournament(**data); session.add(obj)
    else:
        for k,v in data.items(): setattr(obj,k,v)
    session.commit(); session.refresh(obj); return obj

def list_tournaments(session, limit=100, offset=0):
    return session.query(Tournament).order_by(Tournament.start_date.asc().nulls_last()).offset(offset).limit(limit).all()

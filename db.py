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
    year = Column(Integer, nullable=True)
    city = Column(String(255), nullable=True)
    country_code = Column(String(3), nullable=True)
    country = Column(String(255), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date   = Column(Date, nullable=True)
    surface = Column(String(50), nullable=True)
    venue   = Column(String(255), nullable=True)

    itf_link = Column(Text, nullable=False)
    apply_url = Column(Text, nullable=False)

    notes = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("itf_link", name="uq_itf_link_unique"),)

def init_db():
    Base.metadata.create_all(bind=engine)

def upsert_by_link(session, data: dict):
    obj = session.query(Tournament).filter(Tournament.itf_link==data["itf_link"]).first()
    if obj is None:
        obj = Tournament(**data); session.add(obj)
    else:
        for k,v in data.items(): setattr(obj,k,v)
    session.commit(); session.refresh(obj); return obj

def list_tournaments(session, limit=100, offset=0):
    return session.query(Tournament).order_by(Tournament.start_date.asc().nulls_last(),
                                              Tournament.end_date.asc().nulls_last(),
                                              Tournament.name.asc()).offset(offset).limit(limit).all()

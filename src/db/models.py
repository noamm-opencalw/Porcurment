from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config.settings import DB_PATH

Base = declarative_base()

_engine = None
_SessionLocal = None


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True)
    product_query = Column(String(500), nullable=False)
    status = Column(String(20), default="running")  # running | completed | failed
    deals_found = Column(Integer, default=0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey("search_queries.id"), nullable=False)
    title = Column(Text)
    description = Column(Text)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    url = Column(String(1000))
    seller = Column(String(200))
    phone = Column(String(50), default="N/A")
    source_type = Column(String(50))  # retail, wholesale, marketplace, b2b
    shipping_info = Column(String(200), default="unknown")
    verified = Column(Boolean, default=False)
    suspicious_flags = Column(JSON, nullable=True)
    total_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    verdict = Column(String(20), nullable=True)  # BUY, NEGOTIATE, PASS
    risk_level = Column(String(20), nullable=True)
    risk_notes = Column(Text, nullable=True)
    negotiation_strategy = Column(Text, nullable=True)
    score_breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey("search_queries.id"), nullable=False)
    recommendation_summary = Column(Text)
    top_deal_ids = Column(JSON)
    raw_output = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)

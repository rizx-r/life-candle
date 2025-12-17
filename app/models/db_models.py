from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    input_hash = Column(String, unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

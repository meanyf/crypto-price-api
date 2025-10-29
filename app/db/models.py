# models.py
from sqlalchemy import Column, Integer, Numeric, String, Text, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)


class Crypto(Base):
    __tablename__ = "cryptos"

    symbol = Column(String(20), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    current_price = Column(Numeric(20, 8), nullable=False)
    last_updated = Column(DateTime(timezone=True), nullable=False)

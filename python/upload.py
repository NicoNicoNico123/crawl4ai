import os
from sqlalchemy import create_engine, text, Column, String, Date, DateTime, Float, Integer, JSON, PrimaryKeyConstraint, Boolean
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
import pandas as pd
from sqlalchemy.dialects.postgresql import insert, ARRAY

Base = declarative_base()

class SummaryNewsTable(Base):
    __tablename__ = 'summary_news'
    
    success = Column(Boolean, nullable=False)
    url = Column(String, nullable=False)
    tickers = Column(ARRAY(String), nullable=True)
    title = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    category = Column(String, nullable=True)
    error = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)
    author = Column(String, nullable=True)
    
    __table_args__ = (
        PrimaryKeyConstraint('url', name='SummaryNews_pkey'),
    )


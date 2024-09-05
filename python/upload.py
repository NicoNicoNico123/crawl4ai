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
    
    url = Column(String, nullable=False)
    tickers = Column(ARRAY(String))
    title = Column(String)
    summary = Column(String)
    sentiment = Column(Float)
    error = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('url', name='SummaryNews_pkey'),
    )


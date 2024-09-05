import json
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
import os
from sqlalchemy import create_engine, text, Column, String, Date, DateTime, Float, Integer,JSON, PrimaryKeyConstraint
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
import pandas as pd
from sqlalchemy.dialects.postgresql import insert, ARRAY
import pytz
from sqlalchemy import text, func

load_dotenv()

def dataframe_to_db(df, cls):
    session, engine = DataBaseUpload.connect_sql()
    primary_key_columns = {key.name for key in cls.__table__.primary_key}

    print(f"Primary key columns: {primary_key_columns}")

    for index, row in df.iterrows():
        column_values = row.to_dict()
        stmt = insert(cls).values(**column_values)
        
        update_dict = {c.name: getattr(stmt.excluded, c.name) for c in cls.__table__.columns if c.name not in primary_key_columns}
        
        stmt = stmt.on_conflict_do_update(
            index_elements=primary_key_columns,
            set_=update_dict
        )
        
        try:
            session.execute(stmt)
            session.commit()
            print(f"Data for {column_values} added/updated successfully.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
    session.close()

class DataBaseUpload:

    USERNAME = os.getenv('DB_USERNAME')
    PASSWORD = os.getenv('DB_PASSWORD')
    DATABASE_NAME = os.getenv('DB_NAME')
    REMOTE_IP = os.getenv('DB_REMOTE_IP')

    @staticmethod
    def connect_sql():
        # Define your PostgreSQL connection parameters
        DATABASE_URL = f'postgresql+psycopg2://{DataBaseUpload.USERNAME}:{DataBaseUpload.PASSWORD}@{DataBaseUpload.REMOTE_IP}:5432/{DataBaseUpload.DATABASE_NAME}'
        # Create an SQLAlchemy engine
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session(), engine

class NewsQuery:

    @staticmethod
    def querynews(start_date=None, end_date=None, table_name='rss_news_fmp', site=None):
        session, engine = DataBaseUpload.connect_sql()

        try:
            # Fetch the earliest and latest dates if not provided
            if start_date is None or end_date is None:
                date_range_query = text(f"""
                    SELECT 
                        MIN("publishedDate") as min_date,
                        MAX("publishedDate") as max_date
                    FROM {table_name}
                """)
                date_range = session.execute(date_range_query).first()

                if start_date is None:
                    start_date = date_range.min_date
                if end_date is None:
                    end_date = date_range.max_date + timedelta(days=1)  # Include the last day

            query = text(f"""
            SELECT
                "publishedDate", 
                url,
                site
            FROM 
                {table_name}
            WHERE 
                "publishedDate" AT TIME ZONE 'America/New_York' >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}'::timestamp
                AND "publishedDate" AT TIME ZONE 'America/New_York' < '{end_date.strftime('%Y-%m-%d %H:%M:%S')}'::timestamp
                {f"AND site = '{site}'" if site else ''}
            ORDER BY 
                "publishedDate";
            """)

            df = pd.read_sql_query(query, engine)
            df = df.sort_values(by='publishedDate', ascending=True)
            print(f"Number of rows in df: {len(df)}")
            return df

        finally:
            session.close()


   
if __name__ == "__main__":
    # Test DataBaseUpload
    # try:
    #     session, engine = DataBaseUpload.connect_sql()
    #     print("Database connection successful!")
    #     # Test a simple query
    #     result = session.execute(text("SELECT 1"))
    #     print("Query result:", result.scalar())
    #     session.close()
    # except Exception as e:
    #     print("Database connection failed:", str(e))

    # Test querynewsall method
    try:
        start_date = datetime.now() - timedelta(days=7)  # 7 days ago
        #end_date = datetime.now()
        news_df = NewsQuery.querynews(start_date)
        print("querynewsall test successful!")
        print(f"Retrieved {len(news_df)} news items")
        print("Sample data:")
        print(news_df.head())
    except Exception as e:
        print("querynewsall test failed:", str(e))

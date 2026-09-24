from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URI = 'sqlite:///./expenseapp.db'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.kokgddswtdllqttsgptl:fucking_Bitch321@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'

# engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
# needs for sqlite 3

engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

""" pip install psycopg2-binary for postgresql database """

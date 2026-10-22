from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

database_url = os.getenv("DATABASE_URL")

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind = engine, autoflush = False, expire_on_commit = False)
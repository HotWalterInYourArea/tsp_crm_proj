from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()
database_url = os.getenv("DATABASE_URL")

engine = create_engine(
    database_url,
    pool_pre_ping=True,       
    pool_size=5,
    max_overflow=10,
    echo=False,               
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False, 
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
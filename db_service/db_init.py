from sqlalchemy import create_engine
from db_service.declarative_base import Base
import db_service.models

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2://postgres:password@localhost:5432/tsp_database")
    Base.metadata.create_all(engine)
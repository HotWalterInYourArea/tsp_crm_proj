from sqlalchemy import create_engine
from db_service.declarative_base import Base
from db_service.models.activity import Activity
from db_service.models.deal import Deal
from db_service.models.user import User
from db_service.models.client import Client
from db_service.models.department import Department
from db_service.models.associations import supervisor_user_deal, contact_client_deal
engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/tsp_database', pool_pre_ping=True)
Base.metadata.create_all(engine)
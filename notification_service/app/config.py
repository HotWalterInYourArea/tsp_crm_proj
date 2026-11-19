from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_exchange: str = "crm.events"
    rabbitmq_queue: str = "q.notifications"
    rabbitmq_routing_keys: str = "deal.created,activity.created"  # CSV

    jwt_secret: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"

    allow_query_token: bool = True


    class Config:
        env_file = ".env"


settings = Settings()
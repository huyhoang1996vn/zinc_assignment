import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from pydantic_settings import BaseSettings
from sqlmodel import Session, create_engine

load_dotenv()


class Settings(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME")
    SQL_URL: str = os.getenv("SQL_URL")

    class Config:
        env_file = ".env"


settings = Settings()
# region Config
sql_url = f"{settings.SQL_URL}/{settings.DB_NAME}"
engine = create_engine(sql_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

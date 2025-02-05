from dotenv import dotenv_values
from os import path
from pathlib import Path
from .structure import City
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session


BASE_DIR = Path(__file__).resolve().parents[1]
config = dotenv_values(path.join(BASE_DIR, '.env'))

engine = create_engine(config.get("DBPATH"))


def check_city(city: str) -> bool:
    """Проверяет наличие города в базе данных."""

    with Session(engine) as session:
        request = select(City.name).where(City.name.__eq__(city))
        response = session.scalar(request)

        return response != None

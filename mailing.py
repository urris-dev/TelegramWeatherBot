from datetime import datetime
from db.db_functions import check_city
from db.structure import City
from dotenv import dotenv_values
from os import path
from pathlib import Path
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session


BASE_DIR = Path(__file__).resolve().parents[0]
config = dotenv_values(path.join(BASE_DIR, '.env'))

engine = create_engine(config.get("DBPATH"))


class CityNotFoundError(Exception):
    pass

class UserIdFoundError(Exception):
    pass

class UserIdNotFoundError(Exception):
    pass


def mailing_subscribe(city: str, user_id: int):
    with Session(engine) as session:
        if check_city(city) == False:
            raise CityNotFoundError
        else:
            request = select(City).where(City.name.__eq__(city)).where(~(City.subscribed_user_ids.contains([user_id])))
            response = session.scalar(request)

            if response == None:
                raise UserIdFoundError
            else:
                response.subscribed_user_ids.append(user_id)
                session.commit()


def mailing_unsubscribe(city: str, user_id: int):
    with Session(engine) as session:
        if check_city(city) == False:
            raise CityNotFoundError
        else:
            request = select(City).where(City.name.__eq__(city)).where(City.subscribed_user_ids.contains([user_id]))
            response = session.scalar(request)

            if response == None:
                raise UserIdNotFoundError
            else:
                response.subscribed_user_ids.remove(user_id)
                session.commit()


def mailing_sleep(date: datetime) -> float:
    if date.hour < 7:
        launch_date = date.replace(hour=7, minute=0, second=0)
    else:
        launch_date = datetime.fromtimestamp(date.timestamp() + 86400).replace(hour=7, minute=0, second=0)
    
    delta = launch_date - date
    return delta.total_seconds()

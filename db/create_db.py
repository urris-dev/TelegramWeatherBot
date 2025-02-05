from dotenv import set_key
from os import path
from pathlib import Path
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from structure import Base


username = input("Введите имя пользователя базы данных: ")
password = input("Введите пароль от аккаунта пользователя: ")

BASE_DIR = Path(__file__).resolve().parents[1]
db_path = f'postgresql+psycopg2://{username}:{password}@localhost/weather'
set_key(path.join(BASE_DIR, '.env'), "DBPATH", db_path)

connection = connect(user=username, password=password)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = connection.cursor()
database = cursor.execute('CREATE DATABASE weather;')
cursor.close()
connection.close()

engine = create_engine(db_path)
Base.metadata.create_all(engine)

with open(f"{BASE_DIR}/db/cities.txt", "r") as file:
    with Session(engine) as session:
        session.execute(text(file.read()))
        session.commit()

print("База данных была успешно создана!")

from datetime import datetime
from db.db_functions import check_city
from db.structure import Weather
from dotenv import dotenv_values
from os import path
from pathlib import Path
from requests import get as request
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session


BASE_DIR = Path(__file__).resolve().parents[0]
config = dotenv_values(path.join(BASE_DIR, '.env'))

engine = create_engine(config.get("DBPATH"))


def get_wind_direction(degree: int | float) -> str:
    """Функция для преобразования направления ветра из градусов в сторону света."""

    if degree > 337.5 or 0 <= degree <= 22.5:
        return "С⬇️"
    elif 22.5 < degree <= 67.5:
        return "СВ↙️"
    elif 67.5 < degree <= 112.5:
        return "В⬅️"
    elif 112.5 < degree <= 157.5:
        return "ЮВ↖️"
    elif 157.5 < degree <= 202.5:
        return "Ю⬆️"
    elif 202.5 < degree <= 247.5:
        return "ЮЗ↗️"
    elif 247.5 < degree <= 292.5:
        return "З➡️"
    elif 292.5 < degree <= 337.5:
        return "СЗ↘️"


def get_data(city_name: str) -> dict:
    """Функция для сбора погодных данных в переданном городе."""

    url = "http://api.openweathermap.org/data/2.5/weather?"
    params = {
        "q": city_name,
        "appid": config.get("APPID"),
        "units": "metric",
        "lang": "ru"
    }

    response = request(url=url, params=params)
    response_data = response.json()
    
    timestamp = response_data['dt']
    weather = response_data['weather'][0]['description'].capitalize()
    clouds = response_data['clouds']['all']
    temp = response_data['main']['temp']
    temp_feels_like = response_data['main']['feels_like']
    wind_speed = response_data['wind']['speed']
    wind_degree = response_data['wind']['deg']

    return {
        "timestamp": timestamp,
        "weather": weather,
        "clouds": f"{clouds}%",
        "temp": f"{temp}°C",
        "temp_feels_like": f"{temp_feels_like}°C",
        "wind_speed": f"{wind_speed}м/с",
        "wind_direction": get_wind_direction(wind_degree)
        }


def get_weather(city: str) -> str:
    """Основная функция, кэширующая и возвращающая данные о прогнозе погоды в переданном городе."""

    with Session(engine) as session:
        if check_city(city) == False:
            return "Информация для такого города отсутствует."

        current_date = datetime.today()
        request = select(Weather).where(Weather.city.__eq__(city)).where(Weather.forecast_date.__eq__(current_date.strftime("%d.%m.%Y")))
        response = session.scalar(request)

        if (response == None):
            data = get_data(city)
            
            weather = Weather(city=city,
                              forecast_date=current_date.strftime("%d.%m.%Y"),
                              timestamp=data.pop("timestamp"),
                              weather=data)
            session.add(weather)
            response = session.new.pop()
            session.commit()

        elif (current_date.timestamp() - response.timestamp >= 900):
            data = get_data(city)
            
            response.timestamp = data.pop("timestamp")
            response.weather = data
            session.commit()    

        weather_data = [
            f"Город: {city}",
            f"Погода: {response.weather.get('weather')}",
            f"Облачность: {response.weather.get('clouds')}",
            f"Температура: {response.weather.get('temp')}",
            f"Ощущается как: {response.weather.get('temp_feels_like')}",
            f"Ветер: {response.weather.get('wind_speed')} {response.weather.get('wind_direction')}"
        ]

        return "\n".join(weather_data)
            
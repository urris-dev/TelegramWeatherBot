from asyncio import sleep
from datetime import datetime
from db.structure import Weather
from dotenv import dotenv_values
from os import path
from pathlib import Path
from requests import get as request
from sqlalchemy import select, delete, create_engine
from sqlalchemy.orm import Session
from weather import get_wind_direction


BASE_DIR = Path(__file__).resolve().parents[0]
config = dotenv_values(path.join(BASE_DIR, '.env'))

engine = create_engine(config.get("DBPATH"))


def get_data(city_name: str, forecasted_date: str) -> dict[str, dict]:
    """Функция для сбора погодных данных за определённый день в переданном городе."""

    url = "https://api.openweathermap.org/data/2.5/forecast?"
    params = {
        "q": city_name,
        "appid": config.get("APPID"),
        "units": "metric",
        "lang": "ru"
    }

    response = request(url=url, params=params)
    response_data = response.json()['list']

    # Ищем индекс начала диапазона нужных данных в ответе API
    index = 0
    while response_data[index]['dt_txt'] != forecasted_date:
        index += 1

    # Формируем сводку погоды для каждого времени дня
    forecast_data = dict.fromkeys(["Ночь🌃", "Утро🌇", "День🏙", "Вечер🌆"])
    for day_time in forecast_data:
        weather = response_data[index]['weather'][0]['description'].capitalize()
        clouds = response_data[index]['clouds']['all']
        wind_degree = response_data[index]['wind']['deg']
        temp = sorted([data['main']['temp']
                      for data in response_data[index - 1:index + 2]])
        temp_feels_like = sorted([data['main']['feels_like']
                                 for data in response_data[index - 1:index + 2]])
        wind_speed = sorted([data['wind']['speed']
                            for data in response_data[index - 1:index + 2]])

        forecast_data[day_time] = {
            "weather": weather,
            "clouds": f"{clouds}%",
            "temp": f"{min(temp)}°C...+{max(temp)}°C" if temp[-1] >= 0 else f"{max(temp)}°C...{min(temp)}°C",
            "temp_feels_like": f"{temp_feels_like[1]}°C",
            "wind_speed": f"{wind_speed[0]}-{wind_speed[-1]}м/с",
            "wind_direction": get_wind_direction(wind_degree)
        }

        index += 2

    return forecast_data


def get_weather_forecast(city: str, date: str) -> str:
    """Основная функция, кэширующая и предоставляющая полнодневную сводку погоды для переданного города."""

    with Session(engine) as session:
        request = select(Weather).where(Weather.city.__eq__(city)).where(Weather.forecast_date.__eq__(date))
        response = session.scalar(request)
        current_date = datetime.today()

        if response == None:
            forecasted_date = str(datetime.strptime(date, "%d.%m.%Y").replace(hour=3))
            data = get_data(city, forecasted_date)

            weather = Weather(city=city,
                              forecast_date=date,
                              timestamp=current_date.timestamp(),
                              weather=data)
            session.add(weather)
            response = session.new.pop()
            session.commit()

        elif current_date.timestamp() - response.timestamp >= 7200:
            forecasted_date = str(datetime.strptime(date, "%d.%m.%Y").replace(hour=3))
            data = get_data(city, forecasted_date)

            response.timestamp = current_date.timestamp()
            response.weather = data
            session.commit()

        forecast_data = list()
        day_times = ["Ночь🌃", "Утро🌇", "День🏙", "Вечер🌆"]
        for day_time in day_times:
            forecast_data.append(day_time.rjust(25))
            forecast_data.append(f"Погода: {response.weather.get(day_time).get('weather')}")
            forecast_data.append(f"Облачность: {response.weather.get(day_time).get('clouds')}")
            forecast_data.append(f"Температура: {response.weather.get(day_time).get('temp')}")
            forecast_data.append(f"Ощущается как: {response.weather.get(day_time).get('temp_feels_like')}")
            forecast_data.append(f"Ветер: {response.weather.get(day_time).get('wind_speed')} {response.weather.get(day_time).get('wind_direction')}")

        return '\n'.join(forecast_data)


def forecast_sleep(date: float):
    next_day = datetime.fromtimestamp(
        date + 86400).replace(hour=0, minute=0, second=10)

    return int(next_day.timestamp() - date)


async def remove_outdated_forecast_data():
    while True:
        current_date = datetime.today()

        with Session(engine) as session:
            request = delete(Weather).where(Weather.forecast_date.__eq__(current_date.strftime("%d.%m.%Y")))
            session.execute(request)
            session.commit()

        current_date = datetime.today().timestamp()
        seconds_sleep = forecast_sleep(current_date)

        await sleep(seconds_sleep)

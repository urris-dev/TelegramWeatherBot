## Телеграмм-бот для получения прогноза погоды

## Обзор
**Асинхронный** Telegram-бот, предоставляющий информацию о погоде в любом городе России.\
Информация **запрашивается у стороннего API-сервиса** посредством сетевых запросов.\
Реализована **функция периодического кэширования** полученной от API-сервиса информации в базе данных.

## Функциональность
* получение текущего прогноза погоды;
* получение полнодневной сводки погоды на ближайшие 4 дня;
* возможность оформления / отмены подписки на каждодневную рассылку погоды; 

## Используемые технологии
* База данных: **PostgreSQL 17**
* Язык программирования: **Python 3.10**
* ОРМ для работы с БД: **SQLAlchemy 2.0.37**
* API-сервис, предоставляющий погодные данные: **OpenWeatherMap**

## Зависимости
Представлены в файле **requirements.txt**.

## Структура проекта
* **db** - содержит файлы, связанные с базой данных.
* **main.py** - главный файл, отвечающий за работу бота.
* **weather.py** - файл, содержащий функции для получения текущего прогноза прогоды.
* **forecast.py** - файл, реализующий функции для получения полнодневной сводки прогоды.
* **mailing.py** - файл, отвечающий за ежедневную рассылку прогноза погоды.
* **.env** - файл с тестовыми переменными окружения.
* **.env.temp** - шаблон файла с переменными окружения.

## Запуск проекта

 1. Установить PostgreSQL версии 17+
 2. Установить Python версии 3.10+
 3. Клонировать данный репозиторий:
 ```bash
git clone https://github.com/urris-dev/TelegramWeatherBot.git
```
 4. Создать виртуальное окружение в корне проекта  и активировать его:
```bash
python -m venv .venv
source .venv/bin/activate #linux/mac
venv\Scripts\activate #windows
```
 5. Установить зависимости проекта из requirements.txt:
 ```bash
pip install -r requirements.txt
```
 6. Создать .env файл в корне проекта и заполнить его, следуя шаблону из .env.temp.
 7. Запустить файл create_db.py из директории db:
 ```bash
 cd db/
 python create_db.py
 ```
 8. Запустить файл main.py из корня проекта:
 ```bash
 cd -
 python main.py
 ```

## Демонстрация работы
![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/start.png)

![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/commands.png)

![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/weather.png)

![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/forecast.png)

![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/forecast-res.png)

![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/subscribe.png)

![](https://github.com/urris-dev/TelegramWeatherBot/blob/main/demo/subscribe-res.png)




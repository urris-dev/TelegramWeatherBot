from aiogram import Bot, Dispatcher, executor, types
from asyncio import sleep, new_event_loop, set_event_loop
from datetime import datetime
from db.db_functions import check_city
from db.structure import City
from dotenv import dotenv_values
from forecast import get_weather_forecast, remove_outdated_forecast_data
from mailing import CityNotFoundError, UserIdFoundError, UserIdNotFoundError, mailing_subscribe, mailing_unsubscribe, mailing_sleep
from os import path
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from weather import get_weather


BASE_DIR = Path(__file__).resolve().parents[0]
config = dotenv_values(path.join(BASE_DIR, '.env'))

engine = create_engine(config.get("DBPATH"))

BOT_TOKEN = config.get("BOT_TOKEN")
bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher(bot)


# Telegram-bot functions
@dispatcher.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer(f"Здравствуйте, {message.from_user['first_name']}.\n"
                          "Для получения списка доступных команд используйте /commands.")


@dispatcher.message_handler(commands=["commands"])
async def send_command_list(message: types.Message):
    await message.answer("📋Список доступных команд:\n"
                         "/weather [Название города] - Узнать текущую погоду в Вашем городе;\n"
                         "/forecast [Название города] - Получить полнодневную сводку погоды на ближайшие 4 дня для Вашего города.\n"
                         "/subscribe [Название города] - Подписаться на рассылку погоды для Вашего города;\n"
                         "/unsubscribe [Название города] - Отменить подписку на рассылку погоды для Вашего города;")


@dispatcher.message_handler(commands=['weather'])
async def send_weather(message: types.Message):
    if len(message.text) > 9:
        weather_data = get_weather(message.text[9:])
        await message.answer(weather_data)
    else:
        await message.answer("Пожалуйста, введите название города.")


@dispatcher.message_handler(commands=['forecast'])
async def request_forecast(message: types.Message):
    if len(message.text) <= 10:
        await message.answer("Пожалуйста, введите название города.")
    else:
        city = message.text[10:]
        if check_city(city) == False:
            await message.answer("Сводка погоды для данного города не предоставляется.")

        current_date = datetime.today().timestamp()
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for i in range(1, 5):
            forecast_date = datetime.fromtimestamp(
                current_date + 86400 * i).strftime("%d.%m.%Y")
            keyboard.insert(types.InlineKeyboardButton(
                forecast_date, callback_data=f"{city} {forecast_date}"))
        await message.answer("📅Выберите нужную дату:", reply_markup=keyboard)


@dispatcher.callback_query_handler()
async def send_forecast(callback_query: types.CallbackQuery):
    system_data = callback_query.message
    await bot.delete_message(system_data['chat']['id'], system_data['message_id'])

    city, date = callback_query.data.split()
    forecast_data = get_weather_forecast(city, date)
    await bot.send_message(system_data['chat']['id'], f"Сводка погоды на {date}\n{forecast_data}")


@dispatcher.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if len(message.text) <= 11:
        await message.answer("Пожалуйста, введите название города.")
    else:
        city = message.text[11:]
        user_id = message.from_user['id']
        try:
            mailing_subscribe(city, user_id)
            await message.answer("Ваша подписка была успешно оформлена. ✅\n"
                                 "Рассылка погоды проходит каждый день в 7:00. 🕖")
        except CityNotFoundError:
            await message.answer("Рассылка погоды для данного города не предоставляется.")
        except UserIdFoundError:
            await message.answer("Вы уже подписались на рассылку для данного города.")            


@dispatcher.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if len(message.text) <= 13:
        await message.answer("Пожалуйста, введите название города.")
    else:
        city = message.text[13:]
        user_id = message.from_user['id']
        try:
            mailing_unsubscribe(city, user_id)
            await message.answer("Вы успешно отменили подписку на рассылку погоды. ✅")
        except CityNotFoundError:
            await message.answer("Рассылка погоды для данного города не предоставляется.")
        except UserIdNotFoundError:
            await message.answer("Вы не подписаны на рассылку погоды для данного города.")


@dispatcher.message_handler()
async def echo(message: types.Message):
    await message.answer("Извините, я Вас не понимаю.")


# System functions
async def launch_mailing():
    while True:
        current_date = datetime.today()
        seconds_sleep = mailing_sleep(current_date)

        await sleep(seconds_sleep)

        with Session(engine) as session:
            request = select(City).where(City.subscribed_user_ids != [])
            response = session.scalars(request)

            for row in response.all():
                weather_data = get_weather(row.name)
                for user_id in row.subscribed_user_ids:
                    await bot.send_message(user_id, f"📬Ежедневная рассылка погоды📬\n{weather_data}")


if __name__ == "__main__":
    loop = new_event_loop()
    loop.create_task(launch_mailing())
    loop.create_task(remove_outdated_forecast_data())

    set_event_loop(loop=loop)
    executor.start_polling(dispatcher)

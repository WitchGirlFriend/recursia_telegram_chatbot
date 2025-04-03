# 7771992031:AAFAPy8wp8oWmAYGe4CM80etIEDzdlmWbkQ
# я админ 5217615894
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums.parse_mode import ParseMode
from aiogram import BaseMiddleware
from aiogram.filters import Command
import asyncio
import pyodbc

from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

con = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-ODS8NT1;DATABASE=master;trusted_connection=yes')
cur = con.cursor()

API_TOKEN = '7771992031:AAFAPy8wp8oWmAYGe4CM80etIEDzdlmWbkQ'
ADMIN = [5217615894]
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_queries = {}
question1 = "Вопрос 1"
question2 = "Вопрос 2"
question3 = "Вопрос 3"
question4 = "Вопрос 4"


kb = [
        [
            types.KeyboardButton(text=question1, callback_data="button1"),
            types.KeyboardButton(text=question2, callback_data="button2"),
            types.KeyboardButton(text=question3, callback_data="button3"),
            types.KeyboardButton(text=question4, callback_data="button4")
        ],
    ]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb,
        resize_keyboard=True)

def send_to_db(user_id, user_message):
    cur.execute(f"INSERT INTO chatbot (users_id, users_text, status) VALUES ('{user_id}', '{user_message}', 0)")
    cur.commit()

def update_db(user_id, user_message):
    cur.execute(f"UPDATE chatbot SET status = 1 WHERE users_id = {user_id} AND users_text = '{user_message}'")
    cur.commit()

def take_from_db():
    cur.execute("SELECT * FROM chatbot WHERE status = 0")
    fetched = cur.fetchall()
    return fetched

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN:
        await message.answer("Добро пожаловать в админ-панель.")
        sent_messages = take_from_db()
        if sent_messages:
            for i in sent_messages:
                await message.answer(f"Запрос {i}")
        else:
            await message.answer("Нет новых запросов.")
    else:
        await message.answer("Вы не администратор.")

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await bot.send_message(message.chat.id, text="Привет! Я бот поддержки!. Я могу ответить на часто задаваемые вопросы. \n Если интересующего вас вопроса нет - напишите его!", reply_markup=keyboard)


@dp.message()
async def handle_message(message: types.Message):
    user_message = message.text
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    if user_id in ADMIN:
        print(f'Пишет админ {user_name} ({user_id}): {user_message}')
        if message.reply_to_message:
            info = message.reply_to_message.text[7:].strip("()").replace(' ', '')
            massive = info.split(',')
            client_id = massive[1].replace("'", '')
            client_msg = massive[2].replace("'", '')
            # Отправляем ответ пользователю
            print(f"Отправляем {client_id} сообщение")
            try:
                await bot.send_message(user_id, f"Ответ от администратора: {message.text}")
                await message.answer("Ответ отправлен пользователю.")
                update_db(client_id, client_msg)
                print("Отправляем пользователю")
            except Exception as e:
                await message.answer(f"Ошибка при отправке сообщения пользователю: {e}")
        else:
            await message.answer("Для ответа нужно ответить на конкретный запрос!")

    else:
        if user_message == question1:
            await message.answer(f"Ответ 1")
            return
        if user_message == question2:
            await message.answer(f"Ответ 2")
            return
        if user_message == question3:
            await message.answer(f"Ответ 3")
            return
        if user_message == question4:
            await message.answer(f"Ответ 4")
            return
        else:
            # Отправляем сообщение админу
            #for admin_id in ADMIN:
                #print(admin_id)
                #await bot.send_message(admin_id, f"Новое сообщение от {user_name} ({user_id}):\n{user_message}")
                try:
                    print(user_id, user_message)
                    send_to_db(user_id, user_message)
                    await message.answer(
                        f"Ваше сообщение было отправлено администратору, {user_name}! Скоро с вами свяжутся.")
                except:
                    await message.answer("Произошла ошибка с передачей данных")
                # Отправляем подтверждение пользователю




# Обработчик ошибок
async def error_handler(update: types.Update, exception: Exception):
    logging.error(f"Произошла ошибка: {exception}")
    # Отправка сообщения администратору о сбое (по желанию)
    for admin_id in ADMIN:
        await bot.send_message(admin_id, f"Ошибка в боте: {exception}")


async def on_start():
    # Запускаем polling для бота
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

# Основная функция для запуска бота
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from asyncio import run

    run(on_start())
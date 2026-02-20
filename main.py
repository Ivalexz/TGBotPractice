import asyncio
import aiohttp
from aiogram import  Bot, Dispatcher,types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
from aiogram.types import CallbackQuery
import tracemalloc
import os
from dotenv import load_dotenv

tracemalloc.start()
load_dotenv()

api_token = os.getenv("BOT_TOKEN")
API_URL = "http://localhost:8000"

mybot = Bot(token=api_token)
disp = Dispatcher()

user_commands = {}

info_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Додати задачу"), KeyboardButton(text="Видалити задачу")],
        [KeyboardButton(text="Показати всі задачі"), KeyboardButton(text="Змінити статус задачі")]
    ],
    resize_keyboard=True,
)


@disp.message(CommandStart())
async def start(msg: Message):
    user_commands[msg.from_user.id] = None
    await msg.answer("Привіт, я Ваш менеджер задач!", reply_markup=info_buttons)

@disp.message(F.text == "Додати задачу")
async def add_task_msg(msg: Message):
    user_commands[msg.from_user.id] = "add"
    await msg.answer("Введіть у форматі: Назва - Опис")


@disp.message(F.text == "Показати всі задачі")
async def show_tasks(msg: Message):
    user_id = msg.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/tasks/{user_id}") as resp:
            data = await resp.json()

    tasks = data.get("tasks", {})

    if not tasks:
        await msg.answer("У Вас ще немає задач")
        return

    text = "Ваші задачі:\n"
    for task_id, task in tasks.items():
        text += f"ID {task_id} - {task['name']} - {task['description']} - {task['status']}\n"

    await msg.answer(text)


@disp.message(F.text == "Видалити задачу")
async def delete_task_msg(msg: Message):
    user_commands[msg.from_user.id] = "delete"
    await msg.answer("Введіть ID задачі")


@disp.message(F.text == "Змінити статус задачі")
async def change_status_msg(msg: Message):
    user_commands[msg.from_user.id] = "status"
    await msg.answer("Введіть ID задачі")

@disp.message(F.text)
async def all_text_commands(msg: Message):
    user_id = msg.from_user.id
    command = user_commands.get(user_id)

    if command == "add":
        if " - " not in msg.text:
            await msg.answer("Невірний формат. Назва - Опис")
            return

        name, description = msg.text.split(" - ", 1)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{API_URL}/tasks/{user_id}",
                    json={"name": name, "description": description}
            ) as resp:
                data = await resp.json()

        user_commands[user_id] = None
        await msg.answer(f"Задача додана! ID: {data['task']['id']}")

    elif command == "delete":
        if not msg.text.isdigit():
            await msg.answer("Потрібно ввести ID (число)")
            return

        task_id = int(msg.text)

        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{API_URL}/tasks/{user_id}/{task_id}") as resp:
                if resp.status == 404:
                    await msg.answer("Задачу не знайдено")
                    return

        user_commands[user_id] = None
        await msg.answer("Задача видалена")


    elif command == "status":
        if not msg.text.isdigit():
            await msg.answer("Потрібно ввести ID")
            return

        task_id = int(msg.text)
        async with aiohttp.ClientSession() as session:

            async with session.patch(f"{API_URL}/tasks/{user_id}/{task_id}") as resp:
                if resp.status == 404:
                    await msg.answer("Задачу не знайдено")
                    return
                data = await resp.json()
        user_commands[user_id] = None
        await msg.answer(f"Новий статус: {data['task']['status']}")

    else:
        await msg.answer("Оберіть дію з меню")



async def startBot():
    await disp.start_polling(mybot)


asyncio.run(startBot())
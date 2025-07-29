import asyncio
import logging
import sys
from os import environ
from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import json
from main import (
    get_places_mgsu,
    get_places_mpei,
    user_friendly_data,
    get_data_file,
    update_data_file,
)
from kb import main_kb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

load_dotenv()


def load_config(key, default=None):
    value = environ.get(key)
    try:
        return json.loads(value) if value is not None else default
    except json.JSONDecodeError as e:
        return default


token = environ.get("token")
allowed_ids = load_config("allowed_ids")
admins = load_config("admins")
urls_mpei = load_config("urls_mpei")
ids_mpei = load_config("ids_mpei")
urls_mgsu = load_config("urls_mgsu")
ids_mgsu = load_config("ids_mgsu")
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if message.from_user.id not in allowed_ids:
        await message.answer(
            f"Hello, {html.bold(message.from_user.full_name)} you can't use this bot!"
        )
    else:
        await message.answer(
            f"Привет, {html.bold(message.from_user.full_name)}!",
            reply_markup=main_kb(message.from_user.id),
        )


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        if message.from_user.id in allowed_ids:
            msg = message.text.lower()
            if msg == "получить последнее":
                data = get_data_file()
                output = user_friendly_data(data)
                await message.answer(
                    f"{output}", reply_to_message_id=message.message_id
                )
            elif "изменить интервал" in msg and message.from_user.id in admins:
                try:
                    splitted_msg = msg.split()
                    logging.info(dp["job"])
                    if len(splitted_msg) == 3:
                        interval = await change_interval(
                            dp["job"], int(splitted_msg[2])
                        )
                        await message.answer(
                            f"Установлен интервал {interval} мин",
                        )
                except Exception as e:
                    logging.critical(e)
            else:
                await message.answer(
                    "Воспользуйтесь кнопками снизу",
                    reply_markup=main_kb(message.from_user.id),
                )

    except Exception as e:
        logging.error(e)
        await message.reply("Something went wrong")


async def data_updater():
    if urls_mpei and ids_mpei:
        data_mpei = await get_places_mpei(urls_mpei, ids_mpei)
    if urls_mgsu and ids_mgsu:
        data_mgsu = await get_places_mgsu(urls_mgsu, ids_mgsu)
    data = {**data_mpei, **data_mgsu}
    update_data_file(data)


async def setup_scheduler():
    scheduler = AsyncIOScheduler()

    job = scheduler.add_job(data_updater, "interval", minutes=0.5)
    scheduler.start()
    return job


async def change_interval(job, interval):
    interval = max(0.5, interval)
    job.reschedule("interval", minutes=interval)
    job.modify(next_run_time=datetime.datetime.now())
    return interval


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    job = await setup_scheduler()
    dp["job"] = job
    job.modify(next_run_time=datetime.datetime.now())

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("my.log", encoding="UTF-8"),
            logging.StreamHandler(),
        ],
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(e)

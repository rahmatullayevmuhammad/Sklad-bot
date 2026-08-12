import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = "8483261510:AAEsrtBw6kct2R-8khMCVM1G2VGHq664UrE"

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📦 Ombor Botga xush kelibsiz!\n\n"
        "Bot muvaffaqiyatli ishga tushdi."
    )


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=TOKEN)

    print("✅ Ombor Bot ishga tushdi!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
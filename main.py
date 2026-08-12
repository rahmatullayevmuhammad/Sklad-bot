import asyncio
import logging

from aiogram import Bot, Dispatcher, F
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


# Fallback handler for any other text messages
@dp.message(F.text)
async def unknown_message(message: Message):
    await message.answer("Noma'lum buyruq. Iltimos, /start bosing.")


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=TOKEN)

    print("✅ Ombor Bot ishga tushdi!")

    # Pass allowed_updates to ignore non-message updates (like chat_member, channel_post, etc.)
    await dp.start_polling(bot, allowed_updates=["message"])


if __name__ == "__main__":
    asyncio.run(main())

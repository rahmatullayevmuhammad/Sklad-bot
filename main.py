import asyncio
import logging
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Tokenni Render Environment Variable (Atrof-muhit o'zgaruvchilaridan) oladi
# Agar topilmasa, zaxira sifatida token ishlatiladi
TOKEN = os.getenv("BOT_TOKEN", "8483261510:AAEsrtBw6kct2R-8khMCVM1G2VGHq664UrE")

# =========================
# DATABASE
# =========================

db = sqlite3.connect("ombor.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
)
""")

db.commit()

# =========================
# BOT
# =========================

dp = Dispatcher()


class States(StatesGroup):
    add_products = State()
    search = State()
    sale = State()
    income = State()


# =========================
# MENU
# =========================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Mahsulot qo‘shish"),
            KeyboardButton(text="🔎 Kod orqali qidirish")
        ],
        [
            KeyboardButton(text="🛒 Sotuv"),
            KeyboardButton(text="📥 Kirim")
        ],
        [
            KeyboardButton(text="📦 Sklad qoldig‘i")
        ]
    ],
    resize_keyboard=True
)


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📦 Ombor Botga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=menu
    )


# =========================
# MAHSULOT QO‘SHISH
# =========================

@dp.message(F.text == "➕ Mahsulot qo‘shish")
async def add_start(message: Message, state: FSMContext):
    await state.set_state(States.add_products)
    await message.answer(
        "📦 Mahsulotlarni bitta xabarda yuboring.\n\n"
        "Format:\n"
        "KOD | NOMI | SONI\n\n"
        "Masalan:\n\n"
        "1001 | Coca Cola 1.5L | 50\n"
        "1002 | Fanta 1.5L | 30\n"
        "1003 | Sprite 1.5L | 45\n\n"
        "💡 100 ta yoki 1000 ta mahsulotni ham bitta xabarda yuborishingiz mumkin."
    )


@dp.message(States.add_products)
async def add_products(message: Message, state: FSMContext):
    lines = message.text.strip().splitlines()

    added = 0
    duplicate = 0
    errors = 0

    for line in lines:
        if not line.strip():
            continue

        parts = [x.strip() for x in line.split("|")]

        if len(parts) != 3:
            errors += 1
            continue

        code, name, quantity_text = parts

        try:
            quantity = int(quantity_text)
        except ValueError:
            errors += 1
            continue

        if quantity < 0:
            errors += 1
            continue

        try:
            cursor.execute(
                """
                INSERT INTO products (code, name, quantity)
                VALUES (?, ?, ?)
                """,
                (code, name, quantity)
            )
            added += 1
        except sqlite3.IntegrityError:
            duplicate += 1

    db.commit()
    await state.clear()

    await message.answer(
        "✅ Mahsulot kiritish tugadi!\n\n"
        f"📦 Qo‘shildi: {added} ta\n"
        f"⚠️ Takroriy kod: {duplicate} ta\n"
        f"❌ Xato: {errors} ta",
        reply_markup=menu
    )


# =========================
# QIDIRISH
# =========================

@dp.message(F.text == "🔎 Kod orqali qidirish")
async def search_start(message: Message, state: FSMContext):
    await state.set_state(States.search)
    await message.answer(
        "🔎 Mahsulot kodini yuboring.\n\n"
        "Masalan: 1003"
    )


@dp.message(States.search)
async def search_product(message: Message, state: FSMContext):
    code = message.text.strip()

    cursor.execute(
        """
        SELECT code, name, quantity
        FROM products
        WHERE code = ?
        """,
        (code,)
    )

    product = cursor.fetchone()
    await state.clear()

    if not product:
        await message.answer(
            "❌ Mahsulot topilmadi.",
            reply_markup=menu
        )
        return

    code, name, quantity = product

    await message.answer(
        "📦 MAHSULOT\n\n"
        f"🔢 Kod: {code}\n"
        f"📝 Nomi: {name}\n"
        f"📊 Qoldiq: {quantity} dona",
        reply_markup=menu
    )


# =========================
# SOTUV
# =========================

@dp.message(F.text == "🛒 Sotuv")
async def sale_start(message: Message, state: FSMContext):
    await state.set_state(States.sale)
    await message.answer(
        "🛒 Sotilgan mahsulotni yuboring.\n\n"
        "Format:\n"
        "KOD | SONI\n\n"
        "Masalan:\n"
        "1003 | 5"
    )


@dp.message(States.sale)
async def sale_product(message: Message, state: FSMContext):
    parts = [x.strip() for x in message.text.split("|")]

    if len(parts) != 2:
        await message.answer(
            "❌ Format noto‘g‘ri.\n\n"
            "Masalan:\n"
            "1003 | 5"
        )
        return

    code, amount_text = parts

    try:
        amount = int(amount_text)
    except ValueError:
        await message.answer("❌ Soni raqam bo‘lishi kerak.")
        return

    if amount <= 0:
        await message.answer("❌ Soni 0 dan katta bo‘lishi kerak.")
        return

    cursor.execute(
        """
        SELECT name, quantity
        FROM products
        WHERE code = ?
        """,
        (code,)
    )

    product = cursor.fetchone()

    if not product:
        await message.answer("❌ Bunday kodli mahsulot topilmadi.")
        return

    name, old_quantity = product

    if amount > old_quantity:
        await message.answer(
            "❌ Omborda mahsulot yetarli emas!\n\n"
            f"📦 Mahsulot: {name}\n"
            f"📊 Omborda: {old_quantity} dona\n"
            f"🛒 Sotuv: {amount} dona"
        )
        return

    new_quantity = old_quantity - amount

    cursor.execute(
        """
        UPDATE products
        SET quantity = ?
        WHERE code = ?
        """,
        (new_quantity, code)
    )

    db.commit()
    await state.clear()

    await message.answer(
        "✅ SOTUV QABUL QILINDI\n\n"
        f"📦 Mahsulot: {name}\n"
        f"🔢 Kod: {code}\n"
        f"➖ Sotildi: {amount} dona\n"
        f"📊 Eski qoldiq: {old_quantity} dona\n"
        f"📦 Yangi qoldiq: {new_quantity} dona",
        reply_markup=menu
    )


# =========================
# KIRIM
# =========================

@dp.message(F.text == "📥 Kirim")
async def income_start(message: Message, state: FSMContext):
    await state.set_state(States.income)
    await message.answer(
        "📥 Omborga kelgan mahsulotni yuboring.\n\n"
        "Format:\n"
        "KOD | SONI\n\n"
        "Masalan:\n"
        "1003 | 20"
    )


@dp.message(States.income)
async def income_product(message: Message, state: FSMContext):
    parts = [x.strip() for x in message.text.split("|")]

    if len(parts) != 2:
        await message.answer(
            "❌ Format noto‘g‘ri.\n\n"
            "Masalan:\n"
            "1003 | 20"
        )
        return

    code, amount_text = parts

    try:
        amount = int(amount_text)
    except ValueError:
        await message.answer("❌ Soni raqam bo‘lishi kerak.")
        return

    if amount <= 0:
        await message.answer("❌ Soni 0 dan katta bo‘lishi kerak.")
        return

    cursor.execute(
        """
        SELECT name, quantity
        FROM products
        WHERE code = ?
        """,
        (code,)
    )

    product = cursor.fetchone()

    if not product:
        await message.answer("❌ Bunday kodli mahsulot topilmadi.")
        return

    name, old_quantity = product
    new_quantity = old_quantity + amount

    cursor.execute(
        """
        UPDATE products
        SET quantity = ?
        WHERE code = ?
        """,
        (new_quantity, code)
    )

    db.commit()
    await state.clear()

    await message.answer(
        "✅ KIRIM QABUL QILINDI\n\n"
        f"📦 Mahsulot: {name}\n"
        f"🔢 Kod: {code}\n"
        f"➕ Kelgan: {amount} dona\n"
        f"📊 Eski qoldiq: {old_quantity} dona\n"
        f"📦 Yangi qoldiq: {new_quantity} dona",
        reply_markup=menu
    )


# =========================
# SKLAD QOLDIG‘I
# =========================

@dp.message(F.text == "📦 Sklad qoldig‘i")
async def stock(message: Message):
    cursor.execute(
        """
        SELECT code, name, quantity
        FROM products
        ORDER BY id
        """
    )

    products = cursor.fetchall()

    if not products:
        await message.answer(
            "📦 Omborda mahsulot yo‘q.",
            reply_markup=menu
        )
        return

    text = "📦 SKLAD QOLDIG‘I\n\n"

    for code, name, quantity in products:
        text += f"{code} | {name} | {quantity} dona\n"

    await message.answer(
        text,
        reply_markup=menu
    )


# =========================
# ISHGA TUSHIRISH
# =========================

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    print("✅ Ombor Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

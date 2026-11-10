# -*- coding: utf-8 -*-

code = """import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from keyboards import get_yes_no_inline, get_banks_inline
from offers import get_all_offers, get_available_offers, format_offers_list

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = [int(x.strip()) for x in os.getenv("OWNER_ID").split(",")]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class Form(StatesGroup):
    waiting_for_earnings = State()
    waiting_for_age = State()
    waiting_for_ip = State()
    waiting_for_banks = State()
    waiting_for_city = State()


BANKS_MAP = {
    "bank_alfa": "Альфа Банк",
    "bank_t": "Т Банк",
    "bank_sber": "Сбербанк",
    "bank_vtb": "ВТБ Банк",
    "bank_psb": "ПСБ",
    "bank_ozon": "Озон банк"
}


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Готов ли ты заработать от 2.000₽ до 6.500₽ за один банковский продукт?",
        reply_markup=get_yes_no_inline()
    )
    await state.set_state(Form.waiting_for_earnings)


@dp.callback_query(Form.waiting_for_earnings, F.data.in_(["yes", "no"]))
async def process_earnings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    answer = "Да" if callback.data == "yes" else "Нет"
    await state.update_data(earnings_ready=answer)
    await callback.message.edit_text("Сколько тебе лет? (введи число)")
    await state.set_state(Form.waiting_for_age)


@dp.message(Form.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 18:
            await message.answer("К сожалению, ты нам не подходишь. Наш сервис доступен только с 18 лет.")
            await state.clear()
            return
        await state.update_data(age=age)
        await message.answer(
            "Есть ли у тебя открытое ИП?",
            reply_markup=get_yes_no_inline()
        )
        await state.set_state(Form.waiting_for_ip)
    except ValueError:
        await message.answer("Пожалуйста, введи число (возраст).")


@dp.callback_query(Form.waiting_for_ip, F.data.in_(["yes", "no"]))
async def process_ip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    answer = "Да" if callback.data == "yes" else "Нет"
    await state.update_data(has_ip=answer)
    if answer == "Да":
        await callback.message.edit_text(
            "🏦 В каких банках у тебя есть Расчётные Счета?\\nВыбери все подходящие варианты и нажми '✅ Всё, закончил выбор'.",
            reply_markup=get_banks_inline()
        )
        await state.update_data(selected_banks=[])
        await state.set_state(Form.waiting_for_banks)
    else:
        await state.update_data(selected_banks="Нет ИП")
        await callback.message.edit_text("📍 С какого ты города? (введи название)")
        await state.set_state(Form.waiting_for_city)


@dp.callback_query(Form.waiting_for_banks)
async def process_banks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    selected_banks = data.get("selected_banks", [])
    if callback.data == "banks_done":
        if not selected_banks:
            await callback.message.edit_text(
                "⚠️ Пожалуйста, выбери хотя бы один банк.",
                reply_markup=get_banks_inline()
            )
            return
        await state.update_data(selected_banks=selected_banks)
        await callback.message.edit_text("📍 С какого ты города? (введи название)")
        await state.set_state(Form.waiting_for_city)
    elif callback.data in BANKS_MAP:
        bank_name = BANKS_MAP[callback.data]
        if bank_name not in selected_banks:
            selected_banks.append(bank_name)
            await state.update_data(selected_banks=selected_banks)
            banks_list = ", ".join(selected_banks)
            await callback.message.edit_text(
                f"✅ Добавил: {bank_name}\\n\\n📋 Выбранные банки: {banks_list}\\n\\nВыбери еще банки или нажми '✅ Всё, закончил выбор'.",
                reply_markup=get_banks_inline()
            )
        else:
            await callback.message.edit_text(
                f"⚠️ '{bank_name}' уже выбран.\\n\\n📋 Выбранные банки: {', '.join(selected_banks)}\\n\\nВыбери другой банк или нажми '✅ Всё, закончил выбор'.",
                reply_markup=get_banks_inline()
            )


@dp.message(Form.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if not city:
        await message.answer("⚠️ Пожалуйста, введи название города.")
        return

    await state.update_data(city=city)
    data = await state.get_data()

    if data["selected_banks"] == "Нет ИП":
        available_offers = get_all_offers()
    else:
        available_offers = get_available_offers(data["selected_banks"])

    offers_text = format_offers_list(available_offers)
    offers_count = len(available_offers)

    username = message.from_user.username or "Не указан"
    user_id = message.from_user.id
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if data["selected_banks"] == "Нет ИП":
        banks_text = "Нет ИП (доступны ВСЕ офферы)"
    else:
        banks_text = ", ".join(data["selected_banks"])

    application_text = (
        f"🔔 НОВАЯ ЗАЯВКА\\n\\n"
        f"👤 Пользователь: @{username}\\n"
        f"🆔 ID: {user_id}\\n"
        f"🕐 Время: {timestamp}\\n\\n"
        f"📋 Ответы:\\n"
        f"• Готов заработать 2000-6500₽: {data['earnings_ready']}\\n"
        f"• Возраст: {data['age']}\\n"
        f"• Есть ИП: {data['has_ip']}\\n"
        f"• Банки с РКО: {banks_text}\\n"
        f"• Город: {data['city']}\\n\\n"
        f"{offers_text}"
    )

    for owner_id in OWNER_IDS:
        try:
            await bot.send_message(chat_id=owner_id, text=application_text)
        except Exception as e:
            logging.error(f"Ошибка отправки заявки владельцу {owner_id}: {e}")

    await message.answer(
        f"✅ Спасибо! Твоя заявка принята.\\n\\n"
        f"📊 Тебе доступно офферов: {offers_count} шт.\\n\\n"
        f"Мы свяжемся с тобой в ближайшее время для оформления."
    )

    await state.clear()


async def main():
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
"""

with open("bot.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("✅ Готово! bot.py создан с правильными отступами.")
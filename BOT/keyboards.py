from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_yes_no_inline():
    """Кнопки Да/Нет"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no")
        ]
    ])
    return keyboard

def get_banks_inline():
    """Кнопки выбора банков"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏦 Альфа Банк", callback_data="bank_alfa")],
        [InlineKeyboardButton(text="🏦 Т Банк", callback_data="bank_t")],
        [InlineKeyboardButton(text="🏦 Сбербанк", callback_data="bank_sber")],
        [InlineKeyboardButton(text="🏦 ВТБ Банк", callback_data="bank_vtb")],
        [InlineKeyboardButton(text="🏦 ПСБ", callback_data="bank_psb")],
        [InlineKeyboardButton(text="🏦 Озон банк", callback_data="bank_ozon")],
	[InlineKeyboardButton(text="🏦 УралСиб", callback_data="bank_uralsib")],
	[InlineKeyboardButton(text="🏦 Точка Банк", callback_data="bank_tochka")],
        [InlineKeyboardButton(text="✅ Всё, закончил выбор", callback_data="banks_done")]
    ])
    return keyboard
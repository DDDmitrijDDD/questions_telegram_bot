from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt
from utils.db.api.user import DBuser
from utils.system.adminka import AdminIs


@rt.message(F.text == 'Статистика', AdminIs())
async def category(message: Message):
    text = ""
    try:
        question = await DBuser.return_all_questions()
        summa = sum(await DBuser.return_questions_popularity())
        a = 0
        for i in question:
            category = await DBuser.return_category_by_id(i[1])
            if a == 0:
                text += f"{category} -> {i[0]} -> {round(i[2] / summa * 100, 2)}%"
            else:
                text += f"\n{category} -> {i[0]} -> {round(i[2] / summa * 100, 2)}%"
            a += 1
        await message.answer(f"{text}")
    except:
        await message.answer(f"Статистики нету")
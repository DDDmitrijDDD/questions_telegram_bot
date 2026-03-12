from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt, bot
from utils.db.api.user import DBuser
from utils.system.employee import Employee
from utils.system.inline_btns import create_markup


@rt.message(F.text == 'Завершить', Employee())
async def complete(message: Message):
    user_id = await DBuser.return_employee_user_id(message.from_user.id)
    await DBuser.update_employee_user_null(message.from_user.id)
    await DBuser.update_user_employee_null(user_id)
    markup = await create_markup('reply', [[["Категории"]]])
    await bot.send_message(user_id, text="Сотрудник завершил с вами связь", reply_markup=markup)
    markup = await create_markup('reply', [[["Изменить статус"]]])
    await message.answer(f"Вы завершили связь с пользователем", reply_markup=markup)


@rt.message(Employee())
async def call_emp(message: Message):
    try:
        user_id = await DBuser.return_employee_user_id(message.from_user.id)
        if user_id != 0:
            await bot.send_message(user_id, text=f"{message.text}")
    except:
        await message.answer(f"Ошибка")

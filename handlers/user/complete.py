from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt, bot
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup


@rt.message(F.text == 'Завершить')
async def complete(message: Message):
    emp_id = await DBuser.return_user_employee_id(message.from_user.id)
    await DBuser.update_employee_user_null(emp_id)
    await DBuser.update_user_employee_null(message.from_user.id)
    markup = await create_markup('reply', [[["Изменить статус"]]])
    await bot.send_message(emp_id, text="Пользователь завершил с вами связь", reply_markup=markup)
    markup = await create_markup('reply', [[["Категории"]]])
    await DBuser.del_history(message.from_user.id)
    await message.answer(f"Вы завершили связь с сотрудником", reply_markup=markup)


@rt.message()
async def call_emp(message: Message):
    try:
        emp_id = await DBuser.return_user_employee_id(message.from_user.id)
        if emp_id != 0:
            await bot.send_message(emp_id, text=f"{message.text}")
    except:
        await message.answer(f"Ошибка")

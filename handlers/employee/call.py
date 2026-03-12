from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt, bot
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup


@rt.callback_query(lambda c: c.data and c.data.startswith('call_accept_'))
async def call_accept_(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split("_")[2]
    markup = await create_markup('reply', [[["Завершить"]]])
    await DBuser.update_user_employee(user_id, call.from_user.id)
    await DBuser.update_employee_user(user_id, call.from_user.id)
    await call.message.answer(f"Вы приняли вызов. Все следующие сообщения отправятся пользователю", reply_markup=markup)
    await bot.send_message(user_id, text="Сотрудник с вами связался, все следующие сообщения отправятся сотруднику", reply_markup=markup)
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt
from utils.db.api.user import DBuser
from utils.system.employee import Employee


@rt.message(F.text == 'Изменить статус', Employee())
async def category(message: Message):
    markup = InlineKeyboardBuilder()
    status = await DBuser.return_employee_status(message.from_user.id)
    if status == 1:
        markup.row(InlineKeyboardButton(text="Офлайн", callback_data="status_offline", style="danger"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
        await message.answer("Ваш статус <b>Онлайн</b>", reply_markup=markup.as_markup())
    else:
        markup.row(InlineKeyboardButton(text="Онлайн", callback_data="status_online", style="success"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
        await message.answer("Ваш статус <b>Офлайн</b>", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'status_offline')
async def status_offline(call: CallbackQuery):
    await DBuser.update_employee_status(call.from_user.id, 0)
    await call.message.answer(f"Ваш статус изменен на <b>Офлайн</b>")


@rt.callback_query(F.data == 'status_online')
async def status_online(call: CallbackQuery):
    await DBuser.update_employee_status(call.from_user.id, 1)
    await call.message.answer(f"Ваш статус изменен на <b>Онлайн</b>")
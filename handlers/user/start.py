from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.loader import rt, bot
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup


async def del_mes(chat: int, id_: int) -> None:
    """
    удаляет сообщение
    :param chat: id чата
    :param id_: id сообщения
    """
    try: await bot.delete_message(chat, id_)
    except Exception: ...


class UserState(StatesGroup):
    pass


@rt.message(CommandStart())
async def start_message(message: Message, state: FSMContext):
    """Проверка есть ли пользователь в БД"""
    markup = await create_markup('reply', [[["Категории"]]])
    all_user = await DBuser.all_user_id()
    if message.from_user.id not in all_user:
        await DBuser.add_new_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>.", reply_markup=markup)
    else:
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>.", reply_markup=markup)


@rt.callback_query(F.data == 'cancel')
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    await del_mes(call.from_user.id, call.message.message_id)
    await state.clear()



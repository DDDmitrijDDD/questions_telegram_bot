from aiogram import F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message, CallbackQuery
from data.loader import rt, bot
from utils.system.inline_btns import create_markup
from utils.system.adminka import AdminIs


class AdminState(StatesGroup):
    add_category = State()
    add_question = State()
    add_answer = State()
    add_question_more = State()
    add_answer_more = State()
    answer_update = State()
    add_answer_new = State()
    add_employee = State()


async def del_mes(chat: int, id_: int) -> None:
    """
    удаляет сообщение
    :param chat: id чата
    :param id_: id сообщения
    """
    try: await bot.delete_message(chat, id_)
    except Exception:
        ...


@rt.message(CommandStart(), AdminIs(), StateFilter(default_state))
async def command_start(message: Message, state: FSMContext):
    await del_mes(message.from_user.id, message.message_id)
    await state.clear()
    markup = await create_markup('reply', [[["Категории"], ["Сотрудники"]],
                                                       [["Статистика"]]])
    await message.answer(f"Ты админ", reply_markup=markup)


@rt.callback_query(AdminIs(), F.data == 'cancel')
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    await del_mes(call.from_user.id, call.message.message_id)
    await state.clear()


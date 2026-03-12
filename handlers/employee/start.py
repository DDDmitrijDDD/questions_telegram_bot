from aiogram import F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message, CallbackQuery
from data.loader import rt, bot
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup
from utils.system.employee import Employee


class EmployeeState(StatesGroup):
    pass


async def del_mes(chat: int, id_: int) -> None:
    """
    удаляет сообщение
    :param chat: id чата
    :param id_: id сообщения
    """
    try: await bot.delete_message(chat, id_)
    except Exception:
        ...


@rt.message(CommandStart(), Employee(), StateFilter(default_state))
async def command_start(message: Message, state: FSMContext):
    await del_mes(message.from_user.id, message.message_id)
    await state.clear()
    markup = await create_markup('reply', [[["Изменить статус"]]])
    category = await DBuser.return_employee_category_one(message.from_user.id)
    if category == None or category == "":
        await message.answer(f"У вас нету категории. Как только ее добавят, вам придет уведомление", reply_markup=markup)
    else:
        await message.answer(f"Ваша категория: <b>{category}</b>",
                             reply_markup=markup)


@rt.callback_query(Employee(), F.data == 'cancel')
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    await del_mes(call.from_user.id, call.message.message_id)
    await state.clear()


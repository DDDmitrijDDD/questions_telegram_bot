from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt, bot
from handlers.admin.start import AdminState
from utils.db.api.user import DBuser, session
from utils.system.adminka import AdminIs


@rt.message(F.text == 'Сотрудники', AdminIs())
async def employees(message: Message):
    markup = InlineKeyboardBuilder()
    employee = await DBuser.return_employee_name()
    if not employee:
        markup.row(InlineKeyboardButton(text="Добавить Сотрудника", callback_data="add_employee"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await message.answer(f"Сотрудников нету, добавьте их", reply_markup=markup.as_markup())
    else:
        for i in employee:
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"employee_{i}"))
        markup.row(InlineKeyboardButton(text="Добавить сотрудника", callback_data="add_employee"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await message.answer("Выберите действие", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'employees')
async def employees_back(call: CallbackQuery):
    markup = InlineKeyboardBuilder()
    employee = await DBuser.return_employee_name()
    if not employee:
        markup.row(InlineKeyboardButton(text="Добавить Сотрудника", callback_data="add_employee"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await call.message.answer(f"Сотрудников нету, добавьте их", reply_markup=markup.as_markup())
    else:
        for i in employee:
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"employee_{i}"))
        markup.row(InlineKeyboardButton(text="Добавить сотрудника", callback_data="add_employee"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await call.message.answer("Выберите действие", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'add_employee')
async def add_employee(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
    await call.message.answer(f"Введите username сотрудника", reply_markup=markup.as_markup())
    await state.set_state(AdminState.add_employee)


@rt.message(AdminState.add_employee)
async def add_employee_state(message: Message, state: FSMContext):
    name = message.text
    if name[0] == "@":
        name = name[1::]
    markup = InlineKeyboardBuilder()
    try:
        user = await DBuser.return_user_by_username(name)
        await state.update_data(user_id=user[0], username=user[1], fullname=user[2], ids=user[3])
        try:
            category = await DBuser.return_category()
            if not category:
                await DBuser.add_employee_none_category(user[0], user[1], user[2], user[3])
                await message.answer(
                    f"Сотрудник добавлен, категорий не найдено, добавьте категорию и привяжите к ней сотрудника")
                await bot.send_message(user[0], text="Вы добавлены как сотрудник. Категория вам пока что не назначена")
                await state.clear()
            else:
                for i in category:
                    markup.row()
                    markup.row(InlineKeyboardButton(text=i, callback_data=f"and_category_employee_{i}"))
                markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
                await message.answer(f"Выберите категорию для сотрудника", reply_markup=markup.as_markup())
        except:
            pass
    except:
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await message.answer(f"Пользователь не найден, попробуйте ввести другой username",
                             reply_markup=markup.as_markup())
        await state.set_state(AdminState.add_employee)



@rt.callback_query(lambda c: c.data and c.data.startswith('and_category_employee_'))
async def and_category_employee_(call: CallbackQuery, state: FSMContext):
    category = call.data.split("_")[3]
    data = await state.get_data()
    await DBuser.add_employee(data["user_id"], data["username"], data["fullname"], category, data["ids"])
    await call.message.answer(f"Сотрудник добавлен")
    await bot.send_message(data["user_id"], text=f"Вы добавлены как сотрудник. Ваша категория <b>{category}</b>")
    await state.clear()


@rt.callback_query(lambda c: c.data and c.data.startswith('employee_'))
async def employee_(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    employee = call.data.split("_")[1]
    employee = await DBuser.return_employee_by_username(employee)
    category = employee[3]
    if category == None or category == "":
        category = "Нету"
        markup.row(InlineKeyboardButton(text="Добавить категорию", callback_data=f"update_category_for_employee"))
    else:
        markup.row(InlineKeyboardButton(text="Изменить категорию", callback_data=f"update_category_for_employee"))
    session = employee[4]
    if session == 0:
        session = "Не аквтивна"
    else:
        session = "Активна"
    status = employee[5]
    if status == 1:
        status = "Онлайн"
    else:
        status = "Офлайн"
    await state.update_data(employee_id=employee[0])
    markup.row(InlineKeyboardButton(text="Удалить сотрудника", callback_data=f"delete_employee"))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=f"employees"))
    await call.message.answer(f"""Сотрудник: {employee[1]}
Полное имя: {employee[2]}
Категория: {category}
Сессия: {session}
Статус: {status}""", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'delete_employee')
async def delete_employee(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await DBuser.del_employee(data["employee_id"])
    await call.message.answer(f"Сотрудник удален")
    await state.clear()


@rt.callback_query(F.data == 'update_category_for_employee')
async def update_category_for_employee(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    category = await DBuser.return_category()
    if not category:
        await call.message.answer(
            f"Категорий не найдено, добавьте категорию и привяжите к ней сотрудника")
        await state.clear()
    else:
        for i in category:
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"update_category_{i}"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await call.message.answer(f"Выберите категорию для сотрудника", reply_markup=markup.as_markup())


@rt.callback_query(lambda c: c.data and c.data.startswith('update_category_'))
async def update_category_(call: CallbackQuery, state: FSMContext):
    category = call.data.split("_")[2]
    data = await state.get_data()
    await DBuser.update_category_for_employee(data["employee_id"], category)
    await call.message.answer(f"Категория изменена")
    await bot.send_message(data["employee_id"], text=f"У вас новая категория <b>{category}</b>")
    await state.clear()


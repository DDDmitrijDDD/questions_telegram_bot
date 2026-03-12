from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt, bot
from utils.db.api.user import DBuser


@rt.message(F.text == 'Категории')
async def category(message: Message):
    markup = InlineKeyboardBuilder()
    if not await DBuser.return_category():
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>.")
    else:
        for i in await DBuser.return_category():
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"user_category_{i}"))
        await message.answer("Выберите категорию", reply_markup=markup.as_markup())


@rt.callback_query(lambda c: c.data and c.data.startswith('user_category_'))
async def user_category_(call: CallbackQuery, state: FSMContext):
    category = call.data.split("_")[2]
    category_id = await DBuser.return_category_id(category)
    questions = await DBuser.return_questions(category_id)
    markup = InlineKeyboardBuilder()
    await state.update_data(category=category)
    if not questions:
        markup.row(InlineKeyboardButton(text="Назад", callback_data=f"user_category_start"))
        await call.message.answer("Вопросов к данной категории нету")
    else:
        for i in questions:
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"user_questions_{i}"))
        markup.row(InlineKeyboardButton(text="Назад", callback_data=f"user_start_category"))
        await call.message.answer(f"Выберите вопрос", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'user_start_category')
async def user_start_category(call: CallbackQuery):
    markup = InlineKeyboardBuilder()
    if not await DBuser.return_category():
        await call.message.answer(f"Привет, <b>{call.from_user.full_name}</b>.")
    else:
        for i in await DBuser.return_category():
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"user_category_{i}"))
        await call.message.answer("Выберите категорию", reply_markup=markup.as_markup())


@rt.callback_query(lambda c: c.data and c.data.startswith('user_questions_'))
async def user_questions_(call: CallbackQuery, state: FSMContext):
    question = call.data.split("_")[2]
    question_id = await DBuser.return_question_id(question)
    await DBuser.update_question_popular(question)
    data = await state.get_data()
    try:
        answer = await DBuser.return_answer(question_id)
    except:
        answer = []
    markup = InlineKeyboardBuilder()
    if not answer:
        text = "У данного вопроса нету ответа"
    else:
        text = f"Ответ: <b>{answer[1]}</b>"
        await state.update_data(answer_id=answer[0])
    questions = await DBuser.return_questions_on_question(question_id)
    if not questions:
        markup.row(InlineKeyboardButton(text="Связаться с сотрудником", callback_data=f"contact_user"))
    for i in questions:
        markup.row()
        markup.row(InlineKeyboardButton(text=i, callback_data=f"user_questions_{i}"))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=f"user_category_{data['category']}"))
    await call.message.answer(f"""Вопрос: {question}

{text}""", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'contact_user')
async def contact_user(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    data = await state.get_data()
    try:
        employee = await DBuser.return_employee_by_category(data["category"])
        if not employee:
            await call.message.answer(f"Все сотрудники сейчас заняты, либо находятся в оффлайне, попробуйте позже")
            await state.clear()
        else:
            await call.message.answer("Связываем вас с сотрудником. Ожидайте ответа")
            markup.row(InlineKeyboardButton(text="Связаться", callback_data=f"call_accept_{call.from_user.id}", style="success"))
            await bot.send_message(employee, text=f"Пользователь {call.from_user.full_name} хочет связаться с сотрудником", reply_markup=markup.as_markup())
    except:
        await call.message.answer(f"Все сотрудники сейчас заняты, либо находятся в оффлайне, попробуйте позже")
        await state.clear()

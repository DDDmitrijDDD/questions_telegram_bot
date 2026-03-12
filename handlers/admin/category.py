from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import rt
from handlers.admin.start import AdminState
from utils.db.api.user import DBuser
from utils.system.adminka import AdminIs


@rt.message(F.text == 'Категории', AdminIs())
async def category(message: Message):
    markup = InlineKeyboardBuilder()
    if not await DBuser.return_category():
        markup.row(InlineKeyboardButton(text="Добавить категорию", callback_data="category_add"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await message.answer("Категорий нету", reply_markup=markup.as_markup())
    else:
        for i in await DBuser.return_category():
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"category_{i}"))
        markup.row(InlineKeyboardButton(text="Добавить категорию", callback_data="category_add"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await message.answer("Выберите действие", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'category_start')
async def category(call: CallbackQuery):
    markup = InlineKeyboardBuilder()
    if not await DBuser.return_category():
        markup.row(InlineKeyboardButton(text="Добавить категорию", callback_data="category_add"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await call.message.answer("Категорий нету", reply_markup=markup.as_markup())
    else:
        for i in await DBuser.return_category():
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"category_{i}"))
        markup.row(InlineKeyboardButton(text="Добавить категорию", callback_data="category_add"))
        markup.row(InlineKeyboardButton(text="Отмена", callback_data="cancel", style="danger"))
        await call.message.answer("Выберите действие", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'category_add')
async def add_category(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Назад", callback_data=f"category_start"))
    await call.message.answer("Введите название категории")
    await state.set_state(AdminState.add_category)


@rt.message(AdminState.add_category)
async def add_category_state(message: Message, state: FSMContext):
    await DBuser.add_category(message.text)
    await message.answer("Категория добавлена")
    await state.clear()


@rt.callback_query(lambda c: c.data and c.data.startswith('category_'))
async def add_category(call: CallbackQuery, state: FSMContext):
    category = call.data.split("_")[1]
    category_id = await DBuser.return_category_id(category)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Вопросы", callback_data=f"questions_{category_id}"),
               InlineKeyboardButton(text="Удалить", callback_data=f"delete_category", style="danger"))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=f"category_start"))
    await call.message.answer(f"Категория: {category}", reply_markup=markup.as_markup())
    await state.update_data(category=category, category_id=category_id)


@rt.callback_query(F.data == 'delete_category')
async def delete_category(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await DBuser.del_categoty(data["category"])
    employees = await DBuser.return_employee_category()
    for i in employees:
        if str(i) == str(data["category"]):
            index = employees.index(i)
            await DBuser.delete_category_for_employee(employees[index-1])
    await call.message.answer(f"Категория удалена")
    await state.clear()


@rt.callback_query(lambda c: c.data and c.data.startswith('questions_'))
async def questions(call: CallbackQuery, state: FSMContext):
    question_start = call.data.split("_")[1]
    await state.update_data(question_start=question_start)
    data = await state.get_data()
    questions = await DBuser.return_questions(data["category_id"])
    markup = InlineKeyboardBuilder()
    if not questions:
        markup.row(InlineKeyboardButton(text="Добавить Вопрос", callback_data="add_question"))
        markup.row(InlineKeyboardButton(text="Назад", callback_data=f"category_{data['category']}"))
        await call.message.answer("Вопросов к данной категории нету", reply_markup=markup.as_markup())
    else:
        for i in questions:
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"question_{i}"))
        markup.row(InlineKeyboardButton(text="Добавить Вопрос", callback_data="add_question"))
        markup.row(InlineKeyboardButton(text="Назад", callback_data=f"category_{data['category']}"))
        await call.message.answer(f"Выберите вопрос", reply_markup=markup.as_markup())


@rt.callback_query(lambda c: c.data and c.data.startswith('question_'))
async def question(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question = call.data.split("_")[1]
    question_id = await DBuser.return_question_id(question)
    try:
        answer = await DBuser.return_answer(question_id)
    except:
        answer = []
    markup = InlineKeyboardBuilder()
    text2 = "После этого ответа, есть еще вопрос"
    if not answer:
        markup.row(InlineKeyboardButton(text="Добавить ответ", callback_data=f"answer_add"))
        text = "У данного вопроса нету ответа, добавьте его"
    else:
        markup.row(InlineKeyboardButton(text="Изменить ответ", callback_data=f"answer_update"))
        markup.add(InlineKeyboardButton(text="Добавить вопрос", callback_data=f"add_question_on_question"))
        text = f"Ответ: <b>{answer[1]}</b>"
        await state.update_data(answer_id=answer[0])
    if answer[2] == 0:
        questions = await DBuser.return_questions_on_question(question_id)
        if not questions:
            text2 = "После этого ответа нету вопроса и пользователь не может связаться с сотрудником"
        for i in questions:
            markup.row()
            markup.row(InlineKeyboardButton(text=i, callback_data=f"question_{i}"))
    else:
        text2 = "После этого ответа, пользователь может связаться с сотрудником"
    markup.row(InlineKeyboardButton(text="Удалить вопрос", callback_data=f"delete_question", style="danger"))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=f"questions_{data['question_start']}"))

    await state.update_data(question=question, question_id=question_id)
    await call.message.answer(f"""Вопрос: <b>{question}</b>

{text}

{text2}""", reply_markup=markup.as_markup())


@rt.callback_query(F.data == 'add_question_on_question')
async def add_question(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await DBuser.update_answer_redirection_nul(data["answer_id"])
    parent = data["question_id"]
    await state.update_data(parent=parent)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await call.message.answer("Введите вопрос")
    await state.set_state(AdminState.add_question)


@rt.callback_query(F.data == 'add_question')
async def add_question(call: CallbackQuery, state: FSMContext):
    await state.update_data(parent=0)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await call.message.answer("Введите вопрос")
    await state.set_state(AdminState.add_question)


@rt.message(AdminState.add_question)
async def add_question_state(message: Message, state: FSMContext):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await state.update_data(question=message.text)
    await message.answer(f"Введите ответ к вопросу", reply_markup=markup.as_markup())
    await state.set_state(AdminState.add_answer)


@rt.message(AdminState.add_answer)
async def add_answer_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await DBuser.add_question_answer(data["question"], data["category_id"], data["parent"], message.text)
    question_id = await DBuser.return_question_id(data["question"])
    answer_id = await DBuser.return_answer_id_in_question(message.text, question_id)
    await state.update_data(question_id=question_id, answer_id=answer_id)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Перевод на сотрудника", callback_data="translation"))
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await message.answer("Вопрос с ответом созданы. Введите еще вопрос к ответу, либо переводите на сотрудника", reply_markup=markup.as_markup())
    await state.set_state(AdminState.add_question_more)


@rt.message(AdminState.add_question_more)
async def add_question_more_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await DBuser.add_question(message.text, data["category_id"], data["question_id"])
    question_id = await DBuser.return_question_id(message.text)
    await state.update_data(question_id=question_id)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await message.answer("Вопрос создан. Введите ответ",
                         reply_markup=markup.as_markup())
    await state.set_state(AdminState.add_answer_more)


@rt.message(AdminState.add_answer_more)
async def add_question_more_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await DBuser.add_answer(message.text, data["question_id"])
    answer_id = await DBuser.return_answer_id_in_question(message.text, data["question_id"])
    await state.update_data(answer_id=answer_id)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Перевод на сотрудника", callback_data="translation"))
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await message.answer("Ответ создан. Введите еще вопрос к ответу, либо переводите на сотрудника",
                         reply_markup=markup.as_markup())
    await state.set_state(AdminState.add_question_more)


@rt.callback_query(F.data == 'translation', AdminState.add_question_more)
async def translation(call: CallbackQuery, state: FSMContext):
    data = await state.update_data()
    await DBuser.update_answer_redirection(data["answer_id"])
    await call.message.answer(f"После этого ответа, пользователь может связаться с сотрудником")
    await state.clear()


@rt.callback_query(F.data == 'delete_question')
async def delete_question(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await DBuser.del_question(data["question_id"])
    await call.message.answer("Вопрос удален")


@rt.callback_query(F.data == 'answer_add')
async def answer_update(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await call.message.answer("Введите ответ",
                         reply_markup=markup.as_markup())
    await state.set_state(AdminState.add_answer_new)


@rt.message(AdminState.add_answer_new)
async def answer_update_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await DBuser.add_answer(message.text, data["question_id"])
    await message.answer(f"Ответ добавлен")
    await state.clear()


@rt.callback_query(F.data == 'answer_update')
async def answer_update(call: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="Перевод на сотрудника", callback_data="translation"))
    markup.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel", style="danger"))
    await call.message.answer("Введите ответ или переведите на сотрудника",
                         reply_markup=markup.as_markup())
    await state.set_state(AdminState.answer_update)


@rt.message(AdminState.answer_update)
async def answer_update_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await DBuser.update_answer(data["answer_id"], message.text)
    await message.answer(f"Ответ изменен")
    await state.clear()


@rt.callback_query(F.data == 'translation', AdminState.answer_update)
async def translation(call: CallbackQuery, state: FSMContext):
    data = await state.update_data()
    await DBuser.update_answer_redirection(data["answer_id"])
    await call.message.answer(f"После этого ответа, пользователь может связаться с сотрудником")
    await state.clear()
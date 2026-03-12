import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
engine = create_engine(f"sqlite:///utils/db/files/user.db")
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_name = Column(String)
    full_name = Column(String)
    employee = Column(Integer, default=0)
    employee_rel = relationship("Employee", back_populates="user_rel", cascade="all, delete")


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user_id = Column(Integer)
    user_name = Column(String)
    full_name = Column(String)
    category = Column(Integer)
    session = Column(Integer, default=0)
    status = Column(Integer, default=1)
    user = Column(Integer, default=0)
    user_rel = relationship("User", back_populates="employee_rel")


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    questions = relationship("Question", back_populates="category_rel", cascade="all, delete")


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent = Column(Integer)
    category_id = Column(Integer, ForeignKey("category.id"))
    popularity = Column(Integer, default=0)
    category_rel = relationship("Category", back_populates="questions")
    answer = relationship("Answer", back_populates="question_rel", cascade="all, delete")

class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    redirection = Column(Integer, default=0)
    question_id = Column(Integer, ForeignKey("question.id"))
    question_rel = relationship("Question", back_populates="answer")


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer)
    user_id = Column(Integer)
    text = Column(String)


Base.metadata.create_all(engine)


class DBuser:
    @staticmethod
    async def all_user_id():
        users = session.query(User).all()
        users_id = []
        for user in users:
            users_id.append(user.user_id)
        return users_id

    @staticmethod
    async def add_new_user(user_id, user_name, full_name):
        user = User(user_id=user_id, user_name=user_name, full_name=full_name)
        session.add(user)
        session.commit()

    @staticmethod
    async def add_history(user_id, text):
        history = History(user_id=user_id, text=text)
        session.add(history)
        session.commit()

    @staticmethod
    async def add_category(name):
        category = Category(name=name)
        session.add(category)
        session.commit()

    @staticmethod
    async def add_question(name, ids, parent):
        question = Question(name=name, category_id=ids, parent=parent)
        session.add(question)
        session.commit()

    @staticmethod
    async def add_answer(name, ids):
        answers = Answer(name=name, question_id=ids)
        session.add(answers)
        session.commit()

    @staticmethod
    async def add_employee_none_category(user_id, name, name2, ids):
        user = Employee(user_id=user_id, user_name=name, full_name=name2, id=ids)
        session.add(user)
        session.commit()

    @staticmethod
    async def add_employee(user_id, name, name2, category, ids):
        user = Employee(user_id=user_id, user_name=name, full_name=name2, category=category, id=ids)
        session.add(user)
        session.commit()

    @staticmethod
    async def add_question_answer(name, ids, parent, name2):
        question = Question(name=name, category_id=ids, parent=parent)
        answers = Answer(name=name2)
        question.answer = [answers]
        session.add(question)
        session.commit()

    @staticmethod
    async def return_category():
        category_all = session.query(Category).all()
        categories = []
        for category in category_all:
            categories.append(category.name)
        return categories

    @staticmethod
    async def return_user_by_username(name):
        user = session.query(User).filter_by(user_name=name).first()
        return [user.user_id, user.user_name, user.full_name, user.id]

    @staticmethod
    async def return_employee_by_username(name):
        user = session.query(Employee).filter_by(user_name=name).first()
        return [user.user_id, user.user_name, user.full_name, user.category, user.session, user.status]

    @staticmethod
    async def return_employee_name():
        employee_all = session.query(Employee).all()
        employees = []
        for employee in employee_all:
            employees.append(employee.user_name)
        return employees

    @staticmethod
    async def return_employee_by_category(category):
        employee = session.query(Employee).filter_by(category=category, status=1, session=0).first()
        return employee.user_id

    @staticmethod
    async def return_history(ids):
        history = session.query(History).filter_by(user_id=ids).first()
        return history.text

    @staticmethod
    async def return_employee_category():
        employee_all = session.query(Employee).all()
        employees = []
        for employee in employee_all:
            employees.append(employee.user_id)
            employees.append(employee.category)
        return employees

    @staticmethod
    async def return_employee_id():
        employee_all = session.query(Employee).all()
        employees = []
        for employee in employee_all:
            employees.append(employee.user_id)
        return employees

    @staticmethod
    async def return_employee_status(ids):
        employee = session.query(Employee).filter_by(user_id=ids).first()
        return employee.status

    @staticmethod
    async def return_employee_category_one(ids):
        employee = session.query(Employee).filter_by(user_id=ids).first()
        return employee.category

    @staticmethod
    async def return_answer(ids):
        answer = session.query(Answer).filter_by(question_id=ids).first()
        return [answer.id, answer.name, answer.redirection]

    @staticmethod
    async def return_category_id(name):
        category = session.query(Category).filter_by(name=name).first()
        return category.id

    @staticmethod
    async def return_category_by_id(ids):
        category = session.query(Category).filter_by(id=ids).first()
        return category.name

    @staticmethod
    async def return_answer_id_in_question(name, ids):
        answer = session.query(Answer).filter_by(name=name, question_id=ids).first()
        return answer.id

    @staticmethod
    async def update_answer_redirection_nul(ids):
        answer = session.query(Answer).filter_by(id=ids).first()
        if answer:
            answer.redirection = 0
            session.commit()

    @staticmethod
    async def update_user_employee(user_id, employee_id):
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.employee = employee_id
            session.commit()

    @staticmethod
    async def update_question_popular(question):
        question = session.query(Question).filter_by(name=question).first()
        if question:
            question.popularity = question.popularity + 1
            session.commit()

    @staticmethod
    async def update_user_employee_null(user_id):
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.employee = 0
            session.commit()

    @staticmethod
    async def update_employee_user(user_id, employee_id):
        emp = session.query(Employee).filter_by(user_id=employee_id).first()
        if emp:
            emp.user = user_id
            session.commit()

    @staticmethod
    async def update_employee_user_null(employee_id):
        emp = session.query(Employee).filter_by(user_id=employee_id).first()
        if emp:
            emp.user = 0
            session.commit()

    @staticmethod
    async def update_employee_status(ids, status):
        emp = session.query(Employee).filter_by(user_id=ids).first()
        if emp:
            emp.status = status
            session.commit()

    @staticmethod
    async def update_answer_redirection(ids):
        answer = session.query(Answer).filter_by(id=ids).first()
        if answer:
            answer.redirection = 1
            session.commit()

    @staticmethod
    async def update_answer(ids, text):
        answer = session.query(Answer).filter_by(id=ids).first()
        if answer:
            answer.name = text
            session.commit()

    @staticmethod
    async def update_category_for_employee(ids, category):
        employee = session.query(Employee).filter_by(user_id=ids).first()
        if employee:
            employee.category = category
            session.commit()

    @staticmethod
    async def delete_category_for_employee(ids):
        employee = session.query(Employee).filter_by(user_id=ids).first()
        if employee:
            employee.category = ""
            session.commit()

    @staticmethod
    async def return_question_id(name):
        question = session.query(Question).filter_by(name=name).first()
        return question.id

    @staticmethod
    async def return_employee_user_id(ids):
        emp = session.query(Employee).filter_by(user_id=ids).first()
        return emp.user

    @staticmethod
    async def return_user_employee_id(ids):
        user = session.query(User).filter_by(user_id=ids).first()
        return user.employee

    @staticmethod
    async def return_questions(category):
        questions_all = session.query(Question).filter_by(category_id=category, parent=0).all()
        questions = []
        for question in questions_all:
            questions.append(question.name)
        return questions

    @staticmethod
    async def return_all_questions():
        questions_all = session.query(Question).all()
        questions = []
        for question in questions_all:
            questions.append([question.name, question.category_id, question.popularity])
        return questions

    @staticmethod
    async def return_questions_on_question(ids):
        questions_all = session.query(Question).filter_by(parent=ids).all()
        questions = []
        for question in questions_all:
            questions.append(question.name)
        return questions

    @staticmethod
    async def return_questions_popularity():
        questions_all = session.query(Question).all()
        questions = []
        for question in questions_all:
            questions.append(question.popularity)
        return questions

    @staticmethod
    async def del_categoty(name):
        category = session.query(Category).filter_by(name=name).first()
        if category:
            session.delete(category)
            session.commit()

    @staticmethod
    async def del_history(ids):
        history = session.query(History).filter_by(user_id=ids).first()
        if history:
            session.delete(history)
            session.commit()

    @staticmethod
    async def del_employee(ids):
        emp = session.query(Employee).filter_by(user_id=ids).first()
        if emp:
            session.delete(emp)
            session.commit()

    @staticmethod
    async def del_question(ids):
        question = session.query(Question).filter_by(id=ids).first()
        if question:
            session.delete(question)
            session.commit()
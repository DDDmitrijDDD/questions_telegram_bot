from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.config import admins_id
from utils.db.api.user import DBuser

class Employee(BaseFilter):
    """проверка на админ или нет"""
    async def __call__(self, message: Message) -> bool:
        employee = await DBuser.return_employee_id()
        if message.from_user.id in employee:
            return True
        return False

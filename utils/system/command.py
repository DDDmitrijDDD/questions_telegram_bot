from data.loader import Bot, dp
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Перезапустить бота'),
    ]
    await bot.set_my_commands(main_menu_commands)
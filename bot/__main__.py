import logging
import os
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import settings
from commands import register_user_commands, bot_commands, register_middleware


async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher(
        name='Main Dispatcher',
        db_url = settings.db_url.get_secret_value(), 
        db_apikey = settings.db_apikey.get_secret_value(),
    )
    
    commands_for_bot = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]
    await bot.set_my_commands(commands=commands_for_bot)
    
    register_middleware(router=dp)
    register_user_commands(router=dp)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, close_bot_session=True)
    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
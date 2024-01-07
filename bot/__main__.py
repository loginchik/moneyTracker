import logging
import os
import asyncio
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import settings
from commands import register_user_commands, bot_commands, register_middleware


webhook_path = f'/{settings.bot_token.get_secret_value()}'


async def on_startup(bot: Bot) -> None:
    webhook_uri = f'{settings.webhook_base_url.get_secret_value()}:{settings.webhook_server_port}{webhook_path}'
    await bot.set_webhook(webhook_uri, secret_token=settings.webhook_token.get_secret_value())
    
    commands_for_bot = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]
    await bot.set_my_commands(commands=commands_for_bot)


def main():
    dp = Dispatcher(
        name='Main Dispatcher',
        db_url = settings.db_url.get_secret_value(), 
        db_apikey = settings.db_apikey.get_secret_value(),
    )
    register_middleware(router=dp)
    register_user_commands(router=dp)
    
    dp.startup.register(on_startup)
    
    bot = Bot(token=settings.bot_token.get_secret_value())

    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp, 
        bot=bot, 
        secret_token=settings.webhook_token.get_secret_value()
    )
    webhook_requests_handler.register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    web.run_app(app=app, host='localhost', port=8080)

    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
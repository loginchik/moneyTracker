import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import settings

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, close_bot_session=True)
    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
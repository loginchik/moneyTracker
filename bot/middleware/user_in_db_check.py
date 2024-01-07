from typing import Any, Awaitable, Callable, Dict

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker


class UserInDBCheck(BaseMiddleware):  
    async def __call__(
        self, 
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], 
        event: Message | CallbackQuery, 
        data: Dict[str, Any]
        ) -> Any:
        
        user_id_to_check: int = event.from_user.id

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(f'http://127.0.0.1:8000/users/{user_id_to_check}/?apikey=apikey')
            
                if response.status == 404:
                    create_response = await session.post(f'http://127.0.0.1:8000/users/new/?user_id={user_id_to_check}&apikey=apikey')
                    if create_response.status == 201:
                        return await handler(event, data)
                    else:
                        raise ValueError('User is invalid')
                elif response.status == 200:
                    return await handler(event, data)
                else:
                    raise ClientConnectionError
        
        except ClientConnectionError:
            if isinstance(event, Message):
                await event.answer('Бот временно недоступен')
            elif isinstance(event, CallbackQuery):
                await event.message.answer('Бот временно недоступен')
from unittest.mock import AsyncMock
import pytest

from aiogram import Dispatcher, Bot, types
from aiogram.methods import SendMessage
from tests.extra_utils import get_update, get_message
from commands.start_command import start_message
from bot_inner_texts import load_message_texts_json


message_texts = load_message_texts_json()['basic']['start']


@pytest.mark.asyncio
async def test_start_message():
    message = AsyncMock()
    
    await start_message(message=message)
    
    message.answer.assert_called_with(message_texts['start_message'])
    
    
@pytest.mark.asyncio
async def test_start_command(dispatcher: Dispatcher, bot: Bot):
    result = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text='/start')))
    assert isinstance(result, SendMessage)
    assert result.text == message_texts['start_message']
    assert result.reply_markup is None
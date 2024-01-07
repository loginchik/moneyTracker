import asyncio
import pytest
import pytest_asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher
from .mocked_bot import MockedBot
from commands import register_user_commands


@pytest_asyncio.fixture(scope='function')
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()
        

@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    register_user_commands(dp)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()
        

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
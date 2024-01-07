import os
import logging
import datetime

import pytest
import pytest_asyncio

import asyncpg
from asyncpg.exceptions import DuplicateDatabaseError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from aiogram import Bot
from aiogram.types import User, Chat
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from tests.mocked_bot import MockedBot
from config import settings
from db.db_models import Base


TEST_HANDLERS_USER = User(
    id=111, 
    is_bot=False, 
    first_name='Sergey', 
    last_name='Ivanov',
    username=f'sivanov343434343434343434'
)

TEST_HANDLERS_USER_CHAT = Chat(
    id=111, 
    type='private', 
    username=TEST_HANDLERS_USER.username, 
    first_name=TEST_HANDLERS_USER.first_name,
    last_name=TEST_HANDLERS_USER.last_name
)

TEST_HANDLERS_BOT = MockedBot()


def pytest_configure(config):
    if not config.option.log_file:
        timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
        config.option.log_file = 'logs/pytest-log-' + timestamp + '.log'


def pytest_logger_config(logger_config):
    logger_config.add_loggers(['handler_tests', 'test_results_logger'], stdout_level='info')
    logger_config.set_log_option_default('handler_tests,test_results_logger') 
    
def pytest_logger_logdirlink(config):
    return os.path.abspath('bot/logs')


handlers_logger = logging.getLogger('handler_tests')


@pytest.fixture(scope='session')
def database_url():
    return settings.db_url.get_secret_value()


@pytest.fixture(scope='session')
def database_apikey():
    return settings.db_apikey.get_secret_value()


@pytest.fixture(scope='session')
def setup_user_chat():
    handlers_logger.info('Setting up user and chat')
    yield {
        'user': TEST_HANDLERS_USER, 
        'chat': TEST_HANDLERS_USER_CHAT
    }
    handlers_logger.info('Tearing down user and chat')
    
    
@pytest.fixture(scope='function')
def setup_state():
    temp_storage = MemoryStorage()
    state = FSMContext(
        storage=temp_storage, 
        key=StorageKey(
            bot_id=TEST_HANDLERS_BOT.id,
            chat_id=TEST_HANDLERS_USER_CHAT.id,
            user_id=TEST_HANDLERS_USER.id,
        )
    )
    handlers_logger.info('Preparing state')
    yield state
    handlers_logger.info('Tearing state down')
    

@pytest.fixture(scope='class')
def bot():
    return MockedBot()


async def connect_to_test_db() -> AsyncEngine:
    postgres_testdb_url: str = f'postgresql+asyncpg://{settings.db_user.get_secret_value()}:{settings.db_password.get_secret_value()}@{settings.db_host.get_secret_value()}:{settings.db_port}/test_application'
    async_engine: AsyncEngine = create_async_engine(url=postgres_testdb_url).execution_options(
        schema_translate_map={
            None: 'shared', 
            'public': None, 
            'user-specific': 'tenant', 
        }
    )
    return async_engine


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_session(request, event_loop) -> AsyncSession:
    postgres_server_url: str = f'postgresql://{settings.db_user.get_secret_value()}:{settings.db_password.get_secret_value()}@{settings.db_host.get_secret_value()}:{settings.db_port}/'
        
    # Connect to server to create test DB
    try:
        server_connection = await asyncpg.connect(postgres_server_url)
        await server_connection.execute(f"CREATE DATABASE test_application;")
        handlers_logger.info('Test DB is created')
    except DuplicateDatabaseError:
        handlers_logger.error('Test DB already exists')
    finally:
        await server_connection.close()
    
    # Connect to test DB to configure it
    async_engine: AsyncEngine = await connect_to_test_db()
    
    # Create DB schemas
    async with async_engine.begin() as connection:
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS shared;"))
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS tenant;"))
    handlers_logger.info('DB schemas are created')
    
    # Create session
    async_session: AsyncSession = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    
    def final():
        """Sync function that runs async event loop until it's complete. Basically, sync cover for async finalizer."""
        
        async def teardown():
            """Drops all tables in test DB and disposes the engine."""
            await async_engine.dispose()
            handlers_logger.info('Session is closed.')
            
            server_connection = await asyncpg.connect(postgres_server_url)
            await server_connection.execute(f'DROP DATABASE test_application WITH (FORCE)')
            await server_connection.close()
            handlers_logger.info('Database is deleted.')
        event_loop.run_until_complete(teardown())
        
    request.addfinalizer(final)
    return async_session


@pytest_asyncio.fixture(scope='function')
async def create_empty_tables_data(request, event_loop, setup_session):
    async_engine: AsyncEngine = await connect_to_test_db()
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    handlers_logger.info('Tables are created.')
    await async_engine.dispose()
    
    def final():
        async def delete_all_tables():
            async_engine = await connect_to_test_db()
            async with async_engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)
            await async_engine.dispose()
            handlers_logger.info('Tables are deleted')
            
        event_loop.run_until_complete(delete_all_tables())
    
    request.addfinalizer(final)
    return None
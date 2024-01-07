import logging

import asyncpg
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.db_base import establish_connection_with_db
from db.db_models import Base
from config import settings


@pytest_asyncio.fixture(scope='class')
async def get_asm(request, event_loop):
    db_name = 'test_application'
    engine, asm = await establish_connection_with_db(base_model=Base, special_db_name=db_name)
    
    logging.debug('ASM created')
    
    def teardown():
        async def delete_test_db():
            await engine.dispose()
            test_server_url = f'postgres://{settings.db_user.get_secret_value()}:{settings.db_password.get_secret_value()}@{settings.db_host.get_secret_value()}:{settings.db_port}/'
            conn = await asyncpg.connect(test_server_url)
            await conn.execute(f'DROP DATABASE {db_name} WITH (FORCE)')
            await conn.close()
            logging.debug('DB dropped')
        event_loop.run_until_complete(delete_test_db())
    
    request.addfinalizer(teardown)
    return asm
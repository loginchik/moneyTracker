import asyncio
import asyncpg
from asyncpg.exceptions import DuplicateDatabaseError

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from base import Database
from config import settings
from db_models import Base


async def create_db():
    user = settings.db_user.get_secret_value()
    password = settings.db_password.get_secret_value()
    host = settings.db_host.get_secret_value()
    port = settings.db_port
    db_name = settings.db_name.get_secret_value()

    server_url = f'postgres://{user}:{password}@{host}:{port}/'
    connection = await asyncpg.connect(server_url)
    try: 
        await connection.execute(f'CREATE DATABASE {db_name};')
    except DuplicateDatabaseError:
        pass
    
    db_url = server_url + db_name
    connection = await asyncpg.connect(dsn=db_url)
    await connection.execute('''CREATE SCHEMA IF NOT EXISTS shared;''')
    await connection.execute('''CREATE SCHEMA IF NOT EXISTS tenant;''')
    await connection.close()


async def create_all_tables(base_model: object = Base, engine: AsyncEngine = None):
    if not engine:
        raise ValueError('Create AsyncEngine first')
    
    async with engine.begin() as connection:
        await connection.run_sync(base_model.metadata.create_all)
    


class PostresDatabase(Database):
    
    async def setup(self) -> None:
        await create_db()
        async_engine = create_async_engine(
            settings.postgresql_url.get_secret_value(), 
            echo=True
        ).execution_options(
            schema_translate_map={None: 'shared', 'public': None, 'user-specific': 'tenant'}
            )    
        await create_all_tables(engine=async_engine, base_model=Base)

        self.async_session_maker = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
        self.async_engine = async_engine


    async def shutdown(self) -> None:
        await self.async_engine.dispose()
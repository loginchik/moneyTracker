import asyncpg
from asyncpg.exceptions import InvalidCatalogNameError

import pytest

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from db.db_base import create_db_and_schemas, make_async_engine, create_all_tables, create_async_session_maker
from db.db_models import Base
from config import settings


class Test_DBCreation:
    
    host = settings.db_host.get_secret_value()
    port = settings.db_port
    user = settings.db_user.get_secret_value()
    password = settings.db_password.get_secret_value()
    db_name = 'test_application'
    
    fake_test_db_url = f'postgres://{user}:{password}@{host}:{port}/nonexistentdb'
    test_db_url = f'postgres://{user}:{password}@{host}:{port}/{db_name}'
    test_server_url = f'postgres://{user}:{password}@{host}:{port}/'
    
    
    @pytest.mark.asyncio
    async def test_create_db_and_schemas(self):
        await create_db_and_schemas(host=self.host, port=self.port, user=self.user, password=self.password, db_name=self.db_name)

        with pytest.raises(InvalidCatalogNameError):
            assert await asyncpg.connect(self.fake_test_db_url)
        
        try: 
            connection = await asyncpg.connect(self.test_db_url)
            assert connection.is_closed() == False
        except InvalidCatalogNameError as e:
            pytest.fail(e)
        
        finally:
            await connection.close()
            
    @pytest.mark.asyncio 
    async def test_make_async_engine(self):
        created_engine = await make_async_engine(db_name=self.db_name)
        
        assert isinstance(created_engine, AsyncEngine)
        
        await created_engine.dispose()
        
    @pytest.mark.asyncio 
    async def test_create_all_tables(self):
        async_engine = await make_async_engine(db_name=self.db_name)
        await create_all_tables(engine=async_engine, base_model=Base)
        
        connection = await asyncpg.connect(self.test_db_url)
        assert await connection.execute(
            '''SELECT EXISTS(
                SELECT FROM 
                    information_schema.tables
                WHERE 
                    table_schema LIKE 'shared' AND 
                    table_name = 'users'
                );'''
        ) == 'SELECT 1'
        
        assert await connection.execute(
            '''SELECT EXISTS(
                SELECT FROM 
                    information_schema.tables
                WHERE 
                    table_schema LIKE 'tenant' AND 
                    table_name = 'expenses'
                );'''
        ) == 'SELECT 1'
        
        assert await connection.execute(
            '''SELECT EXISTS(
                SELECT FROM 
                    information_schema.tables
                WHERE 
                    table_schema LIKE 'tenant' AND 
                    table_name = 'revenues'
                );'''
        ) == 'SELECT 1'
        
        await connection.close()
        
    @pytest.mark.asyncio
    async def test_create_async_session_maker(self):
        engine = await make_async_engine(db_name=self.db_name)
        sm = await create_async_session_maker(engine=engine)
        assert isinstance(sm, async_sessionmaker)
        await engine.dispose()
        
        connection = await asyncpg.connect(self.test_server_url)
        await connection.execute(f'DROP DATABASE {self.db_name} WITH (FORCE)')
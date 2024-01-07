from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine


class Database(ABC):

    def __init__(self) -> None:
        self.async_session_maker: Optional[sessionmaker] = None
        self.async_engine: Optional[AsyncEngine] = None

    async def __call__(self) -> AsyncIterator[AsyncSession]:
        if not self.async_session_maker:
            raise ValueError('async_session_maker is not awailable. Run setup() first')
        
        async with self.async_session_maker() as session:
            yield session

    @abstractmethod
    def setup(self) -> None:
        ...

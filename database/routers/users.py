from fastapi import APIRouter
from fastapi import Depends, Security, status, HTTPException

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from depends import db
from security import get_api_key
from db_models import User, Revenue, Expense


users_router = APIRouter(
    prefix='/users', 
    tags=['users'])



"""
Select queiries
"""

@users_router.get(path='/all/')
async def get_all_users(session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    response = await session.scalars(select(User))
    all_users_data = response.all()
    return all_users_data


@users_router.get(path='/{user_id}/')
async def get_one_user(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    if not user_id:
        return {}
    
    response = await session.scalars(select(User).where(User.user_id == user_id))
    result = response.one_or_none()
    if not result is None:
        return result        

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'User with id {user_id} does not exist'
        )


"""
Add queries
"""

@users_router.post(path='/new/', status_code=201)
async def add_new_user(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    new_user = User(user_id = user_id)
    try:
        async with session.begin():
            session.add(new_user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'User with user_id = {user_id} already exists'
        )

"""
Delete data
"""

@users_router.delete(path='/delete_data/')
async def delete_user_data(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    async with session.begin():
        await session.execute(delete(Expense).where(Expense.user_id == user_id))
        await session.execute(delete(Revenue).where(Revenue.user_id == user_id))

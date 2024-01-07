import datetime
from io import StringIO

from fastapi import APIRouter, Depends, Security, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from depends import db
from security import get_api_key
from db_models import Expense
from .users import get_one_user, add_new_user

expense_router = APIRouter(
    prefix='/expenses', 
    tags=['expenses'], 
)


"""
Select queries
"""

@expense_router.get(path='/all/')
async def get_user_expenses(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_expenses = await session.scalars(select(Expense).where(Expense.user_id == user_id))
    user_expenses_data = user_expenses.all()
    return user_expenses_data


@expense_router.get(path='/in_period/')
async def get_expenses_in_period(user_id: int, period_start: datetime.datetime, period_end: datetime.datetime, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_expenses = await session.scalars(select(Expense).where(Expense.user_id == user_id).where(Expense.datetime_stamp >= period_start).where(Expense.datetime_stamp <= period_end))
    user_expenses_data = user_expenses.all()
    return user_expenses_data


@expense_router.get(path='/specific_date/')
async def get_expenses_from_specific_date(user_id: int, specific_date: datetime.date, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    p_start = datetime.datetime(year=specific_date.year, month=specific_date.month, day=specific_date.day, hour=0, minute=0, second=1)
    p_end = datetime.datetime(year=specific_date.year, month=specific_date.month, day=specific_date.day, hour=23, minute=59, second=59)

    user_expenses_data = await get_expenses_in_period(user_id=user_id, period_start=p_start, period_end=p_end)
    return user_expenses_data


@expense_router.get(path='/last_days/')
async def get_expenses_from_last_days(user_id: int, days_delta: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    date_start = datetime.date.today() - datetime.timedelta(days=days_delta)
    p_start = datetime.datetime(year=date_start.year, month=date_start.month, day=date_start.day, hour=0, minute=0, second=1)
    p_end = datetime.datetime.now()

    user_expenses_data = await get_expenses_in_period(user_id=user_id, period_start=p_start, period_end=p_end)
    return user_expenses_data


@expense_router.get('/categories/')
async def get_user_expense_categories(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_cats = await session.scalars(select(Expense.category).where(Expense.user_id == user_id))
    user_cats_data = user_cats.all()
    return user_cats_data


@expense_router.get('/subcategories/')
async def get_user_expense_subcategories(user_id: int, category: str, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_subcats = await session.scalars(select(Expense.subcategory).where(Expense.user_id == user_id).where(Expense.category == category))
    user_subcats_data = user_subcats.all()
    return user_subcats_data


"""
Add queries
"""

@expense_router.post(path='/new/', status_code=status.HTTP_201_CREATED)
async def add_expense(user_id: int, category: str, subcategory: str, money_count: str, e_date: str | datetime.datetime, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    try:
        await get_one_user(user_id=user_id, session=session, apikey=apikey)
    except HTTPException:
        try:
            await add_new_user(user_id=user_id, session=session, apikey=apikey)
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT)
        
    if not type(category) == str and (len(category) > 50 or len(category) == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid category')
    if not type(subcategory) == str and (len(subcategory) > 50 or len(subcategory) == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid subcategory')
    if not any([type(money_count) == float, type(money_count) == int]):
        try:
            money_count = float(money_count)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid money count')
        if money_count < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid money count')
    if not type(e_date) == datetime.datetime:
        try:
            e_date = datetime.datetime.strptime(e_date, '%Y-%m-%d %H:%M')
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid date')

    new_expense = Expense(
        user_id = user_id, 
        category = category, 
        money_count = money_count,
        subcategory = subcategory, 
        datetime_stamp = e_date
    )    
    session.add(new_expense)
    await session.commit()


"""
Export
"""

@expense_router.get(path='/export/', response_model=None)
async def export_user_expenses(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_expenses = await get_user_expenses(user_id=user_id, session=session, apikey=apikey)

    if not len(user_expenses) == 0:
        header = ['Категория', 'Подкатегория', 'Сумма', 'Дата и время']
        records = [[exp.category, exp.subcategory, str(exp.money_count), datetime.datetime.strftime(exp.datetime_stamp, '%Y-%m-%d %H:%M')] for exp in user_expenses]

        csv_file = StringIO()
        header_string = ','.join(header) + '\n'
        csv_file.write(header_string)
        for record in records:
            record_string = ','.join(record) + '\n'
            csv_file.write(record_string)
        
        csv_file_value = csv_file.getvalue()
        csv_file.close()
        return csv_file_value
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No expenses to export')
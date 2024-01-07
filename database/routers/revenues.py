import datetime
from io import StringIO

from fastapi import APIRouter, status, HTTPException, Security, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from depends import db
from security import get_api_key
from .users import get_one_user, add_new_user
from db_models import Revenue


revenues_router = APIRouter(
    prefix='/revenues', 
    tags=['revenues']
)


@revenues_router.get(path='/all/')
async def get_all_reveues(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_revenues = await session.scalars(select(Revenue).where(Revenue.user_id == user_id))
    user_revenues_data = user_revenues.all()
    return user_revenues_data


@revenues_router.get(path='/in_period/')
async def get_revenues_in_period(user_id: int, period_start: datetime.datetime, period_end: datetime.datetime, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_revenues = await session.scalars(select(Revenue).where(Revenue.user_id == user_id).where(Revenue.datetime_stamp >= period_start).where(Revenue.datetime_stamp <= period_end))
    user_revenues_data = user_revenues.all()
    return user_revenues_data


@revenues_router.get(path='/last_days/')
async def get_revenues_from_last_days(user_id: int, days_delta: int, session: AsyncSession = Depends(db), apikey = Security(get_api_key)):
    date_start = datetime.date.today() - datetime.timedelta(days=days_delta)
    p_start = datetime.datetime(year=date_start.year, month=date_start.month, day=date_start.day, hourt=0, minute=0, second=1)
    p_end = datetime.datetime.now()

    user_revenues_data = await get_revenues_in_period(user_id=user_id, period_start=p_start, period_end=p_end, session=session, apikey=apikey)
    return user_revenues_data


@revenues_router.get(path='/specific_date/')
async def get_revenues_from_specific_date(user_id: int, specific_date: datetime.date, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    p_start = datetime.datetime(year=specific_date.year, month=specific_date.month, day=specific_date.day, hour=0, minute=0, second=1)
    p_end = datetime.datetime(year=specific_date.year, month=specific_date.month, day=specific_date.day, hour=23, minute=59, second=59)

    user_revenues_data = await get_revenues_in_period(user_id=user_id, period_start=p_start, period_end=p_end, session=session, apikey=apikey)
    return user_revenues_data


@revenues_router.get(path='/categories/')
async def get_user_revenue_categories(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_cats = await session.scalars(select(Revenue.category).where(Revenue.user_id == user_id))
    user_cats_data = user_cats.all()
    return user_cats_data


@revenues_router.get(path='/types/')
async def get_user_revenue_types(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_types = await session.scalars(select(Revenue.type_).where(Revenue.user_id == user_id))
    user_types_data = user_types.all()
    return user_types_data


"""
Add queiries
"""

@revenues_router.post(path='/new/', status_code=status.HTTP_201_CREATED)
async def add_revenue(user_id: int, category: str, type_: str, money_count: float, r_date: datetime.date | str, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    try:
        await get_one_user(user_id=user_id, session=session, apikey=apikey)
    except HTTPException:
        try:
            await add_new_user(user_id=user_id, session=session, apikey=apikey)
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail='User was not nor found neither created')
    
    if not type(category) == str and (len(category) > 50 or len(category) == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid category')
    if not type(type_) == str and (len(type_) > 50 or len(type_) == 0): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invallid type_')
    if not any([type(money_count) == float, type(money_count) == int]) or money_count < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid money_count')
    if not type(r_date) == datetime.datetime:
        try:
            r_date = datetime.datetime.strptime(r_date, '%Y-%m-%d %H:%M')
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid r_date')
        
    new_revenue = Revenue(
        user_id = user_id, 
        category = category, 
        type_ = type_, 
        datetime_stamp = r_date, 
        money_count = money_count
    )
    session.add(new_revenue)
    await session.commit()
    

"""
Export
"""

@revenues_router.get(path='/export/')
async def export_user_revenues(user_id: int, session: AsyncSession = Depends(db), apikey: str = Security(get_api_key)):
    user_revenues = await get_all_reveues(user_id=user_id, session=session, apikey=apikey)

    if not len(user_revenues) == 0:
        header = ['Категория', 'Тип', 'Сумма', 'Дата и время']
        header_str = ','.join(header) + '\n'
        records = [[revenue.category, revenue.type_, str(revenue.money_count), datetime.datetime.strftime(revenue.datetime_stamp, '%Y-%m-%d %H:%M')] for revenue in user_revenues]

        csv_file = StringIO()
        csv_file.write(header_str)
        for record in records:
            record_str = ','.join(record) + '\n'
            csv_file.write(record_str)
        
        csv_file_data = csv_file.getvalue()
        csv_file.close()
        return csv_file_data
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No revenues to export')
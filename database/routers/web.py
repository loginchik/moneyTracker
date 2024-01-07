import os 
import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db_models import Revenue, Expense, User

from depends import db 

from graph_maker.line_graph import make_line_chart
from graph_maker.bar_graph import make_categories_bar, make_types_bar
from graph_maker.comparison_table import make_comparison_expense


web_router = APIRouter(
    prefix='/open'
)


templates_path = os.path.abspath('../frontend/templates')
templates = Jinja2Templates(directory=templates_path)


def expenses_report(values: list, period: str, daily: bool = False, min_date: datetime.datetime = None):
    total = sum([expense.money_count for expense in values])
    dynamics_graph = make_line_chart(values=values, title='Динамика расходов за ' + period, daily=daily, min_date=min_date)
    categories_bar = make_categories_bar(values=values, title='Расходы по категориям за ' + period)

    return total, dynamics_graph, categories_bar


def revenues_report(values: list, period: str, daily: bool = False, min_date: datetime.datetime = None):
    total = sum([revenue.money_count for revenue in values])
    dymanics_graph = make_line_chart(values=values, title = 'Динамика доходов за ' + period, daily=daily, min_date=min_date)
    categories_bar = make_categories_bar(values=values, title='Доходы по категориям за ' + period)
    types_bar = make_types_bar(values=values, title='Доходы по типам за ' + period)

    return total, dymanics_graph, categories_bar, types_bar


def get_datetime_limit(days_delta: int):
    date_ = datetime.date.today() - datetime.timedelta(days=days_delta)
    dateime_ = datetime.datetime(year=date_.year, month=date_.month, day=date_.day)
    period_descr = f'{datetime.datetime.strftime(date_, "%d.%m.%Y")} - {datetime.datetime.strftime(datetime.date.today(), "%d.%m.%Y")}'

    return dateime_, period_descr


@web_router.get('/{user_id}')
async def load_user_page(request: Request, user_id: int, password: str, session: AsyncSession = Depends(db)):
    
    async def check_user_password(user_id: int, password_entered: str):
        user_password_request = await session.scalars(select(User.password).where(User.user_id == user_id))
        user_password = user_password_request.one_or_none()
        return user_password == password_entered
 
    password_check = await check_user_password(user_id=user_id, password_entered=password)

    if password_check:        
        expenses = await session.scalars(select(Expense).where(Expense.user_id == user_id).order_by(Expense.datetime_stamp.desc()))
        expenses_data = expenses.all()
        revenues = await session.scalars(select(Revenue).where(Revenue.user_id == user_id).order_by(Revenue.datetime_stamp.desc()))
        revenues_data = revenues.all()

        if len(expenses_data) == 0 and len(revenues_data) == 0:
            return templates.TemplateResponse(
                request=request, 
                name='404.html'
            )
        
        exp_last_date = datetime.datetime.strftime(expenses_data[-1].datetime_stamp, '%d.%m.%Y')
        exp_recent_date = datetime.datetime.strftime(expenses_data[0].datetime_stamp, '%d.%m.%Y')
        rev_last_date = datetime.datetime.strftime(revenues_data[-1].datetime_stamp, '%d.%m.%Y')
        rev_recent_date = datetime.datetime.strftime(revenues_data[0].datetime_stamp, '%d.%m.%Y')
        datetime_30_days_ago, period_30_descr = get_datetime_limit(days_delta=30)
        datetime_7_days_ago, period_7_descr = get_datetime_limit(days_delta=7)
        
        if len(expenses_data) > 0:
            expenses_total, expenses_dynamics_graph, expenses_categories_bar = expenses_report(values=expenses_data, period=f'{exp_last_date} - {exp_recent_date}')
            last_30_days_expenses = [expense for expense in expenses_data if expense.datetime_stamp >= datetime_30_days_ago]
        else:
            expenses_total, expenses_dynamics_graph, expenses_categories_bar = None, None, None
            last_30_days_expenses = []
        
        if len(revenues_data) > 0:
            revenues_total, revenues_dynamics_graph, revenues_categories_bar, revenues_types_bar = revenues_report(values=revenues_data, period=f'{rev_last_date} - {rev_recent_date}')
            last_30_days_revenues = [revenue for revenue in revenues_data if revenue.datetime_stamp >= datetime_30_days_ago]
        else:
            revenues_total, revenues_dynamics_graph, revenues_categories_bar, revenues_types_bar = None, None, None, None
            last_30_days_revenues = []

        if len(last_30_days_expenses) > 0:
            exp_total_30, exp_dynamics_last_30, exp_categories_last_30 = expenses_report(values=last_30_days_expenses, period=period_30_descr, daily=True, min_date=datetime_30_days_ago)
            exp_30_comparison = make_comparison_expense(values=expenses_data, period_delta=30)
            last_7_days_expenses = [expense for expense in expenses_data if expense.datetime_stamp >= datetime_7_days_ago]
            if len(last_7_days_expenses) > 0:
                exp_total_7, exp_dynamics_last_7, exp_categories_last_7 = expenses_report(values=last_7_days_expenses, period=period_7_descr, daily=True, min_date=datetime_7_days_ago)
                exp_7_comparison = make_comparison_expense(values=expenses_data, period_delta=7)
            else:
                exp_dynamics_last_7, exp_categories_last_7, exp_7_comparison, exp_total_7 = None, None, None, None
        else:
            exp_dynamics_last_30, exp_categories_last_30, exp_30_comparison, exp_total_30 = None, None, None, None
            exp_dynamics_last_7, exp_categories_last_7, exp_7_comparison, exp_total_7 = None, None, None, None

        if len(last_30_days_revenues) > 0:
            rev_last_30_total, rev_dynamics_last_30, rev_categories_last_30, rev_types_last_30 = revenues_report(values=last_30_days_revenues, period=period_30_descr, daily=True, min_date=datetime_30_days_ago)
            last_7_days_revenues = [revenue for revenue in revenues_data if revenue.datetime_stamp >= datetime_7_days_ago]
            rev_last_7_total, rev_dynamics_last_7, rev_categories_last_7, rev_types_last_7 = revenues_report(values=last_7_days_revenues, period=period_7_descr, daily=True, min_date=datetime_7_days_ago) if len(last_7_days_revenues) > 0 else (None, None, None, None)
        else:
            rev_dynamics_last_30, rev_categories_last_30, rev_types_last_30, rev_last_30_total = None, None, None, None
            rev_dynamics_last_7, rev_categories_last_7, rev_types_last_7, rev_last_7_total = None, None, None, None

        return templates.TemplateResponse(
            request=request, 
            name='userpage.html', 
            context={
                'user_id': user_id, 
                'expenses': expenses_data if len(expenses_data) > 0 else None,
                'revenues': revenues_data if len(revenues_data) > 0 else None,
                
                'expenses_total': expenses_total,
                'expenses_dynamics': expenses_dynamics_graph,
                'expenses_categories': expenses_categories_bar,
                'revenues_total': revenues_total,
                'revenues_dynamics': revenues_dynamics_graph, 
                'revenues_categories': revenues_categories_bar,
                'revenues_types': revenues_types_bar, 

                'expenses_total_30': exp_total_30, 
                'expenses_dynamics_last_30': exp_dynamics_last_30,
                'expenses_categories_last_30': exp_categories_last_30, 
                'revenues_total_30': rev_last_30_total,
                'revenues_dynamics_last_30': rev_dynamics_last_30,
                'revenues_categories_last_30': rev_categories_last_30, 
                'revenues_types_last_30': rev_types_last_30,

                'expense_30_comparison': exp_30_comparison,
                'expense_7_comparison': exp_7_comparison,

                'expenses_total_7': exp_total_7,
                'expenses_dynamics_last_7': exp_dynamics_last_7,
                'expenses_categories_last_7': exp_categories_last_7,
                'revenues_total_7': rev_last_7_total, 
                'revenues_dynamics_last_7': rev_dynamics_last_7, 
                'revenues_categories_last_7': rev_categories_last_7, 
                'revenues_types_last_7': rev_types_last_7,
                
                'date_created': datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y %H:%M'),
                'bot_info': {
                    'href': 't.me/KsjWkXjNmECU_bot', 
                    'title': 'Личный менеджер расходов'
                }
            }
        )
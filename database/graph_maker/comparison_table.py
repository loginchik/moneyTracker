import datetime 

import pandas as pd


def get_datetime_limits(delta: int) -> tuple[datetime.datetime]:
    this_delta_days_stop = datetime.date.today() - datetime.timedelta(days=delta)
    last_delta_days_stop = datetime.date.today() - datetime.timedelta(days=delta * 2)
    
    datetime_this_delta = datetime.datetime(year=this_delta_days_stop.year, month=this_delta_days_stop.month, day=this_delta_days_stop.day)
    datetime_last_delta = datetime.datetime(year=last_delta_days_stop.year, month=last_delta_days_stop.month, day=last_delta_days_stop.day)
    return datetime_last_delta, datetime_this_delta


def get_column_names(this_delta: datetime.datetime, last_delta: datetime.datetime, prefix: str = 'Сумма за') -> tuple[str]:
    this_period_label = datetime.datetime.strftime(this_delta, '%d.%m.%Y')
    last_period_label = datetime.datetime.strftime(last_delta, '%d.%m.%Y')
    today_label = datetime.datetime.strftime(datetime.date.today(), '%d.%m.%Y')

    this_column = f'{prefix} {this_period_label} - {today_label}'
    other_column = f'{prefix} {last_period_label} - {this_period_label}'
    return other_column, this_column


def define_period(datetime_stamp: datetime.datetime, date_limit: datetime.datetime, this_column: str, other_column: str) -> str:
    return this_column if datetime_stamp >= date_limit else other_column


def calculate_percentage_change(this_period, other_period):
    if not other_period == 0:
        percentage_change = ((this_period - other_period) / other_period) * 100
        percentage_change = round(percentage_change)
        percentage_str = '+ ' + str(percentage_change) + '%' if percentage_change > 0 else str(percentage_change) + '%'
        return percentage_str
    else:
        return '-'



def make_comparison_expense(values, period_delta: int = 30):
    datetime_60, datetime_30 = get_datetime_limits(delta=period_delta)
    other_column, this_column = get_column_names(this_delta=datetime_30, last_delta=datetime_60)
    
    values_ = [v for v in values if v.datetime_stamp >= datetime_60]
    categories = [v.category for v in values_]
    subcategories = [v.subcategory for v in values_]
    moneys = [v.money_count for v in values_]
    period = [define_period(datetime_stamp=v.datetime_stamp, date_limit=datetime_30, this_column=this_column, other_column=other_column) for v in values_]

    df = pd.DataFrame({'category': categories, 'subcategory': subcategories, 'money': moneys, 'period': period})
    
    if df[df['period'] == other_column].shape[0] > 0:
        pt = pd.pivot_table(data = df, index = ('category', 'subcategory'), columns='period', values='money', aggfunc='sum', fill_value=0).sort_values(by=this_column, ascending=False)
        pt['Изменение'] = (pt[this_column] - pt[other_column]).apply(lambda x: '+ ' + str(x) if x > 0 else str(x))
        pt['Изменение, %'] = pt.apply(lambda x: calculate_percentage_change(this_period=x[this_column], other_period=x[other_column]), axis=1)
        
        pt_header = ['Категория', 'Подкатегория'] + list(pt.columns)
        pt_values = [list(ind) + list(val) for ind, val in zip(pt.index, pt.values)]
        pt_lists = [pt_header, *pt_values]
        return pt_lists
    else:
        return None

    



import datetime
from cycler import cycler
from io import BytesIO
from base64 import b64encode

import matplotlib as mpl
import matplotlib.dates as mpd
import matplotlib.pyplot as plt 

import pandas as pd


mpl.rcParams['figure.autolayout'] = True
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['figure.frameon'] = False
mpl.rcParams['figure.figsize'] = [8, 4]
mpl.rcParams['axes.prop_cycle'] = cycler(color=['#000000', '#404040', '#969696', '#d1d1d1'])
mpl.rcParams['lines.marker'] = 'o'
mpl.rcParams['lines.markersize'] = 4
mpl.rcParams['font.sans-serif'] = ['Roboto', 'Helvetica', 'DejaVu Sans', 'Bitstream Vera Sans', 'Computer Modern Sans Serif', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Arial', 'Avant Garde', 'sans-serif']
mpl.rcParams['font.size'] = 8


def get_last_month_day(month, year):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if year % 4 == 0 else 28
    else:
        return 1


def get_xticks_for_daily(minimum_date, maximum_date):
    if not type(minimum_date) == datetime.date:
        minimum_date = datetime.date(minimum_date.year, minimum_date.month, minimum_date.day)
    if not type(maximum_date) == datetime.date:
        maximum_date = datetime.date(maximum_date.year, maximum_date.month, maximum_date.day)

    days_range = (maximum_date - minimum_date).days
    ticks = [minimum_date + datetime.timedelta(days=i) for i in range(days_range)]
    return ticks[::2] if len(ticks) > 15 else ticks


def make_line_chart(values: list, title: str, daily: bool = False, min_date: datetime.datetime = None):
    dates = [v.datetime_stamp for v in values]
    moneys = [v.money_count for v in values]

    df = pd.DataFrame({'e_date': dates, 'money': moneys})
    df['year'] = df['e_date'].dt.year
    df['month'] = df['e_date'].dt.month
    df['day'] = df['e_date'].dt.day

    figure, axes = plt.subplots()

    if daily:
        pt = pd.pivot_table(data=df, index=('year', 'month', 'day'), values='money', aggfunc='sum')
        x_axis = [datetime.date(year=y, month=m, day=d) for y, m, d in pt.index]
        axes.xaxis.set_major_formatter(mpd.DateFormatter(fmt='%Y-%m-%d'))
    else:
        pt = pd.pivot_table(data=df, index=('year', 'month'), values='money', aggfunc='sum')
        x_axis = [datetime.date(year=y, month=m, day=get_last_month_day(month=m, year=y)) for y, m in pt.index]
        axes.xaxis.set_major_formatter(mpd.DateFormatter(fmt='%Y-%m'))
        x_ticks = None

    axes.grid(visible=True, which='major', axis='both', alpha=0.2, linewidth=1, zorder=1)
    axes.plot(x_axis, pt['money'], zorder=2)
    
    if min_date is None:
        minimun_date = x_axis[0] - datetime.timedelta(days=2)
    else:
        minimun_date_ = min_date - datetime.timedelta(days=2)
        minimun_date = datetime.date(year=minimun_date_.year, month=minimun_date_.month, day=minimun_date_.day)
    maximum_date = x_axis[-1] + datetime.timedelta(days=2)
    
    axes.set_xlim(minimun_date, maximum_date)
    x_ticks = get_xticks_for_daily(minimum_date = minimun_date, maximum_date=maximum_date) if daily else x_axis
    axes.set_xticks(x_ticks)
    axes.set_title(title)
    axes.set_ylabel('Сумма')

    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)

    figure.autofmt_xdate()
    figure.tight_layout()

    buffer = BytesIO()
    figure.savefig(buffer, format='png')
    value = buffer.getvalue()
    buffer.close()
    
    data_url = 'data:image/png;base64,' + b64encode(value).decode()
    return data_url 


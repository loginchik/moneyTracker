from cycler import cycler
from io import BytesIO
from base64 import b64encode

import matplotlib as mpl
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


def make_bar_chart(x_axis, y_axis, title, xlabel):
    figure, axes = plt.subplots()
    bar = axes.barh(y_axis, x_axis, zorder=2)
    axes.set_xlabel(xlabel)
    axes.set_title(title)
    axes.set_xlim(0, max(x_axis) + 0.1 * max(x_axis))

    for rect, value in zip(bar, x_axis):
        x_pos = rect.get_width() + 0.01 * rect.get_width()
        y_pos = rect.get_y() + rect.get_height() / 2
        plt.text(x=x_pos, y=y_pos, s=str(value))

    axes.xaxis.set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['bottom'].set_visible(False)

    figure.tight_layout()

    buffer = BytesIO()
    figure.savefig(buffer, format='png')
    value = buffer.getvalue()
    buffer.close()

    data_url = 'data:image/png;base64,' + b64encode(value).decode()
    return data_url


def make_categories_bar(values: list, title: str):
    categories = [v.category for v in values]
    moneys = [v.money_count for v in values]

    df = pd.DataFrame({'category': categories, 'money': moneys})

    pt = pd.pivot_table(data=df, index='category', values='money', aggfunc='sum').sort_values(by='money', ascending=True)
    x_axis = pt['money']
    y_axis = pt.index

    graph = make_bar_chart(x_axis=x_axis, y_axis=y_axis, title=title, xlabel='Сумма')
    return graph


def make_types_bar(values: list, title: str):
    types = [v.type_ for v in values]
    moneys = [v.money_count for v in values]

    df = pd.DataFrame({'type_': types, 'money': moneys})

    pt = pd.pivot_table(data=df, index='type_', values='money', aggfunc='sum').sort_values(by='money', ascending=True)
    x_axis = pt['money']
    y_axis = pt.index

    graph = make_bar_chart(x_axis=x_axis, y_axis=y_axis, title=title, xlabel='Сумма')
    return graph
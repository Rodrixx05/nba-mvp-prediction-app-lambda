import pandas as pd
from sqlalchemy import create_engine

from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import re

import utils.dashboard_lib_rodrixx as dlib

db_table_name = 'stats_predictions'
results_labels = {'PREDSHARE': 'Predicted Share', 'PREDVOTES': 'Predicted Votes'}
# pio.templates.default = 'ggplot2'

conn_url = 'postgresql://Rodrixx:Jordan-23@postgres-nba:5432/nba_db'
engine = create_engine(conn_url)

query_columns = f"""
    SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = N'{db_table_name}';
"""
query_players = f"""
    SELECT DISTINCT "PLAYER" FROM {db_table_name};
"""
query_datetime = f"""
    SELECT max("DATETIME"), min("DATETIME") FROM {db_table_name}
"""

with engine.connect() as con:
    result_columns = con.execute(query_columns)
    result_players = con.execute(query_players)
    result_datetime = con.execute(query_datetime)

columns_list = [element[0] for element in result_columns]
players_list = [element[0] for element in result_players]
players_list.sort(key = lambda x: x.split(' ')[1])
tuple_datetime = list(result_datetime)[0]
max_datetime = tuple_datetime[0]
min_datetime = tuple_datetime[1]

models_list = [re.search('^PREDVOTES_(.+)', element).group(1) for element in columns_list if re.search('^PREDVOTES', element)]
no_stats_list = ['SEASON', 'RK', 'PLAYER', 'AGE', 'TM', 'POS']
stats_list = list(set(columns_list) - (set(dlib.gen_models_columns(models_list)) | set(no_stats_list)))

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.H1('MVP Prediction App - Season 2022/23', style={'textAlign': 'center'}))),
        dbc.Row(dbc.Col(html.P('Want to check which player is doing better in the NBA right now? You\'re in the right place!', style={'textAlign': 'center'}), width = 8), justify = 'center'),
        dbc.Row(dbc.Col(html.P('This webpage displays the results of trained ML models that predict the NBA\'s MVP of the current season.', style={'textAlign': 'center'}), width = 10), justify = 'center'),
        dbc.Row(dbc.Col(html.P('Fiddle with all the options and have fun!', style={'textAlign': 'center'}), width = 10), justify = 'center'),
        dbc.Container(dbc.Card(
            [
                dbc.CardHeader(html.H3('Initial configuration', className = 'card_title', style={'textAlign': 'center'})),
                dbc.CardBody(dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.H4('Select players', style={'textAlign': 'center'}), width = 6),
                            dbc.Col(html.H4('Select model', style={'textAlign': 'center'}), width = 6)
                        ], justify = 'center'),
                    dbc.Row(
                        [
                            dbc.Col(dcc.RadioItems(id = 'radio_select_players', options = ['Best players', 'Choose players'], value = 'Best players', inputStyle={"margin-left": "5px", "margin-right": "5px"}), width = 3),
                            dbc.Col(
                                [
                                    html.Div(children = 
                                        [
                                            dcc.Input(id = 'number_players', type = 'number', min = 2, max = 10, step = 1, placeholder = 'Nº Players', style={'width': 100}, value = 3)
                                        ], id = 'container_best_players', style = {'display': 'flex', 'justify-content': 'center'}),
                                    html.Div(children = 
                                        [
                                            dcc.Dropdown(id = 'dropdown_players', options = players_list, placeholder = 'Select players', multi = True)
                                        ], id = 'container_custom_players', style = {'display': 'none'})
                                ], width = 3),
                            dbc.Col(dcc.Dropdown(id = 'dropdown_model', options = models_list, value = models_list[0], placeholder = 'Select a model'), width = {'size': 4, 'offset': 1}),
                            dbc.Col(width = 1)
                        ], align = 'center', justify = 'center')
                ]))
            ])),
        dbc.Container(dbc.Card(
            [
                dbc.CardHeader(html.H3('MVP score timeseries', className = 'card_title', style={'textAlign': 'center'})),
                dbc.CardBody(dcc.Graph(id = 'graph_timeseries', figure = {})),
                dbc.CardFooter(dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H5('Select desired interval', style={'textAlign': 'center'}),
                                dcc.DatePickerRange(id = 'daterange_timeseries', min_date_allowed = min_datetime, max_date_allowed = max_datetime, initial_visible_month = max_datetime, start_date = min_datetime, end_date = max_datetime),
                            ], width = 'auto'),
                        dbc.Col(
                            [
                                html.H5('Choose model output', style={'textAlign': 'center'}),
                                dcc.RadioItems(id = 'radio_value_timeseries', options = results_labels, value = 'PREDSHARE', inputStyle={"margin-left": "8px", "margin-right": "5px"})
                            ], width = 'auto')
                    ], align = 'center', justify = 'evenly'))
            ]), style={"margin-top": "25px"}),
        dbc.Container(dbc.Card(
            [
                dbc.CardHeader(html.H3('Stats comparator', className = 'card_title', style={'textAlign': 'center'})),
                dbc.CardBody(html.Div(dash_table.DataTable(
                    id = 'table_stats', 
                    data = [], 
                    columns = [],
                    style_cell = {'font-family': 'sans-serif', 'border': '1px solid black', 'color': 'black'},
                    style_table = {'minWidth': '100%'},
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(220, 220, 220)',
                        }],
                    style_header = 
                        {
                        'backgroundColor': 'rgb(210, 210, 210)',
                        'fontWeight': 'bold'
                        },
                    fixed_columns = {'headers': True, 'data': 1},
                    fill_width = False,
                    editable = False,
                    filter_action = 'none',
                    column_selectable = False,
                    row_selectable = False,
                    row_deletable = False,
                    page_current = 0,
                    page_size = 10
                    ))),
                dbc.CardFooter(dbc.Row(
                    [
                        dbc.Col(dcc.Dropdown(id = 'dropdown_stats', options = stats_list, placeholder = 'Choose stats', multi = True))
                    ], align = 'center', justify = 'center'))
            ]), style={"margin-top": "25px"})
    ])

@app.callback(
    Output('container_best_players', 'style'),
    Output('container_custom_players', 'style'),
    Input('radio_select_players', 'value')
)
def update_select_players(option):
    show_best = {'display': 'flex', 'justify-content': 'center'}
    show_custom = {'display': 'block'}
    hide = {'display': 'none'}
    if option == 'Best players':
        return show_best, hide
    else:
        return hide, show_custom

@app.callback(
    Output('graph_timeseries', 'figure'),
    Input('radio_select_players', 'value'),
    Input('number_players', 'value'),
    Input('dropdown_players', 'value'),
    Input('dropdown_model', 'value'),
    Input('daterange_timeseries', 'start_date'),
    Input('daterange_timeseries', 'end_date'),
    Input('radio_value_timeseries', 'value')
)
def update_timeseries(option, number, players, model, start_date, end_date, value):
    if option == 'Best players':
        query_timeseries = f"""
            SELECT "DATETIME", "PLAYER", "{value}_{model}" FROM {db_table_name}
            WHERE "PLAYER" IN (
                SELECT "PLAYER" FROM (
                    SELECT "PLAYER", "DATETIME", "{value}_{model}" FROM {db_table_name}
                    WHERE "DATETIME" IN (SELECT max("DATETIME") FROM {db_table_name})
                    ORDER BY "{value}_{model}" DESC
                    LIMIT {number}
                ) AS best_players 
            ) AND "DATETIME" BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY "DATETIME" DESC;
        """
        timeseries_df = pd.read_sql(query_timeseries, engine, index_col = "DATETIME", parse_dates = ["DATETIME"])
        fig_timeseries = px.line(data_frame = timeseries_df, y = f'{value}_{model}', color = 'PLAYER')
        fig_timeseries.update_layout(yaxis_title = results_labels[value], xaxis_title = 'Date', legend_title = 'Players', margin=dict(l=20, r=20, t=20, b=20))
        return fig_timeseries
    else:
        query_timeseries = f"""
            SELECT "DATETIME", "PLAYER", "{value}_{model}" FROM {db_table_name}
            WHERE "PLAYER" IN ({str(players)[1:-1]})
            AND "DATETIME" BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY "DATETIME" DESC;
        """
        timeseries_df = pd.read_sql(query_timeseries, engine, index_col = "DATETIME", parse_dates = ["DATETIME"])
        fig_timeseries = px.line(data_frame = timeseries_df, y = f'{value}_{model}', color = 'PLAYER')
        fig_timeseries.update_layout(yaxis_title = results_labels[value], xaxis_title = 'Date', legend_title = 'Players')
        return fig_timeseries

@app.callback(
    Output('table_stats', 'columns'),
    Output('table_stats', 'data'),
    Output('table_stats', 'style_cell_conditional'),
    Input('radio_select_players', 'value'),
    Input('number_players', 'value'),
    Input('dropdown_players', 'value'),
    Input('dropdown_model', 'value'),
    Input('dropdown_stats', 'value')
)
def update_table_stats(option, number, players, model, stats):
    if option == 'Best players':
        query_stats = f"""
            SELECT "DATETIME", "PLAYER", "PREDSHARE_{model}", "PREDVOTES_{model}"{', ' + dlib.string_list_sql(stats) if stats else ''} FROM {db_table_name}
            WHERE "DATETIME" = '{max_datetime.strftime('%Y-%m-%d')}'
            ORDER BY "PREDSHARE_{model}" DESC
            LIMIT {number}     
        """
    else:
        query_stats = f"""
            SELECT "DATETIME", "PLAYER", "PREDSHARE_{model}", "PREDVOTES_{model}"{', ' + dlib.string_list_sql(stats) if stats else ''} FROM {db_table_name}
            WHERE "DATETIME" = '{max_datetime.strftime('%Y-%m-%d')}'
            AND "PLAYER" IN ({str(players)[1:-1]})
            ORDER BY "PREDSHARE_{model}" DESC
        """
    stats_df = pd.read_sql(query_stats, engine)
    stats_df.drop(columns = "DATETIME", inplace = True)
    cols = []
    for col in stats_df.columns:
        col_dict = {'name': col, 'id': col}
        if col == 'PLAYER':
            col_dict['type'] = 'text'
        else:
            col_dict['type'] = 'numeric'
            if '_PC_' in col and 'RANK' not in col:
                col_dict['format'] = {'specifier': '.2~%'}
            else:
                col_dict['format'] = {'specifier': '.2~f'}
        cols.append(col_dict)
    style = [
        {'if': {'column_id': 'PLAYER'}, 'textAlign': 'left'}
    ]
    data = stats_df.to_dict('records')
    return cols, data, style
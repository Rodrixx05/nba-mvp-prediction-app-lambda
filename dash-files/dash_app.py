import pandas as pd
from sqlalchemy import create_engine

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import os
import re

import utils.dashboard_lib_rodrixx as dlib

import sys 
sys.path.append(os.getcwd())

db_table_name = 'stats_predictions'

conn_url = 'postgresql://Rodrixx:Jordan-23@localhost:5432/nba_db'
engine = create_engine(conn_url)

query_columns = f"""
    SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = N'{db_table_name}';
"""
query_players = f"""
    SELECT DISTINCT "PLAYER" FROM {db_table_name};
"""
with engine.connect() as con:
    result_columns = con.execute(query_columns)
    result_players = con.execute(query_players)

columns_list = [element[0] for element in result_columns]
players_list = [element[0] for element in result_players]
players_list.sort(key = lambda x: x.split(' ')[1])

models_list = [re.search('^PREDVOTES_(.+)', element).group(1) for element in columns_list if re.search('^PREDVOTES', element)]
no_stats_list = ['SEASON', 'RK', 'PLAYER', 'AGE', 'TM', 'POS']
stats_list = list(set(columns_list) - (set(dlib.gen_models_columns(models_list)) | set(no_stats_list)))

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
application = app.server

app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.H1('MVP Prediction App - Season 2022/23', style={'textAlign': 'center'}))),
        dbc.Row(dbc.Col(html.P('Want to check which player is doing better in the NBA right now? You\'re in the right place!', style={'textAlign': 'center'}), width = 8), justify = 'center'),
        dbc.Row(dbc.Col(html.P('This webpage displays the results of trained ML models that predict the NBA\'s MVP of the current season.', style={'textAlign': 'center'}), width = 10), justify = 'center'),
        dbc.Row(dbc.Col(html.P('Fiddle with all the options and have fun!', style={'textAlign': 'center'}), width = 10), justify = 'center'),
        dbc.Card(
            [
                dbc.CardHeader(html.H4('Initial configuration', className = 'card_title', style={'textAlign': 'center'})),
                dbc.CardBody(dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.H3('Select players', style={'textAlign': 'center'}), width = 6),
                            dbc.Col(html.H3('Select model', style={'textAlign': 'center'}), width = 6)
                        ], justify = 'center'),
                    dbc.Row(
                        [
                            dbc.Col(dcc.RadioItems(id = 'radio_select_players', options = ['Best players', 'Select players'], value = 'Best players', inputStyle={"margin-left": "5px", "margin-right": "5px"}), width = 3),
                            dbc.Col(html.Div(id = 'container_select_players'), width = 3),
                            dbc.Col(dcc.Dropdown(id = 'dropdown_model', options = models_list, value = models_list[0], placeholder = 'Select a model'), width = {'size': 4, 'offset': 1}),
                            dbc.Col(width = 1)
                        ], align = 'center', justify = 'center')
                ]))
            ], color = 'secondary', inverse = False)
    ])
@app.callback(
    Output('container_select_players', 'children'),
    Input('radio_select_players', 'value')
)
def update_selec_players(option):
    if option == 'Best players':
        return dcc.Input(id = 'number_players', type = 'number', min = 2, max = 10, step = 1, placeholder = 'Nº Players', style={'width': 150})
    else:
        return dcc.Dropdown(id = 'dropdown_players', options = players_list, placeholder = 'Select players', multi = True)

if __name__ == '__main__':
    app.run_server(debug=True, port=8090)
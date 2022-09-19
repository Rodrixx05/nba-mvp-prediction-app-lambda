import pandas as pd
from sqlalchemy import create_engine

from dash import Dash, dcc, html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

import os
import re

import utils.dashboard_lib_rodrixx as dlib

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

models_list = [re.search('^PREDVOTES_(.+)', element).group(1) for element in columns_list if re.search('^PREDVOTES', element)]
no_stats_list = ['SEASON', 'RK', 'PLAYER', 'AGE', 'TM', 'POS']
stats_list = list(set(columns_list) - (set(dlib.gen_models_columns(models_list)) | set(no_stats_list)))

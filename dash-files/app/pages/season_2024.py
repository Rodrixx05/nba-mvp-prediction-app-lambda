import pandas as pd
from sqlalchemy import create_engine

import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

import re
import os

import utils.dashboard_lib_rodrixx as dlib

season = 2024

db_table_name = f'stats_predictions_{season}'

conn_url = os.getenv('NBA_DB_CON')
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

def serve_layout():

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
    models_options = [{'label': dlib.models_translator[model], 'value': model} for model in models_list]
    models_options.sort(key = lambda x: x['label'])
    no_stats_list = ['SEASON', 'RK', 'PLAYER', 'AGE', 'TM', 'POS']
    stats_list = list(set(columns_list) - (set(dlib.gen_models_columns(models_list, columns_list)) | set(no_stats_list)))
    stats_options = [{'label': dlib.cols_translator[col], 'value': col} for col in stats_list]
    stats_options.sort(key = lambda x: x['label'])

    layout = html.Div(
        [
            dbc.Row(dbc.Col(html.H2(f'Season {int(season) - 1}/{str(season)[2:]}', style={'textAlign': 'center', 'margin-bottom': '25px'}))),
            dbc.Container(dbc.Card(
                [
                    dbc.CardHeader(html.H3('Initial configuration', className = 'card_title', style={'textAlign': 'center'})),
                    dbc.CardBody(dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.H4('Select players', style={'textAlign': 'center'}), width = 6),
                                dbc.Col(html.H4('Select ML model', style={'textAlign': 'center'}), width = 6)
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
                                dbc.Col(dcc.Dropdown(id = 'dropdown_model', options = models_options, value = models_options[1]['value'], placeholder = 'Select a model'), width = {'size': 4, 'offset': 1}),
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
                                    dcc.DatePickerRange(id = 'daterange_timeseries', min_date_allowed = min_datetime, max_date_allowed = max_datetime, initial_visible_month = max_datetime, start_date = min_datetime, end_date = max_datetime, display_format = 'DD/MM/YYYY'),
                                ], width = 'auto'),
                            dbc.Col(
                                [
                                    html.H5('Select model output', style={'textAlign': 'center'}),
                                    dcc.RadioItems(id = 'radio_value_timeseries', options = dlib.results_labels, value = 'PREDSHARE', inputStyle={"margin-left": "8px", "margin-right": "5px"})
                                ], width = 'auto')
                        ], align = 'center', justify = 'evenly'))
                ]), style={"margin-top": "25px"}),
            dbc.Container(dbc.Card(
                [
                    dbc.CardHeader(html.H3('Models comparator', className = 'card_title', style={'textAlign': 'center'})),
                    dbc.CardBody(dbc.Row(dbc.Col(dash_table.DataTable(
                        id = 'table_models', 
                        data = [], 
                        columns = [],
                        style_cell = {'font-family': 'sans-serif', 'border': '1px solid black', 'color': 'black'},
                        style_table = {'minWidth': '100%'},
                        style_header = 
                            {
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'fontWeight': 'bold'
                            },
                        fill_width = False,
                        editable = False,
                        filter_action = 'none',
                        column_selectable = False,
                        row_selectable = 'single',
                        cell_selectable = False,
                        row_deletable = False,
                        page_current = 0,
                        page_size = 10
                        ), width = 'auto'), align = 'center', justify = 'center')),
                    dbc.CardFooter(dbc.Row(
                        [
                            dbc.Col(dcc.RadioItems(id = 'radio_metric_models', options = dlib.ext_results_labels, value = 'PREDSHARE', inputStyle={"margin-left": "8px", "margin-right": "5px"}, inline = True), width = 'auto')
                        ], align = 'center', justify = 'center'))
                ]), style={"margin-top": "25px"}),
            dbc.Container(dbc.Card(
                [
                    dbc.CardHeader(html.H3('Stats comparator', className = 'card_title', style={'textAlign': 'center'})),
                    dbc.CardBody(dbc.Row(dbc.Col(dash_table.DataTable(
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
                        ), class_name = 'center'))),
                    dbc.CardFooter(dbc.Row(
                        [
                            dbc.Col(dcc.Dropdown(id = 'dropdown_stats', options = stats_options, placeholder = 'Choose stats', multi = True))
                        ], align = 'center', justify = 'center'))
                ]), style={"margin-top": "25px", "margin-bottom": "25px"}),
            html.Footer(children = 
                [
                    'Stats are updated every day at 10:00:00 (UTC time) from ',
                    html.A('Basketball Reference', href = 'https://basketball-reference.com', target = '_blank'),
                    html.Br(),
                    'Go back ',
                    dcc.Link('Home', href = '/')
                ], style = {'textAlign': 'center'})
        ])
    
    return layout

dash.register_page(__name__, path = f'/{season}')

layout = serve_layout

@callback(
    Output('container_best_players', 'style'),
    Output('container_custom_players', 'style'),
    Input('radio_select_players', 'value')
)
def update_select_players_2024(option):
    show_best = {'display': 'flex', 'justify-content': 'center'}
    show_custom = {'display': 'block'}
    hide = {'display': 'none'}
    if option == 'Best players':
        return show_best, hide
    else:
        return hide, show_custom

@callback(
    Output('graph_timeseries', 'figure'),
    Input('radio_select_players', 'value'),
    Input('number_players', 'value'),
    Input('dropdown_players', 'value'),
    Input('dropdown_model', 'value'),
    Input('daterange_timeseries', 'start_date'),
    Input('daterange_timeseries', 'end_date'),
    Input('radio_value_timeseries', 'value')
)
def update_timeseries_2024(option, number, players, model, start_date, end_date, value):
    if option == 'Best players':
        query_timeseries = f"""
            SELECT "DATETIME", "PLAYER", "{value}_{model}" FROM {db_table_name}
            WHERE "PLAYER" IN (
                SELECT "PLAYER" FROM (
                    SELECT "PLAYER", "DATETIME", "{value}_{model}" FROM {db_table_name}
                    WHERE "DATETIME" = '{end_date}'
                    ORDER BY "{value}_{model}" DESC
                    LIMIT {number}
                ) AS best_players 
            ) AND "DATETIME" BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY "DATETIME" DESC, "{value}_{model}" DESC;
        """       
    else:
        query_timeseries = f"""
            SELECT "DATETIME", "PLAYER", "{value}_{model}" FROM {db_table_name}
            WHERE "PLAYER" IN ({str(players)[1:-1]})
            AND "DATETIME" BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY "DATETIME" DESC, "{value}_{model}" DESC;
        """
    timeseries_df = pd.read_sql(query_timeseries, engine, index_col = "DATETIME", parse_dates = ["DATETIME"])
    fig_timeseries = px.line(data_frame = timeseries_df, y = f'{value}_{model}', color = 'PLAYER', hover_name = 'PLAYER', hover_data = {'PLAYER': False, f'{value}_{model}': ':.3f'})
    y_label = list(filter(lambda x: x['value'] == value, dlib.results_labels))[0]['label']
    fig_timeseries.update_layout(yaxis_title = y_label, xaxis_title = 'Date', legend_title = 'Players', margin=dict(l=20, r=20, t=20, b=20))
    fig_timeseries.update_traces(mode = "markers+lines")
    return fig_timeseries

@callback(
    Output('table_models', 'columns'),
    Output('table_models', 'data'),
    Output('table_models', 'style_data_conditional'),
    Output('table_models', 'style_cell_conditional'),
    Input('radio_select_players', 'value'),
    Input('number_players', 'value'),
    Input('dropdown_players', 'value'),
    Input('dropdown_model', 'value'),
    Input('radio_metric_models', 'value'),
    Input('table_models', 'selected_rows'),
    State('dropdown_model', 'options'),
    State('daterange_timeseries', 'max_date_allowed'),
)

def update_table_models_2024(option, number, players, model, metric, rows, models_options, max_datetime):
    models_list = [model['value'] for model in models_options]
    metric_cols_list = dlib.gen_metric_cols_list(models_list, model, metric)
    sql_metric_cols_list = dlib.string_list_sql(metric_cols_list)
    if option == 'Best players':
        query_models = f"""
            SELECT "DATETIME", "PLAYER", {sql_metric_cols_list} FROM {db_table_name}
            WHERE "DATETIME" = '{max_datetime}'
            ORDER BY "PREDSHARE_{model}" DESC
            LIMIT {number};     
        """
    else:
        query_models = f"""
            SELECT "DATETIME", "PLAYER", {sql_metric_cols_list} FROM {db_table_name}
            WHERE "DATETIME" = '{max_datetime}'
            AND "PLAYER" IN ({str(players)[1:-1]})
            ORDER BY "PREDSHARE_{model}" DESC;
        """
    models_df = pd.read_sql(query_models, engine)
    models_df.drop(columns = "DATETIME", inplace = True)
    cols = []
    for col in models_df.columns:
        if col == 'PLAYER':
            col_dict = {'name': dlib.cols_translator[col], 'id': col}
            col_dict['type'] = 'text'
        else:
            col_dict = {'name': dlib.models_translator[col.split('_')[1]], 'id': col}
            col_dict['type'] = 'numeric'
            if 'SHARE' in col:
                col_dict['format'] = {'specifier': '.2~f'}
            else:
                col_dict['format'] = {'specifier': 'd'}
        cols.append(col_dict)
    
    style_cell = [{'if': {'column_id': 'PLAYER'}, 'textAlign': 'left'}]

    style_data = [{'if': {'column_id': f'{metric_cols_list[0]}'}, 'fontWeight': 'bold'}]

    if rows:
        border_style = '2px dashed royalBlue'
        border_conditional = [
            {
                'if': {'row_index': rows[0], 'column_id': ['PLAYER'] + metric_cols_list}, 
                'border-top': border_style,
                'border-bottom': border_style
            },
            {
                'if': {'row_index': rows[0], 'column_id': 'PLAYER'},
                'border-left': border_style
            },
            {
                'if': {'row_index': rows[0], 'column_id': metric_cols_list[-1]},
                'border-right': border_style
            }

        ]
        style_data += border_conditional

    for element in metric_cols_list[1:]:
        conditional_style = [
            {
                'if': {'filter_query': '{{{0}}} {2} {{{1}}}'.format(element, metric_cols_list[0], '<' if metric == 'PREDRANK' else '>'), 'column_id': f'{element}'},
                'backgroundColor': '#98FB98'
            },
            {
                'if': {'filter_query': '{{{0}}} {2} {{{1}}}'.format(element, metric_cols_list[0], '>' if metric == 'PREDRANK' else '<'), 'column_id': f'{element}'},
                'backgroundColor': '#DB7093'            
            },
            {
                'if': {'filter_query': '{{{0}}} = {{{1}}}'.format(element, metric_cols_list[0]), 'column_id': f'{element}'},
                'backgroundColor': '#FFC047'
            }]
        style_data += conditional_style

    data = models_df.to_dict('records')

    return cols, data, style_data, style_cell 

@callback(
    Output('table_stats', 'columns'),
    Output('table_stats', 'data'),
    Output('table_stats', 'style_cell_conditional'),
    Input('radio_select_players', 'value'),
    Input('number_players', 'value'),
    Input('dropdown_players', 'value'),
    Input('dropdown_model', 'value'),
    Input('dropdown_stats', 'value'),
    State('daterange_timeseries', 'max_date_allowed')
)
def update_table_stats_2024(option, number, players, model, stats, max_datetime):
    if option == 'Best players':
        query_stats = f"""
            SELECT "DATETIME", "PLAYER", "PREDSHARE_{model}", "PREDVOTES_{model}"{', ' + dlib.string_list_sql(stats) if stats else ''} FROM {db_table_name}
            WHERE "DATETIME" = '{max_datetime}'
            ORDER BY "PREDSHARE_{model}" DESC
            LIMIT {number} ;    
        """
    else:
        query_stats = f"""
            SELECT "DATETIME", "PLAYER", "PREDSHARE_{model}", "PREDVOTES_{model}"{', ' + dlib.string_list_sql(stats) if stats else ''} FROM {db_table_name}
            WHERE "DATETIME" = '{max_datetime}'
            AND "PLAYER" IN ({str(players)[1:-1]})
            ORDER BY "PREDSHARE_{model}" DESC;
        """
    stats_df = pd.read_sql(query_stats, engine)
    stats_df.drop(columns = "DATETIME", inplace = True)
    cols = []
    for col in stats_df.columns:
        col_dict = {'name': dlib.cols_translator[col], 'id': col}
        if col == 'PLAYER':
            col_dict['type'] = 'text'
        else:
            col_dict['type'] = 'numeric'
            if '#' in col and 'RANK' not in col:
                col_dict['format'] = {'specifier': '.2~%'}
            else:
                col_dict['format'] = {'specifier': '.2~f'}
        cols.append(col_dict)
    style = [
        {'if': {'column_id': 'PLAYER'}, 'textAlign': 'left'}
    ]
    data = stats_df.to_dict('records')
    return cols, data, style
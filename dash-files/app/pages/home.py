import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path = '/')

def get_season_index(page_name):
    season_year_2 = page_name.split(' ')[1]
    return f"Season {int(season_year_2) - 1}/{season_year_2[2:]}"

def serve_layout():
    index_layout =  dbc.Row(dbc.Col(dbc.Card(
        [
            dbc.CardHeader(html.H3('Choose a Season', className = 'card_title', style={'textAlign': 'center'})),
            dbc.CardBody(dbc.Container(
                [dbc.Row(dbc.Col((dcc.Link(get_season_index(page['name']), href=page['relative_path'], className = 'text-center'))), style = {'textAlign': 'center'}) 
                 for page in dash.page_registry.values() if page['name'] != 'Home']))
        ]), width = 6), justify = 'center')
    return index_layout

layout = serve_layout
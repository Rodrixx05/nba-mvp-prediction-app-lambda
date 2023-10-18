import dash
from dash import Dash, dcc, html, get_asset_url
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], use_pages = True)
app.layout = html.Div(
    [
        dbc.Row([
            dbc.Col(html.Img(src = get_asset_url('nba_logo.jpg'), style={'width':'100%', 'border-radius': '10%'}), width = 2, style={'textAlign': 'center'}),
            dbc.Col([
                dbc.Row(dbc.Col(html.H1(dcc.Link('MVP Prediction App', href = '/'), style={'textAlign': 'center', 'margin-bottom': '30px'}))),
                dbc.Row(dbc.Col(html.P('Want to check which player is doing better in the NBA right now? You\'re in the right place!', style={'textAlign': 'center'})), justify = 'center'),
                dbc.Row(dbc.Col(html.P('This webpage displays the results of trained ML models that predict the NBA\'s MVP of the current season.', style={'textAlign': 'center'})), justify = 'center'),
                dbc.Row(dbc.Col(html.P('Fiddle with all the options and have fun!', style={'textAlign': 'center'})), justify = 'center'),
            ]),
            dbc.Col(html.Img(src = get_asset_url('br_logo.png'), style={'width':'100%', 'border-radius': '10%'}), width = 2, style={'textAlign': 'center'})
        ], align = 'center', style={"height": "50%", 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px', 'margin-bottom': '30px'}),
        dash.page_container
    ])
app.title = 'NBA MVP Prediction App'
server = app.server

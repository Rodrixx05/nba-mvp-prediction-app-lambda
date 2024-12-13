def string_list_sql(mylist):
    return str(mylist)[1:-1].replace('\'', '\"')

def gen_models_columns(mylist, cols):
    returnlist = []
    for model in mylist:
        model_cols = list(filter(lambda x: model in x, cols))
        returnlist += model_cols
    return returnlist

def gen_metric_cols_list(mylist, selected_model, metric):
    newlist = mylist.copy()
    newlist.remove(selected_model)
    newlist.insert(0, selected_model)
    return list(map(lambda x: f'{metric}_{x}' if 'ADJ' not in metric else f'PREDSHARE_{x}_ADJ', newlist))

def id_factory(page: str):
    def func(_id: str):
        return f"{page}-{_id}"
    return func

def treat_single_quote(players):
  if players:
    new_players = list(map(lambda player: player.replace("'", r"''"), players))
    return str(new_players)[1:-1].replace('"', "'")

cols_translator = {
    "MP_TOT": "Min Tot",
    "PREDSHARE_RF": "Predicted Share RF",
    "PREDSHARE_ENS": "Predicted Share ENS",
    "PREDSHARE_XGB": "Predicted Share XGB",
    "PREDSHARE_RF_ADJ": "Adj Predicted Share RF",
    "PREDVOTES_RF": "Predicted Votes RF",
    "PREDRANK_RF": "Predicted Rank RF",
    "PREDSHARE_ENS_ADJ": "Adj Predicted Share ENS",
    "PREDVOTES_ENS": "Predicted Votes ENS",
    "PREDRANK_ENS": "Predicted Rank ENS",
    "PREDSHARE_XGB_ADJ": "Adj Predicted Share XGB",
    "PREDVOTES_XGB": "Predicted Votes XGB",
    "PREDRANK_XGB": "Predicted Rank XGB",
    "DATETIME": "Date",
    "AGE": "Age",
    "MP_PG": "Min PG",
    "FG_PG": "FGM PG",
    "FGA_PG": "FGA PG",
    "FG#": "FG%",
    "3P_PG": "3PM PG",
    "3PA_PG": "3PA PG",
    "3P#": "3P%",
    "2P_PG": "2PM PG",
    "2PA_PG": "2PA PG",
    "2P#": "2P%",
    "EFG#": "EFG%",
    "FT_PG": "FTM PG",
    "FTA_PG": "FTA PG",
    "FT#": "FT%",
    "ORB_PG": "ORB PG",
    "DRB_PG": "DRB PG",
    "TRB_PG": "TRB PG",
    "AST_PG": "AST PG",
    "STL_PG": "STL PG",
    "BLK_PG": "BLK PG",
    "TOV_PG": "TOV PG",
    "PF_PG": "PF PG",
    "PTS_PG": "PTS PG",
    "MP_RANK_PG": "Min PG Rank",
    "FG_RANK_PG": "FGM PG Rank",
    "FGA_RANK_PG": "FGA PG Rank",
    "FG#_RANK": "FG% Rank",
    "3P_RANK_PG": "3PM PG Rank",
    "3PA_RANK_PG": "3PA PG Rank",
    "3P#_RANK": "3P% Rank",
    "2P_RANK_PG": "2PM PG Rank",
    "2PA_RANK_PG": "2PA PG Rank",
    "2P#_RANK": "2P% Rank",
    "EFG#_RANK": "EFG% Rank",
    "FT_RANK_PG": "FTM PG Rank",
    "FTA_RANK_PG": "FTA PG Rank",
    "FT#_RANK": "FT% Rank",
    "ORB_RANK_PG": "ORB PG Rank",
    "DRB_RANK_PG": "DRB PG Rank",
    "TRB_RANK_PG": "TRB PG Rank",
    "AST_RANK_PG": "AST PG Rank",
    "STL_RANK_PG": "STL PG Rank",
    "BLK_RANK_PG": "BLK PG Rank",
    "TOV_RANK_PG": "TOV PG Rank",
    "PF_RANK_PG": "PF PG Rank",
    "PTS_RANK_PG": "PTS PG Rank",
    "#GS": "Games Started %",
    "SEASON": "Season",
    "PER": "Player Efficiency Rating",
    "TS#": "True Shooting %",
    "3PAR": "3-Point Attempt Rate",
    "FTR": "Free-Throw Attempt Rate",
    "ORB#": "ORB%",
    "DRB#": "DRB%",
    "TRB#": "TRB%",
    "AST#": "AST%",
    "STL#": "STL%",
    "BLK#": "BLK%",
    "TOV#": "TOV%",
    "USG#": "Usage %",
    "OWS": "Offensive Win Shares",
    "DWS": "Defensive Win Shares",
    "WS": "Win Shares",
    "WS/48": "Win Shares Per 48 Min",
    "OBPM": "Offensive Box +/-",
    "DBPM": "Defensive Box +/-",
    "BPM": "Box +/-",
    "VORP": "Value Over Replacement Player",
    "PER_RANK": "Player Efficiency Rating Rank",
    "TS#_RANK": "True Shooting % Rank",
    "3PAR_RANK": "3-Point Attempt Rate Rank",
    "FTR_RANK": "Free-Throw Attempt Rate Rank",
    "ORB#_RANK": "ORB% Rank",
    "DRB#_RANK": "DRB% Rank",
    "TRB#_RANK": "TRB% Rank",
    "AST#_RANK": "AST% Rank",
    "STL#_RANK": "STL% Rank",
    "BLK#_RANK": "BLK% Rank",
    "TOV#_RANK": "TOV% Rank",
    "USG#_RANK": "Usage % Rank",
    "OWS_RANK": "Offensive Win Shares Rank",
    "DWS_RANK": "Defensive Win Shares Rank",
    "WS_RANK": "Win Shares Rank",
    "WS/48_RANK": "Win Shares Per 48 Min Rank",
    "OBPM_RANK": "Offensive Box +/- Rank",
    "DBPM_RANK": "Defensive Box +/- Rank",
    "BPM_RANK": "Box +/- Rank",
    "VORP_RANK": "Value Over Replacement Player Rank",
    "#W": "Wins %",
    "#W_RANK": "Wins % Rank",
    "#G": "Games Played %",
    "RK": "ID",
    "G": "Games Played",
    "GS": "Games Started",
    "GT": "Games Total",
    "TOV_RANK_TOT": "TOV Tot Rank",
    "PF_RANK_TOT": "PF Tot Rank",
    "PTS_RANK_TOT": "PTS Tot Rank",
    "FG_TOT": "FGM Tot",
    "FGA_TOT": "FGA Tot",
    "3P_TOT": "3PM Tot",
    "3PA_TOT": "3PA Tot",
    "2P_TOT": "2PM Tot",
    "2PA_TOT": "2PA Tot",
    "FT_TOT": "FTM Tot",
    "FTA_TOT": "FTA Tot",
    "ORB_TOT": "ORB Tot",
    "DRB_TOT": "DRB Tot",
    "TRB_TOT": "TRB Tot",
    "AST_TOT": "AST Tot",
    "STL_TOT": "STL Tot",
    "BLK_TOT": "BLK Tot",
    "TOV_TOT": "TOV Tot",
    "PF_TOT": "PF Tot",
    "PTS_TOT": "PTS Tot",
    "MP_RANK_TOT": "Min Tot Rank",
    "FG_RANK_TOT": "FGM Tot Rank",
    "FGA_RANK_TOT": "FGA Tot Rank",
    "3P_RANK_TOT": "3PM Tot Rank",
    "3PA_RANK_TOT": "3PA Tot Rank",
    "2P_RANK_TOT": "2PM Tot Rank",
    "2PA_RANK_TOT": "2PA Tot Rank",
    "FT_RANK_TOT": "FTM Tot Rank",
    "FTA_RANK_TOT": "FTA Tot Rank",
    "ORB_RANK_TOT": "ORB Tot Rank",
    "DRB_RANK_TOT": "DRB Tot Rank",
    "TRB_RANK_TOT": "TRB Tot Rank",
    "AST_RANK_TOT": "AST Tot Rank",
    "STL_RANK_TOT": "STL Tot Rank",
    "BLK_RANK_TOT": "BLK Tot Rank",
    "TM": "Team",
    "PLAYER": "Player",
    "POS": "Position"
}

models_translator = {
    'RF': 'Random Forest (RF)',
    'ENS': 'Ensemble (ENS)',
    'XGB': 'XGBoost (XGB)',
    'RFV2': 'Random Forest v2 (RFV2)',
    'ENSV2': 'Ensemble v2 (ENSV2)',
    'XGBV2': 'XGBoost v2 (XGBV2)',
    'LGBMV2': 'LightGBM v2 (LGBMV2)'
}

results_labels = [
    {'label': 'Predicted Share', 'value': 'PREDSHARE'},
    {'label': 'Predicted Votes', 'value': 'PREDVOTES'},
]

ext_results_labels = [
    {'label': 'Predicted Share', 'value': 'PREDSHARE'},
    {'label': 'Predicted Votes', 'value': 'PREDVOTES'},
    {'label': 'Adjusted Predicted Share', 'value': 'PREDSHARE_ADJ'},
    {'label': 'Predicted Rank', 'value': 'PREDRANK'},
]
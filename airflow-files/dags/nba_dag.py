from airflow.decorators import task, dag
from datetime import datetime
import os

import pandas as pd
from sklearn.pipeline import Pipeline

import utils.basketball_reference_rodrixx as brr
import utils.preprocessing_lib_rodrixx as prep


DATA_PATH = '/opt/airflow/data'

@dag(
    description='DAG which imports data daily from Basketball Reference and makes predictions on the MVP winner',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2022, 8, 1),
    catchup=False,
    tags=['nba'],
)

def nba_mvp_predictor():

    @task()

    def import_data_br(year = 2022, file_out = 'raw_df.pkl', path_out = DATA_PATH):

        getter = brr.BasketballReferenceGetter()
        raw_df = getter.extract_player_stats_multiple(year, mvp = False, advanced = True, ranks = True)

        df_file = os.path.join(path_out, file_out)
        raw_df.to_pickle(df_file)
    
    @task()
    
    def preprocess_data(file_in = 'raw_df.pkl', path_in = DATA_PATH, file_out = 'pre_df.pkl', path_out = DATA_PATH):

        df_file_in = os.path.join(path_in, file_in)
        pre_df = pd.read_pickle(df_file_in)

        cols_to_drop = ['Rk', 'GT', 'FG_tot', '3PA_tot', '2PA_tot', 'FGA_rank_tot', 'Tm', 'Pos']
        cols_to_filter = ['PER', 'WS/48', 'BPM', 'USG%']

        pipe_prep = Pipeline(steps = [
            ('DropPlayersMultiTeams', prep.DropPlayersMultiTeams()),
            ('OutlierFilter', prep.OutlierFilter(q = .0005, col_to_filter = cols_to_filter)),
            ('SetIndex', prep.SetIndex()),
            ('DropColumns', prep.DropColumns(cols_to_drop)),
            ('DropPlayers', prep.DropPlayers()),
        ])
        pre_df = pipe_prep.fit_transform(pre_df)

        df_file_out = os.path.join(path_out, file_out)
        pre_df.to_pickle(df_file_out)
    
    data_import = import_data_br()
    data_preprocessed = preprocess_data()

    data_import >> data_preprocessed

predict_nba_mvp = nba_mvp_predictor()
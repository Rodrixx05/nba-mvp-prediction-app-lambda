from airflow.decorators import task, dag
from datetime import datetime, date
import os
import re
import pickle5 as pickle

import pandas as pd
from sklearn.pipeline import Pipeline
from sqlalchemy import create_engine

import utils.basketball_reference_rodrixx as brr
import utils.preprocessing_lib_rodrixx as prep
import utils.postprocessing_lib_rodrixx as post


DATA_PATH = '/opt/airflow/data'

@dag(
    description='DAG which imports data daily from Basketball Reference and makes predictions on the MVP winner',
    schedule_interval='0 9 * * *',
    start_date=datetime(2022, 10, 16),
    catchup=False,
    tags=['nba'],
)

def nba_mvp_predictor():

    @task()

    def import_data_br(year = 2023, df_name_out = 'raw_df.pkl'):

        getter = brr.BasketballReferenceGetter()
        raw_df = getter.extract_player_stats_multiple(year, mvp = False, advanced = True, ranks = True)

        df_file = os.path.join(DATA_PATH, df_name_out)
        raw_df.to_pickle(df_file)
    
    @task()
    
    def preprocess_data(df_name_in = 'raw_df.pkl', df_name_out = 'pre_df.pkl', players_name = 'players.pkl', ohe_name = 'ohecol.pkl', dropcols_name = 'dropcols.pkl'):

        df_file_in = os.path.join(DATA_PATH, df_name_in)
        pre_df = pd.read_pickle(df_file_in)

        cols_tot = [col for col in pre_df.columns if '_tot' in col]
        cols_to_drop = ['Rk', 'G', 'GS', 'GT', 'Tm']
        cols_to_drop += cols_tot
        col_to_ohe = 'Pos'

        pipe_prep = Pipeline(steps = [
            ('DropPlayersMultiTeams', prep.DropPlayersMultiTeams()),
            ('SetIndex', prep.SetIndex()),
            ('OHE', prep.OHE(col_to_ohe)),
            ('DropColumns', prep.DropColumns(cols_to_drop)),
            ('DropPlayers', prep.DropPlayers()),
        ])

        pre_df = pipe_prep.fit_transform(pre_df)

        df_file_out = os.path.join(DATA_PATH, df_name_out)
        pre_df.to_pickle(df_file_out)

        players_series = pipe_prep['DropPlayers'].players_list
        players_file = os.path.join(DATA_PATH, players_name)
        players_series.to_pickle(players_file)

        ohe_series = pipe_prep['OHE'].ohe_series
        ohe_file = os.path.join(DATA_PATH, ohe_name)
        ohe_series.to_pickle(ohe_file) 

        dropcols_df = pipe_prep['DropColumns'].drop_df
        dropcols_file = os.path.join(DATA_PATH, dropcols_name)
        dropcols_df.to_pickle(dropcols_file) 
    
    @task()

    def make_prediction(df_name_in = 'pre_df.pkl', prediction_name = 'prediction.pkl'):

        df_file_in = os.path.join(DATA_PATH, df_name_in)
        post_df = pd.read_pickle(df_file_in)

        predictions_list = []
        model_names = [file for file in os.listdir(DATA_PATH) if re.match('^model_.+\.pkl$', file)]

        for model_name in model_names:
            model_file = os.path.join(DATA_PATH, model_name)
            with open(model_file, 'rb') as file:
                model = pickle.load(file)
        
            prediction = model.predict(post_df)

            model_type = re.match('^model_(.+)\.pkl$', model_name).group(1)
            prediction_series = pd.Series(prediction, index = post_df.index, name = f'PredShare_{model_type}')
            predictions_list.append(prediction_series)
        
        prediction_df = pd.concat(predictions_list, axis = 1)

        prediction_file = os.path.join(DATA_PATH, prediction_name)
        prediction_df.to_pickle(prediction_file)
    
    @task()

    def postprocess_data(df_name_in = 'pre_df.pkl', df_name_out = 'final_df.pkl', players_name = 'players.pkl', ohe_name = 'ohecol.pkl', dropcols_name = 'dropcols.pkl', prediction_name = 'prediction.pkl'):

        df_file_in = os.path.join(DATA_PATH, df_name_in)
        pre_df = pd.read_pickle(df_file_in)

        players_file = os.path.join(DATA_PATH, players_name)
        players_series = pd.read_pickle(players_file)

        ohe_file = os.path.join(DATA_PATH, ohe_name)
        ohe_series = pd.read_pickle(ohe_file)

        dropcols_file = os.path.join(DATA_PATH, dropcols_name)
        dropcols_df = pd.read_pickle(dropcols_file)     

        prediction_file = os.path.join(DATA_PATH, prediction_name)
        prediction_df = pd.read_pickle(prediction_file)

        post_df = post.get_processed_prediction(prediction_df, players_series)
        post_df['Datetime'] = date.today()

        final_df = pd.concat([post_df, pre_df], axis = 1)
        final_df = post.add_deleted_columns(final_df, dropcols_df, ohe_series)
        final_df.reset_index(inplace = True, drop = True)
        final_df.columns = map(post.format_column_name, final_df.columns)

        df_file_out = os.path.join(DATA_PATH, df_name_out)
        final_df.to_pickle(df_file_out)
    
    @task()

    def insert_to_db(df_name_in = 'final_df.pkl'):
        df_file_in = os.path.join(DATA_PATH, df_name_in)
        final_df = pd.read_pickle(df_file_in)

        conn_url = os.getenv('NBA_DB_CON')
        conn = create_engine(conn_url)

        final_df.to_sql('stats_predictions_2023', conn, if_exists = 'append', index = False)
    
    data_import = import_data_br()
    data_preprocessed = preprocess_data()
    prediction = make_prediction()
    data_postprocessed = postprocess_data()
    data_to_db = insert_to_db()


    data_import >> data_preprocessed >> prediction >> data_postprocessed >> data_to_db

predict_nba_mvp = nba_mvp_predictor()
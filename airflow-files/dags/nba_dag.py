from airflow.decorators import task, dag
from datetime import datetime
import utils.basketball_reference_rodrixx as brr

@dag(
    description='DAG which imports data daily from Basketball Reference and makes predictions on the MVP winner',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2022, 8, 1),
    catchup=False,
    tags=['nba'],
)
def nba_mvp_predictor():
    @task(task_id = 'import_data')
    def import_data_br(year = 2022, path = '/opt/airflow/data'):
        getter = brr.BasketballReferenceGetter()
        br_df = getter.extract_player_stats_multiple(year, mvp = False, advanced = True, ranks = True)
        br_df.to_pickle(path + '/raw_df.pkl')
    
    data_import = import_data_br()


predict_nba_mvp = nba_mvp_predictor()
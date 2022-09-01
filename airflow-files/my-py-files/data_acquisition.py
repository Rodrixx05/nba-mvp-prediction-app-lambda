import basketball_reference_rodrixx as brr

def import_data_br(year = 2023, path = '/opt/bitnami/pickles'):
    getter = brr.BasketballReferenceGetter()
    br_df = getter.extract_player_stats_multiple(year, mvp = False, advanced = True, ranks = True)
    br_df.to_pickle(path + '/raw_df.pkl')
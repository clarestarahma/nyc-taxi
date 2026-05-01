from prefect import task, get_run_logger

def drop_columns(df_list: list, drop_cols: list):
    for df in df_list:
        df.drop(columns=drop_cols, axis=1, inplace=True)

# drop unused column for yellow and green taxi
@task(name='Drop unused column for yellow and green taxi', retries=3, retry_delay_seconds=10)
def drop_unused_columns(yellow_df_list: list, green_df_list: list, drop_cols_yellow: list, drop_cols_green: list):
    logger = get_run_logger()
    logger.info('Start drop unused columns')
    drop_columns(yellow_df_list, drop_cols_yellow)
    drop_columns(green_df_list, drop_cols_green)
    logger.info('Finish drop unused columns')
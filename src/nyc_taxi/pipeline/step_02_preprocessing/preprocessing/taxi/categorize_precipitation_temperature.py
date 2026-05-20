from nyc_taxi.utils.db_utils import query_to_df, execute_query, get_connection
from nyc_taxi.queries.taxi_queries import TaxiQueries


def apply_categorization():
    with get_connection() as conn:
        execute_query(TaxiQueries.ADD_CATEGORY_PREC.format(target_table='silver.green_trips'), conn)
        execute_query(TaxiQueries.ADD_CATEGORY_PREC.format(target_table='silver.yellow_trips'), conn)
        execute_query(TaxiQueries.ADD_CATEGORY_TEMP.format(target_table='silver.green_trips'), conn)
        execute_query(TaxiQueries.ADD_CATEGORY_TEMP.format(target_table='silver.yellow_trips'), conn)
        conn.execute(TaxiQueries.UPDATE_TEMP_PREC_GREEN)
        conn.execute(TaxiQueries.UPDATE_TEMP_PREC_YELLOW)
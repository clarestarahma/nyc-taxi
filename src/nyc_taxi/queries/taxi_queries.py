class TaxiQueries:
    CREATE_SCHEMA = "CREATE SCHEMA IF NOT EXISTS {schema_name}"

    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM df WHERE 1=0"
    
    INSERT = """
        INSERT INTO {target_table} 
        SELECT * FROM df 
    """

    GET_ALL_DATA = "SELECT * FROM {target_table}"
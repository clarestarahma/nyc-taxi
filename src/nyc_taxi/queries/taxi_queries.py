class TaxiQueries:
    CREATE_SCHEMA = "CREATE SCHEMA IF NOT EXISTS {schema_name}"

    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM df WHERE 1=0"
    
    INSERT = """
        INSERT INTO {target_table} 
        SELECT * FROM df 
    """

    GET_ALL_DATA = "SELECT * FROM {target_table}"

    GET_DATE_TEMP_PREC_YELLOW = "SELECT DATE(tpep_pickup_datetime) as tpep_pickup_datetime, temperature_2m_max, precipitation_sum FROM {target_table}"
    GET_DATE_TEMP_PREC_GREEN = "SELECT DATE(lpep_pickup_datetime) as lpep_pickup_datetime, temperature_2m_max, precipitation_sum FROM {target_table}"

    ADD_CATEGORY_TEMP = "ALTER TABLE {target_table} ADD COLUMN IF NOT EXISTS temp_category VARCHAR"
    ADD_CATEGORY_PREC = "ALTER TABLE {target_table} ADD COLUMN IF NOT EXISTS precip_category VARCHAR"

    UPDATE_TEMP_PREC_YELLOW = """
UPDATE silver.yellow_trips
SET
  precip_category =
    CASE
      WHEN precipitation_sum = 0 THEN 'tidak hujan'
      WHEN precipitation_sum <= 2 THEN 'hujan ringan'
      WHEN precipitation_sum <= 10 THEN 'hujan sedang'
      ELSE 'hujan lebat'
    END,
  temp_category =
    CASE
      WHEN temperature_2m_max < 0 THEN 'sangat dingin'
      WHEN temperature_2m_max < 10 THEN 'dingin'
      WHEN temperature_2m_max < 20 THEN 'sejuk'
      ELSE 'hangat'
    END;
"""
    UPDATE_TEMP_PREC_GREEN = """
UPDATE silver.green_trips
SET
  precip_category =
    CASE
      WHEN precipitation_sum = 0 THEN 'tidak hujan'
      WHEN precipitation_sum <= 2 THEN 'hujan ringan'
      WHEN precipitation_sum <= 10 THEN 'hujan sedang'
      ELSE 'hujan lebat'
    END,
  temp_category =
    CASE
      WHEN temperature_2m_max < 0 THEN 'sangat dingin'
      WHEN temperature_2m_max < 10 THEN 'dingin'
      WHEN temperature_2m_max < 20 THEN 'sejuk'
      ELSE 'hangat'
    END;
"""

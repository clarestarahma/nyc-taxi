import duckdb

# LANGSUNG connect tanpa wrapper kamu
con = duckdb.connect("data/nyc_taxi.db")

print("=== SCHEMAS ===")
print(con.execute("SHOW SCHEMAS").fetchall())

print("\n=== TABLES ===")
print(con.execute("SHOW TABLES").fetchall())

print("\n=== FULL TABLE LIST ===")
print(con.execute("""
SELECT table_schema, table_name 
FROM information_schema.tables
""").fetchall())
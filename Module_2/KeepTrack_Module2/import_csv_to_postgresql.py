import csv
import psycopg2
from psycopg2 import sql

CSV_FILE = r"gapminder_simple.csv"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "gapminder_simple",
    "user": "postgres",
    "password": "Viettri05194826!"
}

SCHEMA = "raw"
TABLE = "main_sheet"


# -----------------------------
# Read CSV header
# -----------------------------
with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    columns = next(reader)

print(f"Found {len(columns)} columns")


# -----------------------------
# Connect PostgreSQL
# -----------------------------
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()


# -----------------------------
# Create schema
# -----------------------------
cur.execute(
    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}")
    .format(sql.Identifier(SCHEMA))
)


# -----------------------------
# Drop existing table
# -----------------------------
cur.execute(
    sql.SQL("DROP TABLE IF EXISTS {}.{}")
    .format(
        sql.Identifier(SCHEMA),
        sql.Identifier(TABLE)
    )
)


# -----------------------------
# Auto create columns as TEXT
# -----------------------------
column_definitions = sql.SQL(", ").join(
    sql.SQL("{} TEXT").format(sql.Identifier(col))
    for col in columns
)

create_query = sql.SQL("""
    CREATE TABLE {}.{} (
        {}
    )
""").format(
    sql.Identifier(SCHEMA),
    sql.Identifier(TABLE),
    column_definitions
)

cur.execute(create_query)
conn.commit()

print("Table created")


# -----------------------------
# COPY CSV
# -----------------------------
with open(CSV_FILE, "r", encoding="utf-8-sig") as f:

    copy_query = sql.SQL("""
        COPY {}.{}
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE
        )
    """).format(
        sql.Identifier(SCHEMA),
        sql.Identifier(TABLE)
    )

    cur.copy_expert(copy_query.as_string(conn), f)

conn.commit()

cur.close()
conn.close()

print("Import completed")
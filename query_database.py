#query_database.py
import sqlite3
from tabulate import tabulate

def fetch_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def fetch_column_names(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    return [column[1] for column in cursor.fetchall()]

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Fetch all table names
    tables = fetch_table_names(cursor)

    for table in tables:
        print(f"\nData from table '{table}':")

        # Fetch column names
        columns = fetch_column_names(cursor, table)

        # Execute query
        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
        rows = cursor.fetchall()

        # Print results in a formatted table
        print(tabulate(rows, headers=columns, tablefmt="grid"))

        # Print total count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Total records: {count}")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()

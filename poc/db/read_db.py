import sqlite3
from prettytable import PrettyTable

def print_table(db_path, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute a query to retrieve all data from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Create a PrettyTable object and set the column names
    table = PrettyTable()
    table.field_names = column_names

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Print the table
    print(table)

    # Close the database connection
    conn.close()

# Example usage
if __name__ == "__main__":
    db_path = 'poc/db/produkte.db'
    table_name = 'produkte'
    print_table(db_path, table_name)

    # print types of each column
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()
    [print(line) for line in rows]
    conn.close()
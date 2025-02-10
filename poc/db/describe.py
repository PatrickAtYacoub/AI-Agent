import sqlalchemy
import os
import argparse
from terminaltables import AsciiTable


def describe_database(engine):
    inspector = sqlalchemy.inspect(engine)
    db_info = {}
    for table_name in inspector.get_table_names():
        db_info[table_name] = describe_table(engine, table_name)
    return db_info

def describe_table(engine, table_name):
    inspector = sqlalchemy.inspect(engine)
    columns = inspector.get_columns(table_name)
    table_info = {
        'columns': columns,
        'primary_key': inspector.get_pk_constraint(table_name),
        'foreign_keys': inspector.get_foreign_keys(table_name),
        'indexes': inspector.get_indexes(table_name)
    }
    return table_info

def info2terminaltable(info):
    table_data = []
    for table_name, table_info in info.items():
        print([table_name])
        table_data.append(['Column', 'Type', 'Nullable', 'Primary Key', 'Foreign Keys', 'Indexes'])
        for column in table_info['columns']:
            table_data.append([
                column['name'],
                column['type'],
                column['nullable'],
                column['name'] in table_info['primary_key']['constrained_columns'],
                [fk['referred_columns'] for fk in table_info['foreign_keys']],
                [index['name'] for index in table_info['indexes']]
            ])
    return AsciiTable(table_data).table


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Describe a SQLite database.")
    parser.add_argument("dbpath", nargs='?', help="Path to the SQLite database file")
    args = parser.parse_args()

    if args.dbpath is None:
        args.dbpath = ".cache/41/cache.db"#input("Please enter the path to the SQLite database file: ")

    DB_PATH = os.path.expanduser(args.dbpath)
    if not os.path.isfile(DB_PATH):
        raise FileNotFoundError(f"Database file '{DB_PATH}' does not exist.")
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    db_info = describe_database(engine)
    print(info2terminaltable(db_info))
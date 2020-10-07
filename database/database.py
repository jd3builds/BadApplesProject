import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    connection = None

    try:
        connection = sqlite3.connect(db_file)
        return connection
        # print(sqlite3.version) # can use to print version
    except Error as err:
        print(err)

    return connection


def create_table(connection, create_table_sql):
    try:
        curs = connection.cursor()
        curs.execute(create_table_sql)
    except Error as err:
        print(err)


if __name__ == "__main__":
    # Just pass desired file name, sqlite3 will then create .db file in CWD. If already made, nothing happens.
    # create_connection("expirations.db")
    # create_connection("useritems.db")

    sql_create_general_items_table = """ CREATE TABLE IF NOT EXISTS general_items (
                                    name text PRIMARY KEY,
                                    days_to_exp integer NOT NULL
                                );"""

    # need to make a query to make user_items table

    connection = create_connection("expirations.db")

    if connection is not None:
        create_table(connection, sql_create_general_items_table)
    else:
        print("Unable to create db connection.")
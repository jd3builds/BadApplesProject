import sqlite3
from sqlite3 import Error


# ----------------- CREATION FUNCTIONS ----------------- #


# Takes in the name of the db file and returns a connection to that db file.
def create_connection(db_file):
    connection = None

    try:
        connection = sqlite3.connect(db_file)
        return connection
        # print(sqlite3.version) # can use to print version
    except Error as err:
        print(err)

    return connection


# Creates a table using the given command in the specified db (via connection)
def create_table(connection, create_table_sql):
    try:
        curs = connection.cursor()
        curs.execute(create_table_sql)
    except Error as err:
        print(err)


# Creates the general items table in the expirations.db file
def create_general_table():
    sql_create_general_items_table = """ CREATE TABLE IF NOT EXISTS general_items (
                                        itemName varchar PRIMARY KEY,
                                        id integer NOT NULL,
                                        category integer NOT NULL,
                                        subcategory integer,
                                        storageType integer,
                                        unopened boolean,
                                        expirationLowerBound integer NOT NULL,
                                        expirationUpperBound integer,
                                        expirationUnitType varchar NOT NULL
                                    );"""

    connection = create_connection("expirations.db")

    if connection is not None:
        create_table(connection, sql_create_general_items_table)
    else:
        print("Unable to create db connection.")


# Creates the user items table in the useritems.db file
def create_user_table():
    sql_create_user_items_table = """ CREATE TABLE IF NOT EXISTS user_items (
                                    itemName varchar PRIMARY KEY,
                                    id integer NOT NULL,
                                    category integer NOT NULL,
                                    subcategory integer,
                                    storageType integer,
                                    unopened boolean,
                                    expirationLowerBound integer NOT NULL,
                                    expirationUpperBound integer,
                                    expirationUnitType varchar NOT NULL
                                    );"""

    connection = create_connection("useritems.db")

    if connection is not None:
        create_table(connection, sql_create_user_items_table)
    else:
        print("Unable to create db connection.")


# Creates the categories table in the categories.db file
def create_category_table():
    sql_create_category_table = """ CREATE TABLE IF NOT EXISTS categories (
                                    id integer PRIMARY KEY,
                                    category varchar NOT NULL
                                    );"""

    connection = create_connection("categories.db")

    if connection is not None:
        create_table(connection, sql_create_category_table)
    else:
        print("Unable to create db connection.")


# Creates the subcategories table in the subcategories.db file
def create_subcategory_table():
    sql_create_subcategory_table = """ CREATE TABLE IF NOT EXISTS subcategories(
                                        id integer PRIMARY KEY,
                                        subcategory varchar NOT NULL
                                    );"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        create_table(connection, sql_create_subcategory_table)
    else:
        print("Unable to create db connection.")


# Creates the storagetype table in the storagetypes.db file
def create_storage_type_table():
    sql_create_storage_type_table = """ CREATE TABLE IF NOT EXISTS storagetype(
                                        id integer PRIMARY KEY,
                                        storagetype varchar NOT NULL
                                    );"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        create_table(connection, sql_create_storage_type_table)
    else:
        print("Unable to create db connection.")


# ----------------- INSERTION FUNCTIONS ----------------- #


# General function for inserting information using the given sql code in specified table from db connection
def insert_table(connection, insert_sql, info):
    try:
        curs = connection.cursor()
        curs.execute(insert_sql, info)
    except Error as err:
        print(err)


# Inserts item in general_items table in expirations.db file
def insert_general_table(item):
    sql_insert_general_table = """ INSERT INTO general_items (itemName, id, category, subcategory, storageType, 
                                                            unopened, expirationLowerBound, expirationUpperBound,
                                                            expirationUnitType) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    connection = create_connection("expirations.db")

    if connection is not None:
        insert_table(connection, sql_insert_general_table, item)
    else:
        print("Unable to create db connection.")


# Inserts item in user_items table in useritems.db file
def insert_user_table(item):
    sql_insert_user_table = """INSERT INTO user_items (itemName, id, category, subcategory, storageType, 
                                                            unopened, expirationLowerBound, expirationUpperBound,
                                                            expirationUnitType) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    connection = create_connection("useritems.db")

    if connection is not None:
        insert_table(connection, sql_insert_user_table, item)
    else:
        print("Unable to create db connection.")


# Inserts category in categories table in categories.db file
def insert_category_table(category):
    sql_insert_category_table = """INSERT INTO categories (id, category) VALUES(?, ?)"""

    connection = create_connection("categories.db")

    if connection is not None:
        insert_table(connection, sql_insert_category_table, category)
    else:
        print("Unable to create db connection.")


# Inserts subcategory in subcategories table in subcategories.db file
def insert_subcategory_table(subcategory):
    sql_insert_subcategory_table = """INSERT INTO subcategories (id, subcategory) VALUES(?, ?)"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        insert_table(connection, sql_insert_subcategory_table, subcategory)
    else:
        print("Unable to create db connection.")


# Inserts storage_type in storagetype table in storagetypes.db
def insert_storage_type_table(storage_type):
    sql_insert_storage_type_table = """INSERT INTO storagetype (id, storagetype) VALUES(?, ?)"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        insert_table(connection, sql_insert_storage_type_table, storage_type)
    else:
        print("Unable to create db connection.")


# ----------------- UPDATE FUNCTIONS ----------------- #


# General function for updating information using the given sql code in specified table from db connection
def update_data(connection, update_sql, data):
    try:
        curs = connection.cursor()
        curs.execute(update_sql, data)
    except Error as err:
        print(err)


# Updates item in general_items table in expirations.db file
def update_general_table(item):
    sql_update_general_table = """ UPDATE general_items 
                                    SET id = ? ,
                                        category = ? ,
                                        subcategory = ? ,
                                        storageType = ? ,
                                        unopened = ? ,
                                        expirationLowerBound = ? ,
                                        expirationUpperBound = ? ,
                                        expirationUnitType = ?
                                    WHERE itemName = ?"""

    connection = create_connection("expirations.db")

    if connection is not None:
        insert_table(connection, sql_update_general_table, item)
    else:
        print("Unable to create db connection.")


# Updates item in user_items table in useritems.db file
def update_user_table(item):
    sql_update_user_table = """ UPDATE user_items 
                                        SET id = ? ,
                                            category = ? ,
                                            subcategory = ? ,
                                            storageType = ? ,
                                            unopened = ? ,
                                            expirationLowerBound = ? ,
                                            expirationUpperBound = ? ,
                                            expirationUnitType = ?
                                        WHERE itemName = ?"""

    connection = create_connection("useritems.db")

    if connection is not None:
        insert_table(connection, sql_update_user_table, item)
    else:
        print("Unable to create db connection.")


# Updates category in categories table in categories.db file
def update_category_table(category):
    sql_update_category_table = """UPDATE categories 
                                    SET category = ?
                                    WHERE id = ?"""

    connection = create_connection("categories.db")

    if connection is not None:
        insert_table(connection, sql_update_category_table, category)
    else:
        print("Unable to create db connection.")


# Updates subcategory in subcategories table in subcategories.db file
def update_subcategory_table(subcategory):
    sql_update_subcategory_table = """UPDATE subcategories 
                                    SET subcategory = ?
                                    WHERE id = ?"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        insert_table(connection, sql_update_subcategory_table, subcategory)
    else:
        print("Unable to create db connection.")


# Updates storage_type in storagetype table in storagetypes.db
def update_storage_type_table(storage_type):
    sql_update_storage_type_table = """UPDATE storagetype
                                    SET storagetype = ?
                                    WHERE id = ?"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        insert_table(connection, sql_update_storage_type_table, storage_type)
    else:
        print("Unable to create db connection.")


if __name__ == "__main__":
    create_general_table()
    create_user_table()
    create_storage_type_table()
    create_category_table()
    create_subcategory_table()
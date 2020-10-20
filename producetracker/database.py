import sqlite3
from sqlite3 import Error
import numpy as np
from datetime import datetime as dt, date, timedelta
import time
import os.path

# ----------------- HELPER FUNCTIONS ----------------- #


# General function that executes sql code given the connection and sql
# Optional parameter for data used in the query
# Optional parameter for not needing to execute a db commit (when not modifying data)
# Returns cursor on success, None otherwise
def execute_sql(connection, sql, data=None, commit=True):
    try:
        curs = connection.cursor()
        if data is None:
            curs.execute(sql)
        else:
            curs.execute(sql, data)
        if commit:
            connection.commit()
        return curs
    except Error as err:
        print(err)
        return None


# ----------------- CREATION FUNCTIONS ----------------- #


# Takes in the name of the db file and returns a connection to that db file.
def create_connection(db_file):
    connection = None

    try:
        connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), db_file))
        return connection
        # print(sqlite3.version) # can use to print version
    except Error as err:
        print(err)

    return connection


# Creates the general items table in the expirations.db file
def create_general_table():
    sql_create_general_items_table = """ CREATE TABLE IF NOT EXISTS general_items (
                                        itemName varchar,
                                        id integer NOT NULL PRIMARY KEY,
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
        execute_sql(connection, sql_create_general_items_table, commit=False)
    else:
        print("Unable to create expirations.db connection.")


# Creates the user items table in the useritems.db file
def create_user_table():
    sql_create_user_items_table = """ CREATE TABLE IF NOT EXISTS user_items (
                                    itemName varchar NOT NULL,
                                    id integer PRIMARY KEY,
                                    category integer NOT NULL,
                                    subcategory integer,
                                    storageType integer,
                                    unopened boolean,
                                    expirationLowerBound integer NOT NULL,
                                    expirationUpperBound integer,
                                    expirationUnitType varchar NOT NULL,
                                    expirationDate datetime NOT NULL
                                    );"""

    connection = create_connection("useritems.db")

    if connection is not None:
        execute_sql(connection, sql_create_user_items_table, commit=False)
    else:
        print("Unable to create useritems.db connection.")


# Creates the categories table in the categories.db file
def create_category_table():
    sql_create_category_table = """ CREATE TABLE IF NOT EXISTS categories (
                                    id integer PRIMARY KEY,
                                    category varchar NOT NULL
                                    );"""

    connection = create_connection("categories.db")

    if connection is not None:
        execute_sql(connection, sql_create_category_table, commit=False)
    else:
        print("Unable to create categories.db connection.")


# Creates the subcategories table in the subcategories.db file
def create_subcategory_table():
    sql_create_subcategory_table = """ CREATE TABLE IF NOT EXISTS subcategories(
                                        id integer PRIMARY KEY,
                                        subcategory varchar NOT NULL
                                    );"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        execute_sql(connection, sql_create_subcategory_table, commit=False)
    else:
        print("Unable to create subcategories.db connection.")


# Creates the storagetype table in the storagetypes.db file
def create_storage_type_table():
    sql_create_storage_type_table = """ CREATE TABLE IF NOT EXISTS storagetype(
                                        id integer PRIMARY KEY,
                                        storagetype varchar NOT NULL
                                    );"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        execute_sql(connection, sql_create_storage_type_table, commit=False)
    else:
        print("Unable to create storagetypes.db connection.")


# ----------------- INSERTION FUNCTIONS ----------------- #


# Inserts item in general_items table in expirations.db file
# Returns True on successful insertion, returns False otherwise
def insert_general_table(item):
    sql_insert_general_table = """ INSERT INTO general_items (itemName, id, category, subcategory, storageType,
                                                            unopened, expirationLowerBound, expirationUpperBound,
                                                            expirationUnitType) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    connection = create_connection("expirations.db")

    if connection is not None:
        return True if execute_sql(connection, sql_insert_general_table, item) is not None else False
    else:
        print("Unable to create expirations.db connection.")
        return False


# Inserts item in user_items table in useritems.db file
# Returns True on successful insertion, returns False otherwise
def insert_user_table(item):

    normal_days = 0

    if item[8] == 'Days' or item[8] == 'days':
        normal_days = item[6]
    elif item[8] == 'Weeks' or item[8] == 'weeks':
        normal_days = item[6] * 7
    elif item[8] == 'Months' or item[8] == 'months':
        normal_days = item[6] * 30
    elif item[8] == 'Years' or item[8] == 'years':
        normal_days = item[6] * 365

    expirationDate = date.today() + timedelta(days=normal_days)
    item = list(item)
    item.append(expirationDate)

    results = query_all_user_item()
    i = 0
    for res in results:
        if res[1] == i:
            i += 1
        else:
            break

    item[1] = i
    item = tuple(item)

    sql_insert_user_table = """INSERT INTO user_items (itemName, id, category, subcategory, storageType,
                                                            unopened, expirationLowerBound, expirationUpperBound,
                                                            expirationUnitType, expirationDate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    connection = create_connection("useritems.db")

    if connection is not None:
        return item[1] if execute_sql(connection, sql_insert_user_table, item) is not None else False
    else:
        print("Unable to create useritems.db connection.")
        return False


# Inserts category in categories table in categories.db file
# Returns True on successful insertion, returns False otherwise
def insert_category_table(category):
    sql_insert_category_table = """INSERT INTO categories (id, category) VALUES(?, ?)"""

    connection = create_connection("categories.db")

    if connection is not None:
        return True if execute_sql(connection, sql_insert_category_table, category) is not None else False
    else:
        print("Unable to create categories.db connection.")
        return False


# Inserts subcategory in subcategories table in subcategories.db file
# Returns True on successful insertion, returns False otherwise
def insert_subcategory_table(subcategory):
    sql_insert_subcategory_table = """INSERT INTO subcategories (id, subcategory) VALUES(?, ?)"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        return True if execute_sql(connection, sql_insert_subcategory_table, subcategory) is not None else False
    else:
        print("Unable to create subcategories.db connection.")
        return False


# Inserts storage_type in storagetype table in storagetypes.db
# Returns True on successful insertion, returns False otherwise
def insert_storage_type_table(storage_type):
    sql_insert_storage_type_table = """INSERT INTO storagetype (id, storagetype) VALUES(?, ?)"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        return True if execute_sql(connection, sql_insert_storage_type_table, storage_type) is not None else False
    else:
        print("Unable to create storagetypes.db connection.")
        return False


# ----------------- UPDATE FUNCTIONS ----------------- #


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
        return True if execute_sql(connection, sql_update_general_table, item) is not None else False
    else:
        print("Unable to create expirations.db connection.")
        return False


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
                                            expirationUnitType = ?,
                                            expirationDate = ?
                                        WHERE itemName = ?"""

    connection = create_connection("useritems.db")

    if connection is not None:
        return True if execute_sql(connection, sql_update_user_table, item) is not None else False
    else:
        print("Unable to create useritems.db connection.")
        return False


# Updates category in categories table in categories.db file
def update_category_table(category):
    sql_update_category_table = """UPDATE categories
                                    SET category = ?
                                    WHERE id = ?"""

    connection = create_connection("categories.db")

    if connection is not None:
        return True if execute_sql(connection, sql_update_category_table, category) is not None else False
    else:
        print("Unable to create categories.db connection.")
        return False


# Updates subcategory in subcategories table in subcategories.db file
def update_subcategory_table(subcategory):
    sql_update_subcategory_table = """UPDATE subcategories
                                    SET subcategory = ?
                                    WHERE id = ?"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        return True if execute_sql(connection, sql_update_subcategory_table, subcategory) is not None else False
    else:
        print("Unable to create subcategories.db connection.")
        return False


# Updates storage_type in storagetype table in storagetypes.db
def update_storage_type_table(storage_type):
    sql_update_storage_type_table = """UPDATE storagetype
                                    SET storagetype = ?
                                    WHERE id = ?"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        return True if execute_sql(connection, sql_update_storage_type_table, storage_type) is not None else False
    else:
        print("Unable to create storagetypes.db connection.")
        return False


# ----------------- QUERY FUNCTIONS ----------------- #


def query_all_user_item():
    sql_query_user_item = """SELECT * FROM user_items"""

    connection = create_connection("useritems.db")

    if connection is not None:
        curs = execute_sql(connection, sql_query_user_item, commit=False)
        results = curs.fetchall()
        return results
    else:
        print("Unable to create useritems.db connection.")
        return None


# Queries for a user_item based on if item id matches input
# Returns table results as 2d array from the query
def query_user_item_by_id(id):
    sql_query_user_item = """SELECT * FROM user_items WHERE id = ?"""

    connection = create_connection("useritems.db")

    if connection is not None:
        curs = execute_sql(connection, sql_query_user_item, (id,), commit=False)
        results = curs.fetchall()
        return results
    else:
        print("Unable to create useritems.db connection.")
        return None


# Queries for a user_item based on if item name contains input
# Returns
def query_user_item_by_name(name):
    sql_query_user_item = """SELECT * FROM user_items WHERE itemName LIKE '%'||?||'%'"""

    connection = create_connection("useritems.db")

    if connection is not None:
        curs = execute_sql(connection, sql_query_user_item, (name,), commit=False)
        results = curs.fetchall()
        return results
    else:
        print("Unable to create useritems.db connection.")
        return None


# ----------------- DELETE FUNCTIONS ----------------- #


# Deletes a user_item according to its id from useritems.db
def delete_user_item(id):
    sql_delete_user_item = """DELETE FROM user_items WHERE id = ?"""

    connection = create_connection("useritems.db")

    if connection is not None:
        return True if execute_sql(connection, sql_delete_user_item, (id,)) is not None else False
    else:
        print("Unable to create useritems.db connection.")
        return False


# Deletes all user_items in the table from useritems.db
def delete_all_user_items():
    sql_delete_all_items = """DELETE FROM user_items"""

    connection = create_connection("useritems.db")

    if connection is not None:
        return True if execute_sql(connection, sql_delete_all_items) is not None else False
    else:
        print("Unable to create useritems.db connection.")
        return False


# Deletes all general_items in the table from expirations.db
def delete_all_general_items():
    sql_delete_all_items = """DELETE FROM general_items"""

    connection = create_connection("expirations.db")

    if connection is not None:
        return True if execute_sql(connection, sql_delete_all_items) is not None else False
    else:
        print("Unable to create expirations.db connection.")
        return False


# Deletes all categories in the table from categories.db
def delete_all_categories():
    sql_delete_all_items = """DELETE FROM categories"""

    connection = create_connection("categories.db")

    if connection is not None:
        return True if execute_sql(connection, sql_delete_all_items) is not None else False
    else:
        print("Unable to create categories.db connection.")
        return False


# Deletes all subcategories in the table from subcategories.db
def delete_all_subcategories():
    sql_delete_all_items = """DELETE FROM general_items"""

    connection = create_connection("subcategories.db")

    if connection is not None:
        return True if execute_sql(connection, sql_delete_all_items) is not None else False
    else:
        print("Unable to create subcategories.db connection.")
        return False


# Deletes all storage types in the table from storagetypes.db
def delete_all_storage_types():
    sql_delete_all_items = """DELETE FROM storagetypes"""

    connection = create_connection("storagetypes.db")

    if connection is not None:
        return True if execute_sql(connection, sql_delete_all_items) is not None else False
    else:
        print("Unable to create storagetypes.db connection.")
        return False


def levenshtein(s, t):
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols), dtype = int)

    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 2
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
    return Ratio


def match_item(raw_item):
    sql_query_all_item = """SELECT * FROM general_items"""

    connection = create_connection("expirations.db")

    if connection is not None:
        curs = execute_sql(connection, sql_query_all_item, (), commit=False)
        results = curs.fetchall()
        max = -1
        curr = None
        for i in results:
            ratio = levenshtein(i[0], raw_item).item()
            if ratio > max:
                curr = i
                max = ratio
        return curr
    else:
        print("Unable to create expirations.db.")
        return None


if __name__ == "__main__":
    # create_general_table()
    create_user_table()

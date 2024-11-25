import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy import text


def get_next_id(conn, table_name, col_name):
    uids = []
    cursor = conn.execute(
        text("""SELECT MAX(""" + col_name + """) From """ + table_name)
    )
    for result in cursor:
        # can also be accessed using result[0]
        uids.append(result[0])
    cursor.close()
    max_id = uids[0]
    return int(max_id) + 1


def get_table_data(conn, table_name):
    data = []
    for row in conn.execute(text("""SELECT * FROM """ + str(table_name))):
        col_data = []
        for c in row:
            col_data.append(c)
        data.append(col_data)
    return data


def get_column_names(conn, table_name):
    result = conn.execute(text("""SELECT * FROM """ + str(table_name)))
    col_names = []
    for col in result.keys():
        col_names.append(col)
    return col_names


def get_all_table_names(metaData):
    names = []
    keys = metaData.tables.keys()
    for key in keys:
        names.append(key)
    return names

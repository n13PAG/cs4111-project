import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy import text


class CategoryHandler:
    # def __init__(self, connection, metaData):
    #     self.conn = connection
    #     self.metaData = metaData
    #     self.courses_table = metaData.tables["courses"]
    #     self.categories_table = metaData.tables["categories_held"]

    conn = None
    metaData = None
    courses_table = None
    categories_table = None

    def set(self, connection, metaData):
        self.conn = connection
        self.metaData = metaData
        self.courses_table = metaData.tables["courses"]
        self.categories_table = metaData.tables["categories_held"]

    def does_category_exist_name(self, name):
        cat_table = self.categories_table
        check_query = cat_table.select().where(cat_table.c.name_ == name)
        check_result = self.conn.execute(check_query)

        if check_result.rowcount > 0:
            return True
        else:
            return False

    def does_category_exist(self, id):
        cat_table = self.categories_table
        check_query = cat_table.select().where(cat_table.c.category_id == id)
        check_result = self.conn.execute(check_query)

        if check_result.rowcount > 0:
            return True
        else:
            return False

    def get_category(self, name):
        query = (
            """SELECT * FROM categories_held WHERE categories_held.name_ = """ + str(name) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_category(self, id):
        query = (
            """SELECT * FROM categories_held WHERE categories_held.category_id = """ + str(id) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_category_id(self, name):
        query = (
            """SELECT category_id FROM categories_held WHERE categories_held.category_id = """ + str(name) + """""")
        result = self.conn.execute(text(query))
        for r in result:
            return r.category_id

    def get_all_categories(self, cid):
        query = (
            """SELECT * FROM categories_held WHERE categories_held.cid = """ + str(cid) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_all_category_names(self, cid):
        result = self.get_all_categories(cid)
        names = []
        for r in result:
            names.append(r.name_)
        return names

    def add_category(self, name, description, cid):
        categories_table = self.categories_table
        query = insert(categories_table).values(
            name_=name,
            description=description,
            cid=cid,
        )
        result = self.conn.execute(query)
        self.conn.commit()

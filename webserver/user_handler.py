import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import helper_functions as ext


class UserHandler:
    # def __init__(self, connection, metaData):
    #     self.conn = connection
    #     self.metaData = metaData
    #     self.users_table = metaData.tables["users"]
    #     self.repos_owned = metaData.tables["repos_owned"]

    conn = None
    metaData = None
    users_table = None
    repos_owned = None

    def set(self, connection, metaData):
        self.conn = connection
        self.metaData = metaData
        self.users_table = metaData.tables["users"]
        self.repos_owned = metaData.tables["repos_owned"]

    def get_user(self, uid):
        query = (
            """SELECT * FROM users WHERE users.uid = """ + str(uid) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_uid_with_uni(self, uni):
        user_table = self.users_table
        check_query = user_table.select().where(user_table.c.uni == uni)
        check_result = self.conn.execute(check_query)
        for r in check_result:
            return r.uid

    def get_student(self, sid):
        query = (
            """SELECT * FROM users WHERE users.sid = """ + str(sid) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_professor(self, pid):
        query = (
            """SELECT * FROM users WHERE users.pid = """ + str(pid) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_all_students(self):
        query = (
            """SELECT * FROM users WHERE users.sid > 0 """)
        result = self.conn.execute(text(query))
        return result

    def get_all_professors(self):
        query = (
            """SELECT * FROM users WHERE users.pid > 0 """)
        result = self.conn.execute(text(query))
        return result

    def does_user_exist_uid(self, uid):
        user_table = self.users_table
        check_query = user_table.select().where(user_table.c.uid == uid)
        check_result = self.conn.execute(check_query)

        if check_result.rowcount > 0:
            return True
        else:
            return False

    def does_user_exist_uni(self, uni):
        user_table = self.users_table
        check_query = user_table.select().where(user_table.c.uni == uni)
        check_result = self.conn.execute(check_query)

        if check_result.rowcount > 0:
            return True
        else:
            return False

    def get_student_uid(self, sid):
        result = self.get_student(sid)
        for r in result:
            return r.uid

    def get_professor_uid(self, pid):
        result = self.get_professor(pid)
        for r in result:
            return r.uid

    def get_uni(self, uid):
        result = self.get_user(uid)
        for r in result:
            return r.uni

    def get_email(self, uid):
        result = self.get_user(uid)
        for r in result:
            return r.email

    def get_name(self, uid):
        result = self.get_user(uid)
        for r in result:
            return r.name

    def add_user(self, is_student, uni, email, name):
        if self.does_user_exist_uni(uni):
            return False
        else:
            uid = ext.get_next_id(self.conn, "users", "uid")

            if is_student:
                sid = ext.get_next_id(self.conn, "users", "sid")
                pid = None

                # create repos
                rid = ext.get_next_id(self.conn, "repos_owned", "rid")

                # Create personal repo
                query = insert(self.repos_table).values(
                    rid=rid,
                    total_note_num=0,
                    p_note_num=0,
                    np_note_num=0,
                    sid=sid,
                    nprid=None,
                    prid=rid + 1,
                )
                result = self.conn.execute(query)
                self.conn.commit()

                # Create external(liked notes repo)
                query = insert(self.repos_table).values(
                    rid=rid + 1,
                    total_note_num=0,
                    p_note_num=0,
                    np_note_num=0,
                    sid=sid,
                    nprid=rid + 2,
                    prid=None,
                )
                result = self.conn.execute(query)
                self.conn.commit()

            else:
                sid = None
                pid = ext.get_next_id(self.conn, "users", "pid")

            query = insert(self.users_table).values(
                uid=uid,
                sid=sid,
                pid=pid,
                uni=uni,
                email=email,
                name=name,
            )

            result = self.conn.execute(query)
            self.conn.commit()

            return True

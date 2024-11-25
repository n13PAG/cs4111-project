import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy import text


class CoursesHandler:
    # conn = None
    # metaData = None
    # courses_table = None
    # courses_created_table = None
    # categories_table = None
    def __init__(self) -> None:
        pass

    def set(self, connection, metaData):
        self.conn = connection
        self.metaData = metaData
        self.courses_table = metaData.tables["courses"]
        self.courses_created_table = metaData.tables["course_created"]
        self.categories_table = metaData.tables["categories_held"]
        self.students_enrolled_table = metaData.tables["student_enrolled"]

    def get_course_name(self, cid):
        query = (
            """SELECT courses.name FROM courses WHERE courses.cid = """ + str(cid) + """""")
        result = self.conn.execute(text(query))

        for r in result:
            return r.name

    def get_all_course_names(self):
        query = (""" SELECT courses.name FROM courses """)
        result = self.conn.execute(text(query))
        names = []
        for r in result:
            names.append(r.name)
        return names

    # def get_course_cid(self, name):
    #     query = (
    #         """SELECT courses.cid FROM courses WHERE courses.name = """ + str(name) + """""")
    #     query = self.courses_table.select().where(
    #         self.courses_table.c.name == name)
    #     result = self.conn.execute(text(query))
    #     for r in result:
    #         return r.cid

    def get_course_cid(self, name):
        # get cid
        course_table = self.courses_table
        cid_query = course_table.select().where(
            course_table.c.name == name
        )
        cid_result = self.conn.execute(cid_query)
        cid = -1
        for r in cid_result:
            cid = r.cid
        return cid

    def get_course(self, cid):
        query = (
            """SELECT * FROM courses WHERE courses.cid = """ + str(cid) + """""")
        result = self.conn.execute(text(query))
        return result

    def get_all_courses_by_prof(self, pid):
        query = (
            """SELECT * FROM courses, course_created WHERE courses.cid = course_created.cid AND course_created.pid = """ + str(pid) + """""")
        result = self.conn.execute(text(query))
        return result

    def does_course_exist_cid(self, cid):
        course_table = self.courses_table
        check_query = course_table.select().where(course_table.c.cid == cid)
        check_result = self.conn.execute(check_query)

        if check_result.rowcount > 0:
            return True
        else:
            return False

    def does_course_exist_name(self, name):
        course_table = self.courses_table
        check_query = course_table.select().where(course_table.c.name == name)
        check_result = self.conn.execute(check_query)

        if check_result.rowcount > 0:
            return True
        else:
            return False

    def add_course(self, cid, course_name, semester, year, pid):
        course_table = self.courses_table
        courses_created_table = self.courses_created_table
        categories_table = self.categories_table

        # insert into courses table
        query = insert(course_table).values(
            cid=cid, name=course_name, semester=semester, year=year
        )
        result = self.conn.execute(query)
        self.conn.commit()

        # insert into courses created table
        query = insert(courses_created_table).values(
            pid=pid, cid=cid)
        result = self.conn.execute(query)
        self.conn.commit()

        # Create general category for courses
        query = insert(categories_table).values(
            name_="General", description="A general category", cid=cid
        )
        result = self.conn.execute(query)
        self.conn.commit()

    def get_enrolled_student_count(self, cid):
        query = (
            """ SELECT COUNT(*) FROM student_enrolled WHERE student_enrolled.cid = """ + str(cid) + """""")
        result = self.conn.execute(text(query))
        return result.scalar()

    def get_enrolled_students(self):
        query = (
            """ SELECT * FROM student_enrolled, users WHERE student_enrolled.sid = """)
        result = self.conn.execute(text(query))
        return result

    def is_student_enrolled(self, sid, cid):
        query = (
            """ SELECT COUNT(*) FROM student_enrolled WHERE student_enrolled.sid = """ + str(sid) + """ AND student_enrolled.cid = """ + str(cid) + """ """)
        result = self.conn.execute(text(query))
        if result.scalar() == 0:
            return False
        else:
            return True

    def enroll_student(self, sid, cid):
        query = insert(self.students_enrolled_table).values(sid=sid, cid=cid)
        result = self.conn.execute(query)
        self.conn.commit()

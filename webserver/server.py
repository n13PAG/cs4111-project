#!/usr/bin/env python3

"""

Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import json
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash, jsonify
from flask import session
from sqlalchemy import text
from datetime import datetime
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_cors import CORS
from webforms import UserLoginForm
from webforms import SignUpForm
from webforms import UploadForm
from webforms import AddCourseForm
from webforms import AddCourseCategoryForm
from webforms import SearchForm
from webforms import SelectCourseForm
from webforms import UpvoteForm
from webforms import EnrollForm

# handlers
from course_handler import CoursesHandler
from category_handler import CategoryHandler
from user_handler import UserHandler
from user import User
import helper_functions as ext

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=tmpl_dir)
CORS(app)

# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "vo2195"
DB_PASSWORD = "vo2195"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://" + DB_USER + ":" + \
    DB_PASSWORD + "@" + DB_SERVER + "/w4111"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)
engine.connect()
metaData = MetaData()
metaData.reflect(bind=engine)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "for dev")
app.config.update(PERMANENT_SESSION_LIFETIME=600)

# setup login manager
login_manager = LoginManager()
login_manager.init_app(app)


user_handler = UserHandler()
course_handler = CoursesHandler()
category_handler = CategoryHandler()


def set_handlers(conn, metaData):
    user_handler.set(conn, metaData)
    course_handler.set(conn, metaData)
    category_handler.set(conn, metaData)
    # UserHandler.set(conn, metaData)
    # CoursesHandler.set(conn, metaData)
    # CategoryHandler.set(conn, metaData)


@login_manager.user_loader
def load_user(user_id):
    set_handlers(g.conn, metaData)
    if user_handler.does_user_exist_uid(user_id):
        user = user_handler.get_user(user_id)
        for r in user:
            return User(user_id, r.sid, r.pid, r.name, r.email)
    else:
        return None


def create_user_instance(uid):
    set_handlers(g.conn, metaData)
    user = user_handler.get_user(uid)
    for r in user:
        return User(uid, r.sid, r.pid, r.name, r.email)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()

        # set connection in classes
        set_handlers(g.conn, metaData)

    except:
        print("uh oh, problem connecting to database")
        import traceback

        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/register_request', methods=['POST'])
def register_user():
    set_handlers(g.conn, metaData)

    data = request.get_json()

    next_id = ext.get_next_id(g.conn, "users", "uid")
    u_sid = ext.get_next_id(g.conn, "users", "sid")
    u_pid = None
    u_uni = 'zy5566'
    u_name = data['username']
    u_email = data["email"]

    user_table = metaData.tables['users']
    query = insert(user_table).values(
        uid=next_id,
        sid=u_sid,
        pid=u_pid,
        uni=u_uni,
        email=u_email,
        name=u_name,
    )

    # user_handler.add_user(True, u_uni, u_email, u_name)

    result = g.conn.execute(query)
    g.conn.commit()

    # print(data["email"])
    # print(data["jdata"])
    # print(json.dumps(data))
    # pdata = json.loads(data)
    # print(pdata)
    # print(data['username'])
    # return jsonify({"result": "success"})
    return data


@app.route('/test', methods=['GET'])
def get_test():
    return jsonify({"message": "Check"})

@app.route('/testCourses', methods=['GET'])
def get_courses_test():
    set_handlers(g.conn, metaData)
    course_names = course_handler.get_all_course_names()
    return jsonify({"courses":course_names})

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    set_handlers(g.conn, metaData)

    # get form
    form = SignUpForm()

    # init error
    error = None

    if request.method == "POST":
        # Validation
        if form.validate_on_submit():
            # get form data
            u_uni = form.uni.data
            u_email = form.email.data
            u_name = form.name.data
            is_student = form.is_student.data

            # # get num section from uni
            # u_id = int(u_uni[len(u_uni) - 4:])

            # get user table
            user_table = metaData.tables["users"]

            # Check if user with the uni entered exists
            check_query = user_table.select().where(user_table.c.uni == u_uni)
            check_result = g.conn.execute(check_query)

            if check_result.rowcount > 0:
                error = "User already exists."
                return render_template("signup.html", error=error, form=form)
            else:
                u_pid = null
                u_sid = null

                # set pid or sid based on user type
                if is_student:
                    u_pid = None

                    u_sid = ext.get_next_id("users", "sid")
                else:
                    u_pid = ext.get_next_id("users", "pid")
                    u_sid = None

                # uids = []
                # cursor = g.conn.execute(text("""SELECT MAX(uid) From users"""))
                # for result in cursor:
                #     # can also be accessed using result[0]
                #     uids.append(result[0])
                # cursor.close()
                # max_id = uids[0]
                # next_id = int(max_id) + 1

                next_id = ext.get_next_id("users", "uid")

                query = insert(user_table).values(
                    uid=next_id,
                    sid=u_sid,
                    pid=u_pid,
                    uni=u_uni,
                    email=u_email,
                    name=u_name,
                )

                result = g.conn.execute(query)
                g.conn.commit()

            # create repos if new user is a student
            if is_student:
                # get table
                repos_table = metaData.tables["repos_owned"]

                rids = []
                cursor = g.conn.execute(
                    text("""SELECT MAX(rid) From repos_owned"""))
                for result in cursor:
                    # can also be accessed using result[0]
                    rids.append(result[0])
                cursor.close()
                max_id = rids[0]
                next_id = int(max_id) + 1

                # Create personal repo
                query = insert(repos_table).values(
                    rid=next_id,
                    total_note_num=0,
                    p_note_num=0,
                    np_note_num=0,
                    sid=u_sid,
                    nprid=None,
                    prid=next_id + 1,
                )
                result = g.conn.execute(query)
                g.conn.commit()

                # Create external(liked notes repo)
                query = insert(repos_table).values(
                    rid=next_id + 1,
                    total_note_num=0,
                    p_note_num=0,
                    np_note_num=0,
                    sid=u_sid,
                    nprid=next_id + 2,
                    prid=None,
                )
                result = g.conn.execute(query)
                g.conn.commit()

            flash("Account Created")
            return redirect(url_for("login"))
        else:
            error = "Invalid Input. Please try again."

    return render_template("signup.html", error=error, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    set_handlers(g.conn, metaData)

    form = UserLoginForm()
    error = None

    if request.method == "POST":
        # Validation
        if form.validate_on_submit():
            user_table = metaData.tables["users"]
            uni_query = user_table.select().where(user_table.c.uni == form.uni.data)
            result = g.conn.execute(uni_query)
            print(result.first())
            # if no row, then no uni exists as a user
            if result.rowcount == 0:
                error = "Invalid Credentials. Please try again."
            else:

                email_check = user_table.select().where(
                    user_table.c.email == form.email.data, user_table.c.uni == form.uni.data)
                result = g.conn.execute(email_check)

                if result.rowcount == 0:
                    error = "Invalid Credentials. Please try again."
                else:
                    uid = user_handler.get_uid_with_uni(form.uni.data)
                    user = create_user_instance(uid)
                    login_user(user)
                    return redirect(url_for("dashboard", user=form.uni.data))
        else:
            error = "Invalid Input. Please try again."

    return render_template("login.html", form=form, error=error)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    set_handlers(g.conn, metaData)
    if current_user.is_student():
        return student_dashboard()
    else:
        return professor_dashboard()


def professor_dashboard():

    uid = current_user.get_id()
    user = user_handler.get_user(uid)
    pid = -1
    for r in user:
        pid = r.pid
    result = course_handler.get_all_courses_by_prof(pid)

    courses = []
    for r in result:
        count = course_handler.get_enrolled_student_count(r.cid)
        courses.append([r.cid, r.name, count, r.semester, r.year])

    return render_template("prof_dashboard.html", courses=courses)


def student_dashboard():
    return render_template("stud_dashboard.html")


@app.route("/addcourse", methods=["GET", "POST"])
@login_required
def add_course():
    set_handlers(g.conn, metaData)
    if request.method == "GET":
        form = AddCourseForm()
        return render_template(
            "addcourse.html",
            error=None,
            form=form,
        )
    elif request.method == "POST":
        form = AddCourseForm()
        cid = form.cid.data
        name = form.course_name.data
        semester = form.semester.data
        year = form.year.data

        if form.validate_on_submit():
            user = user_handler.get_professor(current_user.get_id())
            pid = -1
            for r in user:
                pid = r.pid

            if course_handler.does_course_exist_name(name):
                error = "Course already exists"
                return render_template(
                    "addcourse.html",
                    error=error,
                    form=form,
                )
            else:
                course_handler.add_course(cid, name, semester, year, pid)
                error = None
                return render_template(
                    "addcourse.html",
                    error=error,
                    form=form,
                )


@app.route('/addcategory', methods=["GET", "POST"])
@login_required
def add_category():
    set_handlers(g.conn, metaData)
    if request.method == "GET":
        form = AddCourseCategoryForm()
        return render_template(
            "addcategory.html",
            error=None,
            form=form,
        )
    elif request.method == "POST":
        form = AddCourseCategoryForm()

        if form.validate_on_submit():
            if course_handler.does_course_exist_cid(form.cid.data) and course_handler.does_course_exist_name(form.course_name.data):

                cid = form.cid.data
                course_name = form.course_name.data
                category_name = form.category_name.data
                category_description = form.category_description.data

                if category_handler.does_category_exist_name(category_name):
                    error = "Category with this name already exists"
                    return render_template(
                        "addcategory.html",
                        error=error,
                        form=form,
                    )
                else:
                    category_handler.add_category(
                        category_name, category_description, cid)
                    return render_template(
                        "addcategory.html",
                        error=None,
                        form=form,
                    )

            else:
                error = 'Course does not exist'
                return render_template(
                    "addcategory.html",
                    error=error,
                    form=form,
                )


@app.route('/enroll', methods=["GET", "POST"])
@login_required
def enroll():
    set_handlers(g.conn, metaData)

    if request.method == "GET":
        form = EnrollForm()

        course_names = course_handler.get_all_course_names()
        form.course_name.choices = course_names

        return render_template("enroll.html", error=None, form=form)
    elif request.method == "POST":

        form = EnrollForm()

        course_names = course_handler.get_all_course_names()
        form.course_name.choices = course_names

        if form.validate_on_submit():
            uid = current_user.get_id()
            user = user_handler.get_user(uid)

            sid = -1
            for r in user:
                sid = r.sid

            cid = course_handler.get_course_cid(form.course_name.data)

            if course_handler.is_student_enrolled(sid, cid):
                error = "You are already enrolled in the courses"
                return render_template("enroll.html", error=error, form=form)
            else:
                course_handler.enroll_student(sid, cid)
                return render_template("enroll.html", error=None, form=form)


@app.route('/uploadnote', methods=["GET", "POST"])
@login_required
def upload_note():
    set_handlers(g.conn, metaData)

    uid = current_user.get_id()
    user = user_handler.get_user(uid)

    sid = -1
    for r in user:
        sid = r.sid

    if request.method == 'GET':
        form = UploadForm()

        course_names = course_handler.get_all_course_names()
        form.course_name.choices = course_names

        if form.course_name.data:
            # get cid
            course_table = metaData.tables["courses"]
            cid_query = course_table.select().where(
                course_table.c.name == form.course_name.data
            )
            cid_result = g.conn.execute(cid_query)
            cid = -1
            for r in cid_result:
                cid = r.cid

            result = category_handler.get_all_category_names(cid)
            form.category_name.choices = result

        return render_template("uploadnote.html", error=None, form=form)
    elif request.method == 'POST':
        form = UploadForm()

        course_names = course_handler.get_all_course_names()
        form.course_name.choices = course_names

        if form.course_name.data:
            # get cid
            course_table = metaData.tables["courses"]
            cid_query = course_table.select().where(
                course_table.c.name == form.course_name.data
            )
            cid_result = g.conn.execute(cid_query)
            cid = -1
            for r in cid_result:
                cid = r.cid

            result = category_handler.get_all_category_names(cid)
            form.category_name.choices = result

            if form.validate_on_submit():
                text = form.file_link.data
                category_name = form.category_name.data
                date = datetime.now()

                # get category id
                categories_held = metaData.tables["categories_held"]
                cat_query = categories_held.select().where(
                    categories_held.c.name_ == category_name
                )
                result = g.conn.execute(cat_query)

                category_id = 0
                for r in result:
                    category_id = r.category_id

                # insert note into uploads table
                uploads_table = metaData.tables["uploads"]
                uploads_query = insert(uploads_table).values(
                    sid=sid, content=text, upvotes=0, upload_date=date
                )
                result = g.conn.execute(uploads_query)
                g.conn.commit()

                # get note id of note that just got added
                note_id = ext.get_next_id(
                    g.conn, """uploads""", """note_id""") - 1

                # insert note into belongs table
                belongs_table = metaData.tables["belongs"]
                belongs_query = insert(belongs_table).values(
                    note_id=note_id, category_id=category_id
                )
                result = g.conn.execute(belongs_query)
                g.conn.commit()

                # get rid of personal repo using sid
                repos_owned_table = metaData.tables["repos_owned"]
                repos_query = repos_owned_table.select().where(
                    repos_owned_table.c.sid == sid
                )
                result = g.conn.execute(repos_query)

                # personal repo rid
                rid_p = -1
                # external repo rid
                rid_n = -1

                # TODO: Add check for when there is no repo
                rid = -1
                for r in result:
                    if r.nprid == None:
                        rid = r.rid
                        rid_p = r.rid
                    if r.prid == None:
                        rid_n = r.rid

                    # add note to notes contained table
                note_contained_table = metaData.tables["note_contained"]
                note_contained_query = insert(note_contained_table).values(
                    note_id=note_id, rid=rid, content=text, upvotes=0, upload_date=date
                )
                result = g.conn.execute(note_contained_query)
                g.conn.commit()

                from sqlalchemy import text

                print(rid_p)
                print(rid_p)
                query = (
                    """
                        UPDATE repos_owned
                        SET total_note_num = total_note_num + 1, p_note_num = p_note_num + 1
                        WHERE rid ="""
                    + str(rid_p)
                    + """;

                        UPDATE repos_owned
                        SET total_note_num = total_note_num + 1, np_note_num = np_note_num + 1
                        WHERE rid ="""
                    + str(rid_n)
                    + """ ;
                        """
                )

                result = g.conn.execute(text(query))
                g.conn.commit()

                print("Uploaded")

                return render_template(
                    "uploadnote.html", error=None, form=form
                )
            else:
                return render_template(
                    "uploadnote.html", error="Error with input", form=form
                )


@app.route('/get_categories', methods=["GET", "POST"])
def get_categories():
    course_name = request.args.get("course_name")
    # get cid
    course_table = metaData.tables["courses"]
    cid_query = course_table.select().where(
        course_table.c.name == course_name
    )
    cid_result = g.conn.execute(cid_query)
    cid = -1
    for r in cid_result:
        cid = r.cid

    result = category_handler.get_all_categories(cid)

    categories = []
    for r in result:
        categories.append([r.category_id, r.name_])

    return render_template("category_options.html", categories=categories)


@app.route('/search', methods=["GET", "POST"])
@login_required
def search_notes():
    set_handlers(g.conn, metaData)

    search_form = SearchForm()
    course_names = course_handler.get_all_course_names()
    search_form.course_name.choices = course_names

    if request.method == "GET":
        return render_template("search.html", form=search_form)
    elif request.method == "POST":
        course_name = search_form.course_name.data

        # get cid
        course_table = metaData.tables["courses"]
        cid_query = course_table.select().where(
            course_table.c.name == course_name
        )
        cid_result = g.conn.execute(cid_query)
        cid = -1
        for r in cid_result:
            cid = r.cid

        categories_table = metaData.tables["categories_held"]

        course_category_join = (
            """
                        WITH course_cat(category_id, category_name, category_description) AS (
                        SELECT categories_held.category_id, categories_held.name_, categories_held.description
                        FROM (SELECT * FROM courses WHERE cid = """
            + str(cid)
            + """) AS select_course, categories_held
                        WHERE select_course.cid = categories_held.cid
                        ),
                        belong_join (note_id, category_id, category_name, category_description) AS (
                        SELECT belongs.note_id, course_cat.category_id, course_cat.category_name, course_cat.category_description
                        FROM course_cat, belongs
                        WHERE course_cat.category_id = belongs.category_id
                        ),
                        uploads_join (note_id, link, category_name, upvotes, upload_date) AS (
                            SELECT DISTINCT note_contained.note_id, note_contained.content, dj.category_name, note_contained.upvotes, note_contained.upload_date
                            FROM note_contained
                            INNER JOIN (SELECT DISTINCT note_id, category_name FROM belong_join) dj
                            ON dj.note_id = note_contained.note_id
                        )

                        SELECT DISTINCT *, COUNT(note_id) FROM uploads_join GROUP BY note_id, link, category_name, upvotes, upload_date

                        """
        )
        cursor = g.conn.execute(text(course_category_join))

        rows = []
        for result in cursor:
            # can also be accessed using result[0]
            data = []
            for r in result:
                print(r)
                data.append(r)
            rows.append(data)
        cursor.close()

        # # # return rows
        # return rows

        return render_template("search.html", form=search_form, data=rows)


@app.route('/like_post/<note_id>', methods=["GET"])
def like_post(note_id):
    set_handlers(g.conn, metaData)

    uid = current_user.get_id()
    user = user_handler.get_user(uid)

    sid = -1
    for r in user:
        sid = r.sid
    if was_note_liked_by_user(sid, note_id):
        remove_like(sid, note_id)
    else:
        like_note(sid, note_id)

    return redirect(url_for('search_notes'))


def get_all_notes_in_repo(sid):
    query = ("""
        WITH my_repo(rid, sid) AS (
            SELECT repos_owned.rid, repos_owned.sid
            FROM repos_owned
            WHERE repos_owned.sid = """ + str(sid) + """ AND repos_owned.prid >= 0 
        ),
        notes_in_repo(note_id, rid, sid, content, upvotes, upload_date) AS (
            SELECT note_contained.note_id, my_repo.rid, my_repo.sid, note_contained.content, note_contained.upvotes, note_contained.upload_date
            FROM note_contained, my_repo
            WHERE note_contained.rid = my_repo.rid
        ),
        note_data(note_id, rid, content, upvotes, upload_date, category_id, category_name, category_description, course_id, course_name, semester, year) AS (
            SELECT notes_in_repo.note_id, notes_in_repo.rid, notes_in_repo.content, notes_in_repo.upvotes, notes_in_repo.upload_date, belongs.category_id, categories_held.name_, categories_held.description, courses.cid, courses.name, courses.semester, courses.year
            FROM notes_in_repo, belongs, categories_held, courses
            WHERE notes_in_repo.note_id = belongs.note_id AND belongs.category_id = categories_held.category_id AND categories_held.cid = courses.cid
        )

        SELECT * FROM note_data
    """)

    result = g.conn.execute(text(query))
    data = []
    for r in result:
        col = []
        for c in r:
            col.append(c)
        data.append(col)
    return data


def get_all_liked_notes(sid):
    query = ("""
        WITH my_repo(rid, sid) AS (
            SELECT repos_owned.rid, repos_owned.sid
            FROM repos_owned
            WHERE repos_owned.sid = """ + str(sid) + """ AND repos_owned.nprid >= 0 
        ),
        notes_in_repo(note_id, rid, sid, content, upvotes, upload_date) AS (
            SELECT note_contained.note_id, my_repo.rid, my_repo.sid, note_contained.content, note_contained.upvotes, note_contained.upload_date
            FROM note_contained, my_repo
            WHERE note_contained.rid = my_repo.rid
        ),
        note_data(note_id, rid, content, upvotes, upload_date, category_id, category_name, category_description, course_id, course_name, semester, year) AS (
            SELECT notes_in_repo.note_id, notes_in_repo.rid, notes_in_repo.content, notes_in_repo.upvotes, notes_in_repo.upload_date, belongs.category_id, categories_held.name_, categories_held.description, courses.cid, courses.name, courses.semester, courses.year
            FROM notes_in_repo, belongs, categories_held, courses
            WHERE notes_in_repo.note_id = belongs.note_id AND belongs.category_id = categories_held.category_id AND categories_held.cid = courses.cid
        )

        SELECT * FROM note_data
    """)

    query = ("""
        WITH my_repo(rid, sid) AS (
            SELECT repos_owned.rid, repos_owned.sid
            FROM repos_owned
            WHERE repos_owned.sid = """ + str(sid) + """ AND repos_owned.nprid >= 0 
        ),
        notes_in_repo(note_id, rid, sid, content, upvotes, upload_date) AS (
            SELECT note_contained.note_id, my_repo.rid, my_repo.sid, note_contained.content, note_contained.upvotes, note_contained.upload_date
            FROM note_contained, my_repo
            WHERE note_contained.rid = my_repo.rid
        )
        SELECT * FROM notes_in_repo
    """)

    result = g.conn.execute(text(query))
    data = []
    for r in result:
        col = []
        for c in r:
            col.append(c)
        data.append(col)
    return data


def like_note(sid, note_id):
    student_likes_table = metaData.tables["student_likes"]

    # add to student likes table
    like_query = insert(student_likes_table).values(sid=sid, note_id=note_id)
    result = g.conn.execute(like_query)
    g.conn.commit()

    # update upvote counter in uploads and note_contained
    upvotes_query = (
        """
                        UPDATE note_contained
                        SET upvotes = upvotes + 1
                        WHERE note_id ="""
        + str(note_id)
        + """ ;
                        UPDATE uploads
                        SET upvotes = upvotes + 1
                        WHERE note_id ="""
        + str(note_id)
        + """ ;
                    """
    )
    result = g.conn.execute(text(upvotes_query))
    g.conn.commit()


def was_note_liked_by_user(sid, note_id):
    student_likes_table = metaData.tables["student_likes"]
    query = student_likes_table.select().where(student_likes_table.c.note_id ==
                                               note_id, student_likes_table.c.sid == sid)
    result = g.conn.execute(query)
    count = 0
    for r in result:
        count += 1

    if count == 0:
        return False
    else:
        return True


def remove_like(sid, note_id):
    student_likes_table = metaData.tables["student_likes"]
    if was_note_liked_by_user(sid, note_id):

        # remove from student likes table
        stmt = delete(student_likes_table).where(
            student_likes_table.c.note_id == note_id, student_likes_table.c.sid == sid)
        result = g.conn.execute(stmt)
        g.conn.commit()

        # update upvote counter in uploads and note_contained
        upvotes_query = (
            """
                        UPDATE note_contained
                        SET upvotes = upvotes - 1
                        WHERE note_id ="""
            + str(note_id)
            + """ ;
                        UPDATE uploads
                        SET upvotes = upvotes - 1
                        WHERE note_id ="""
            + str(note_id)
            + """ ;
                    """
        )
        result = g.conn.execute(text(upvotes_query))
        g.conn.commit()


def count_upvotes(note_id):
    query = (""" 
        SELECT COUNT(note_id)
        FROM student_likes
        WHERE note_id = """ + str(note_id) + """
    """)

    result = g.conn.execute(text(query))

    return result.scalar()


@app.route("/display_tables")
def debug_display():
    table_names = []
    table_names.append("users")
    table_names.append("courses")
    table_names.append("course_created")
    table_names.append("categories_held")
    table_names.append("student_enrolled")
    table_names.append("belongs")
    table_names.append("uploads")
    table_names.append("repos_owned")
    table_names.append("note_contained")
    table_names.append("student_likes")

    table_col_names = []
    for name in table_names:
        table_col_names.append(ext.get_column_names(g.conn, name))

    tables_dict = []
    for name in table_names:
        tables_dict.append(
            [name, ext.get_column_names(g.conn, name), ext.get_table_data(g.conn, name)])

    return render_template("debug.html", tables_dict=tables_dict)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--debug", is_flag=True)
    @click.option("--threaded", is_flag=True)
    @click.argument("HOST", default="0.0.0.0")
    @click.argument("PORT", default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

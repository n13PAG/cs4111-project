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
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash
from flask import session
from sqlalchemy import text
from flask_login import UserMixin, LoginManager
from webforms import UserLoginForm
from webforms import SignUpForm
from webforms import UploadForm
from webforms import AddCourseForm

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=tmpl_dir)


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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route("/")
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)
    print("index")

    #
    # example of a database query
    #
    names = []
    cursor = g.conn.execute(text("""SELECT name From users"""))
    for result in cursor:
        names.append(result[0])  # can also be accessed using result[0]
    cursor.close()
    print(names[0])

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
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

            # get num section from uni
            u_id = int(u_uni[len(u_uni) - 4:])

            # get user table
            user_table = metaData.tables["users"]

            # Check if user with the uni entered exists
            check_query = user_table.select().where(user_table.c.uni == u_uni)
            check_result = g.conn.execute(check_query)

            if check_result.rowcount > 0:
                error = "User taken. Please enter new ."
                return render_template("signup.html", error=error, form=form)
            else:
                u_pid = null
                u_sid = null

                # set pid or sid based on user type
                if is_student:
                    u_pid = None
                    u_sid = u_id
                else:
                    u_pid = u_id
                    u_sid = None

                uids = []
                cursor = g.conn.execute(text("""SELECT MAX(uid) From users"""))
                for result in cursor:
                    # can also be accessed using result[0]
                    uids.append(result[0])
                cursor.close()
                max_id = uids[0]
                next_id = int(max_id) + 1

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

                # Create personal repo
                query = insert(repos_table).values(
                    rid=0,
                    total_note_num=0,
                    p_note_num=0,
                    np_note_num=0,
                    sid=u_sid,
                    nprid=None,
                    prid=0,
                )
                result = g.conn.execute(query)
                g.conn.commit()

                # Create external(liked notes repo)
                query = insert(repos_table).values(
                    rid=1,
                    total_note_num=0,
                    p_note_num=0,
                    np_note_num=0,
                    sid=u_sid,
                    nprid=0,
                    prid=None,
                )
                result = g.conn.execute(query)
                g.conn.commit()

            flash('Account Created')
            return redirect(url_for("login"))
        else:
            error = "Invalid Input. Please try again."

    return render_template("signup.html", error=error, form=form)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#


@app.route("/another")
def another():
    return render_template("anotherfile.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    from sqlalchemy import text

    notes = []
    cursor = g.conn.execute(text("""SELECT (note_id,content) FROM uploads"""))
    for result in cursor:
        notes.append(result[0])  # can also be accessed using result[0]
    cursor.close()
    print(notes)

    if request.method == "GET":
        user = request.args["user"]
        user_table = metaData.tables["users"]
        uni_query = user_table.select().where(user_table.c.uni == user)
        result = g.conn.execute(uni_query)

        for r in result:
            if r.pid == None:
                session["user_uni"] = r.uni
                form = UploadForm()

                # if form.validate_on_submit():
                #   u_sid = r.sid
                #   text = form.file_link.data
                #   print(u_sid)
                #   print(text)
                #   uploads_table = metaData.tables['uploads']
                #   uploads_query = insert(uploads_table).values(sid=u_sid, content=text, upvotes = 0, upload_date = None )
                #   result = g.conn.execute(uploads_query)
                #   g.conn.commit()

                #   print(select(uploads_table))
                # result = g.conn.execute(uploads_query)
                # for u in result:
                #   print(u)

                return render_template(
                    "dashboard.html", form=form, is_student=True, is_professor=False
                )
            elif r.sid == None:
                session["user_uni"] = r.uni
                form = AddCourseForm()
                return render_template(
                    "dashboard.html", form=form, is_student=False, is_professor=True
                )

    elif request.method == "POST":
        user = session["user_uni"]
        user_table = metaData.tables["users"]
        uni_query = user_table.select().where(user_table.c.uni == user)
        result = g.conn.execute(uni_query)

        for r in result:
            if r.pid == None:
                form = UploadForm()
                print("Link that was saved:")
                # print(form.file_link.data)

                if form.validate_on_submit():
                    u_sid = r.sid
                    text = form.file_link.data
                    # print(u_sid)
                    # print(text)
                    uploads_table = metaData.tables["uploads"]
                    uploads_query = insert(uploads_table).values(
                        sid=u_sid, content=text, upvotes=0, upload_date=None
                    )
                    result = g.conn.execute(uploads_query)
                    g.conn.commit()

                    return render_template(
                        "dashboard.html", form=form, is_student=True, is_professor=False
                    )
            elif r.sid == None:
                form = AddCourseForm()
                return render_template(
                    "dashboard.html", form=form, is_student=False, is_professor=True
                )

        # if r.sid == None:
        # return redirect(url_for('prof_dashboard', user = r, is_student = False, is_professor = True))
    #     form = None
    #     return render_template('dashboard.html', form = form, is_student = False, is_professor = True)
    #   elif r.pid == None:
    #     print(r.sid)
    #     form = UploadForm()
    #     # print(form.file_link.data)
    #     # if request.method == 'POST':
    #       # if form.validate_on_submit():
    #         # u_sid = r.sid
    #         # text = form.file_link.data
    #         # print(u_sid)
    #         # print(text)
    #         # uploads_table = metaData.tables['uploads']
    #         # uploads_query = insert(uploads_table).values(sid=u_sid, content=text, upvotes = 0, upload_date = None )
    #         # result = g.conn.execute(uploads_query)
    #         # g.conn.commit()

    #     return render_template('dashboard.html', form = form, is_student = True, is_professor = False)

    # return redirect(url_for('stud_dashboard', student_user = r))

    return "text"
    # if user.sid == None:
    #   redirect(url_for('prof_dashboard()'))
    # elif user.pid == None:
    #   redirect(url_for('stud_dashboard'))


# professordashboard
# @app.route('/prof_dashboard', methods=['GET','POST'])
# def prof_dashboard():
#   form = AddCourseForm()

#   if request.method == 'POST':
#     if form.validate_on_submit():
#       user = request.args['user']
#       cid = form.cid.data
#       course_name = form.course_name.data
#       semester = form.semester.data
#       year = form.year.data

#       # cursor = g.conn.execute(text("""SELECT MAX(note_id) FROM courses"""))

#       courses_table = metaData.tables['courses']
#       query = insert(courses_table).values(cid=cid, name=course_name, semester=semester, year=year)
#       result = g.conn.execute(query)
#       g.conn.commit()

#       courses_created_table = metaData.tables['course_created']
#       query = insert(courses_created_table).values(sid = user.sid, cid=cid)
#       result = g.conn.execute(query)
#       g.conn.commit()

#       query = courses_table.select()
#       result = g.conn.execute(query)
#       for r in result:
#         print(r)

#   return render_template('prof_dashboard.html', form = form)

# studentdashboard
# @app.route('/stud_dashboard', methods=['GET','POST'])
# def stud_dashboard():
#   form = UploadForm()

#   if request.method == 'POST':
#     if form.validate_on_submit():
#       print(session['test'])
#       print("Hello")
# print(student_user)
# print(request.form['test_var'])
# for r in request.args:
#   print(r)

# user = request.args['student_user']
# u_sid = user.sid
# text = form.file_link.data
# print(u_sid)
#   print(text)
# uploads_table = metaData.tables['uploads']
# uploads_query = insert(uploads_table).values(sid=u_sid, content=text, upvotes = 0, upload_date = None )
# result = g.conn.execute(uploads_query)
# g.conn.commit()

# return render_template('stud_dashboard.html', form = form)


# Example of adding new data to the database
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    print(text(name))
    return redirect("/")


# Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#       user_table = metaData.tables['users']
#       uni_query = user_table.select().where(user_table.c.uni == request.form['uni'])
#       result = g.conn.execute(uni_query)
#       uni = result.fetchone()
#       #if no row, then no uni exists as a user
#       if result.rowcount == 0:
#         error = 'Invalid Credentials. Please try again.'
#       else:
#         return redirect(url_for('tbd'))
#     return render_template('login.html', error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
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
                return redirect(url_for("dashboard", user=form.uni.data))
        else:
            error = "Invalid Input. Please try again."

    return render_template("login.html", form=form, error=error)


# Custom error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


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

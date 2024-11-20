from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateField,
    IntegerField,
    EmailField,
    PasswordField,
    BooleanField,
    SelectField,
    SubmitField,
    FileField,
)
from wtforms import validators
from flask_mdeditor import MDEditorField


class UserLoginForm(FlaskForm):
    email = EmailField("Email address", [
                       validators.DataRequired(), validators.Email()])
    uni = StringField(
        "UNI", [validators.DataRequired(), validators.Length(min=6, max=6)]
    )
    submit = SubmitField("Login")


class SignUpForm(FlaskForm):
    email = EmailField("Email address", [
                       validators.DataRequired(), validators.Email()])
    uni = StringField(
        "UNI", [validators.DataRequired(), validators.Length(min=6, max=6)]
    )
    name = StringField("Full name", [validators.DataRequired()])
    is_student = BooleanField("Are you a student")
    submit = SubmitField("Sign Up")


class AddCourseForm(FlaskForm):
    # TODO: Must change cid in database to be text
    cid = IntegerField("Course ID", [validators.DataRequired()])
    course_name = StringField("Course Name", [validators.DataRequired()])
    semester = SelectField(
        "Semester",
        choices=[("FALL", "FALL"), ("SPRING", "SPRING"), ("SUMMER", "SUMMER")],
    )
    year = IntegerField("Year", [validators.DataRequired()])
    submit = SubmitField("Add Course")


class AddCourseCategoryForm(FlaskForm):
    cid = IntegerField("Course ID", [validators.DataRequired()])
    course_name = StringField("Course Name", [validators.DataRequired()])
    category_name = StringField("Category Name", [validators.DataRequired()])
    category_description = StringField(
        "Category Description", [validators.DataRequired()]
    )
    submit = SubmitField("Submit")


class UploadForm(FlaskForm):
    file_link = StringField("PDF link", [validators.DataRequired()])
    submit = SubmitField("Submit")


# class SearchForm(FlaskForm):


class MDForm(FlaskForm):
    content = MDEditorField("Body", validators=[validators.DataRequired()])
    submit = SubmitField()

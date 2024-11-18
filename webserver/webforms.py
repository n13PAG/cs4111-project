from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, EmailField, PasswordField, BooleanField, SelectField, SubmitField, FileField
from wtforms import validators
from flask_mdeditor import  MDEditorField

class UserLoginForm(FlaskForm):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    uni = StringField('UNI', [validators.DataRequired(), validators.Length(min=6, max=6)])
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    uni = StringField('UNI', [validators.DataRequired(), validators.Length(min=6, max=6)])
    name = StringField('Full name', [validators.DataRequired()])
    is_student = BooleanField('Are you a student')
    submit = SubmitField('Sign Up')

class AddCourseForm(FlaskForm):
    # TODO: Must change cid in database to be text 
    cid = IntegerField('Course ID', [validators.DataRequired()])
    course_name = StringField('Course Name', [validators.DataRequired()])
    semester = SelectField(u'Semester', choices=[('FALL', 'FALL'), ('SPRING', 'SPRING'), ('SUMMER', 'SUMMER')])
    year = IntegerField('Year', [validators.DataRequired()])
    submit = SubmitField('Add Course')

class UploadForm(FlaskForm):
    file_link = StringField('PDF link', [validators.DataRequired()])
    submit = SubmitField('Submit')

class MDForm(FlaskForm):
    content = MDEditorField('Body', validators=[validators.DataRequired()])
    submit = SubmitField()


    
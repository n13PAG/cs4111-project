from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, EmailField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms import validators
from flask_mdeditor import  MDEditorField

class UserLoginForm(FlaskForm):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    uni = StringField('UNI', [validators.DataRequired(), validators.Length(min=6, max=6)])

class SignUpForm(FlaskForm):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    uni = StringField('UNI', [validators.DataRequired(), validators.Length(min=6, max=6)])
    name = StringField('Full name', [validators.DataRequired()])

class AddCourseForm(FlaskForm):
    # TODO: Must change cid in database to be text 
    cid = IntegerField('Course ID', [validators.DataRequired()])
    course_name = StringField('Course Name', [validators.DataRequired()])
    semester = SelectField(u'Semester', choices=[('FALL', 'FALL'), ('SPRING', 'SPRING'), ('SUMMER', 'SUMMER')])
    year = IntegerField('Year', [validators.DataRequired()])

class MDForm(FlaskForm):
    content = MDEditorField('Body', validators=[validators.DataRequired()])
    submit = SubmitField()


    
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# Create a Post Form
class PostForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    profile = CKEditorField("Write something about yourself", validators=[DataRequired()])
    experience = CKEditorField("Experience", validators=[DataRequired()])
    education = CKEditorField("Education", validators=[DataRequired()])
    skills = CKEditorField("Skills", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a User Form Class 
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    # password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")

# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a PasswordForm Class
class PasswordForm(FlaskForm):
    username = StringField("What's your username", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a LoginForm Class
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


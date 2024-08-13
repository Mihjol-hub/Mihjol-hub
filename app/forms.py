#app/form.py 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import DateField 

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    workrole = StringField('Work Role')
    entreprise = StringField('Enterprise')
    biography = TextAreaField('Biography')
    birthday = DateField('Birthday', format='%Y-%m-%d')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordConfirmForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class ProfileForm(FlaskForm):
    workrole = StringField('Work Role')
    entreprise = StringField('Enterprise')
    biography = TextAreaField('Biography')
    birthday = DateField('Birthday', format='%Y-%m-%d')
    submit = SubmitField('Update Profile')

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=4, max=20)])
    description = TextAreaField('Description')
    submit = SubmitField('Create Group')

class CreatePostForm(FlaskForm):
    content = TextAreaField('Post Content', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Post')
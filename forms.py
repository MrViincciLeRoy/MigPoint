from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

class LoginForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired(), Length(10, 10), Regexp(r'^0\d{9}$')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(2, 100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(10, 10), Regexp(r'^0\d{9}$')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
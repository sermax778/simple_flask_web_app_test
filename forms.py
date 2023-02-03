from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, Length, DataRequired, EqualTo


class LoginForm(FlaskForm):
    login = StringField('Login: ', validators=[DataRequired()])
    psw = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=35)])
    remember = BooleanField('Keep me logged: ', default=False)
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    login  = StringField('Login: ', validators=[DataRequired()])
    email  = StringField('Email: ', validators=[Email()])
    psw    = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=35)])
    repsw  = PasswordField('Re-enter password: ', validators=[DataRequired(), EqualTo('psw', message='Passwords are different')])
    agr    = BooleanField('I agree with the rules: ', default=False)
    submit = SubmitField('Submit')
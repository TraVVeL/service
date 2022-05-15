from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Логин", validators=[Email()])
    password = PasswordField("пароль", validators=[DataRequired(), Length(min=6, max=50)])
    remindme = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")

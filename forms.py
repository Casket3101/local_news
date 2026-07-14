from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('ელ-ფოსტა', validators=[DataRequired(), Email()])
    password = PasswordField('პაროლი', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('რეგისტრაცია')

class LoginForm(FlaskForm):
    email = StringField('ელ-ფოსტა', validators=[DataRequired(), Email()])
    password = PasswordField('პაროლი', validators=[DataRequired()])
    submit = SubmitField('შესვლა')

class NewsForm(FlaskForm):
    title = StringField('სიახლის სათაური', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('კონტენტი / ტექსტი', validators=[DataRequired()])
    category = SelectField('კატეგორია', choices=[
        ('განათლება', 'განათლება'),
        ('კულტურა', 'კულტურა'),
        ('სპორტი', 'სპორტი'),
        ('საზოგადოება', 'საზოგადოება')
    ], validators=[DataRequired()])
    submit = SubmitField('გამოქვეყნება (გაიგზავნება დასამტკიცებლად)')
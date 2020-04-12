from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
# unfinished
# forms for index page


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[Length(0, 64)])
    college = StringField('college', validators=[Length(0, 10)])
    grade = StringField('grade', validators=[Length(0, 4)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
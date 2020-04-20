from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField
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


class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadPhotoForm(FlaskForm):
    photo = FileField(validators = [FileRequired()])
    submit = SubmitField('Upload')
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField


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
    title = TextAreaField("Title", validators=[DataRequired()])
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostMdForm(FlaskForm):
    body = TextAreaField("Body", validators=[DataRequired()])
    body_html = HiddenField()


class UploadPhotoForm(FlaskForm):
    photo = FileField('image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')


class CommentForm(FlaskForm):
    body = TextAreaField('Enter your comment', render_kw={"placeholder": "Enter your comment"}, validators=[DataRequired()])
    submit = SubmitField('Submit')

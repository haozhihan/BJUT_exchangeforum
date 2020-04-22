# At the beginning, we use this form to test our code.
# However, after we connect with front end, we found it useless.
#  Therefore, we decide to comment out it.




from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# class LoginForm(FlaskForm):
#    student_id = StringField('user', validators=[DataRequired()])
#    password = PasswordField('Password', validators=[DataRequired()])
#    remember_me = BooleanField('Keep me logged in')
#    submit = SubmitField('Log In')
#
#
# class RegistrationForm(FlaskForm):
#    student_id = StringField('Student ID', validators=[DataRequired()])
#    ID_number = StringField('ID number', validators=[DataRequired(), Length(10, 18)])
#    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
#                                            Email()])
#    username = StringField('Username', validators=[
#        DataRequired(), Length(1, 64),
#        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
#              'Usernames must have only letters, numbers, dots or '
#              'underscores')])
#   password = PasswordField('Password', validators=[
#       DataRequired(), EqualTo('password2', message='Passwords must match.')])
#   password2 = PasswordField('Confirm password', validators=[DataRequired()])
#   submit = SubmitField('Register')
#
#   def validate_email(self, field):
#               if User.query.filter_by(email=field.data.lower()).first():
#           raise ValidationError('Email already registered.')
#
#   def validate_student_id(self, field):
#       if User.query.filter_by(student_id=field.data).first():
#           raise ValidationError('Student id already in use.')
#
#   def validate_ID_number(self,field):
#       if User.query.filter_by(ID_number=field.data).first():
#           raise ValidationError("ID number already in use.")
#
#   def validate_username(self, field):
#       if User.query.filter_by(username=field.data).first():
#           raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
  old_password = PasswordField('Old password', validators=[DataRequired()])
  password = PasswordField('New password', validators=[
      DataRequired(), EqualTo('password2', message='Passwords must match.')])
  password2 = PasswordField('Confirm new password',
                            validators=[DataRequired()])
  submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
  email = StringField('Email', render_kw={"placeholder":"Your Email"}, validators=[DataRequired(), Length(1, 64),
                                           Email()])
  submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
  password = PasswordField('New Password', render_kw={"placeholder":"New Password"},
                           validators=[DataRequired(),
                                       EqualTo('password2', message='Passwords must match')])
  password2 = PasswordField('Confirm password', render_kw={"placeholder":"Confirm password"},
                            validators=[DataRequired()])
  submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
  email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                              Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  submit = SubmitField('Update Email Address')

  def validate_email(self, field):
      if User.query.filter_by(email=field.data.lower()).first():
          raise ValidationError('Email already registered.')

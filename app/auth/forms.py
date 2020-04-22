from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User




# 修改邮箱
class ChangeEmailForm(FlaskForm):
  email = StringField('New Email', validators=[DataRequired(), Length(1, 64), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  submit = SubmitField('Update Email Address')

  def validate_email(self, field):
      if User.query.filter_by(email=field.data.lower()).first():
          raise ValidationError('Email already registered.')



# 重置密码的界面1
class PasswordResetRequestForm(FlaskForm):
  email = StringField('Email', render_kw={"placeholder":"Your Email"},
                      validators=[DataRequired(), Length(1, 64), Email()])
  submit = SubmitField('Reset Password')



# 重置密码的界面2（在邮件里面）
class PasswordResetForm(FlaskForm):
  password = PasswordField('New Password', render_kw={"placeholder":"New Password"},
             validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
  password2 = PasswordField('Confirm password', render_kw={"placeholder":"Confirm password"},
                            validators=[DataRequired()])
  submit = SubmitField('Reset Password')

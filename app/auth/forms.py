from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


# 重置密码的界面1
class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', render_kw={"placeholder": "Your Email"},
                        validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


# 重置密码的界面2（在邮件里面）
class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', render_kw={"placeholder": "New Password"},
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', render_kw={"placeholder": "Confirm password"},
                              validators=[DataRequired()])
    submit = SubmitField('Reset Password')

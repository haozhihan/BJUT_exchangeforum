from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email





class RegisterOrganizationForm(FlaskForm):
    name = StringField('Organization name', validators=[DataRequired(), Length(1,64)])
    teacher = StringField('Organization Teacher', validators=[DataRequired(), Length(1, 64)])
    leader = StringField('Organization Leader Student', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Organization Email', render_kw={"placeholder": "Your Email"},
                        validators=[DataRequired(), Length(1, 64), Email()])
    college = StringField('College', validators=[DataRequired(), Length(1, 64)])
    phone = StringField('Contact Number', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Submit')
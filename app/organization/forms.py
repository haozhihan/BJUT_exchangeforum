from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email





class RegisterOrganizationForm(FlaskForm):
    name = StringField('Organization Name', render_kw={"placeholder": "Organization Name"}, validators=[DataRequired(), Length(1,64)])
    teacher = StringField('Organization Teacher', render_kw={"placeholder": "Organization Teacher"}, validators=[DataRequired(), Length(1, 64)])
    leader = StringField('Organization Leader Student', render_kw={"placeholder": "Organization Leader Student"}, validators=[DataRequired(), Length(1, 64)])
    email = StringField('Organization Email', render_kw={"placeholder": "Organization Email"}, validators=[DataRequired(), Length(1, 64), Email()])
    college = StringField('College', render_kw={"placeholder": "College or BJUT"},validators=[DataRequired(), Length(1, 64)])
    phone = StringField('Contact Number', render_kw={"placeholder": "Contact Number"},validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Submit')
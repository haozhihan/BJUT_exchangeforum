from flask import render_template, redirect, url_for, flash
from . import organization
from .. import db
from ..models import Organization, User
from ..email import send_email
from .forms import RegisterOrganizationForm


@organization.route('/register', methods=['GET', 'POST'])
def register_organization():
    form = RegisterOrganizationForm()
    if form.validate_on_submit():
        organization = Organization(name=form.name.data,
                                    teacher=form.teacher.data,
                                    leader_student=form.leader.data,
                                    phone=form.phone.data,
                                    college=form.college.data,
                                    email=form.email.data,
                                    avatar_img='/static/Image/ico.jpeg')
        db.session.add(organization)
        db.session.commit()
        token = organization.generate_confirmation_token()
        send_email('13011090966@163.com', 'Register Organization',
                   'mail_organization/To_administrator', organization=organization, token=token)
        flash('A register organization-account email has been sent to administrator.')
        return redirect(url_for('auth.login'))
    return render_template('organization/register2.html', form=form)


@organization.route('/send_result/<oid>', methods=['GET', 'POST'])
def send_result(oid):
    return render_template('organization/send_result.html', oid=oid)


@organization.route('/register_success/<oid>', methods=['GET'])
def register_success(oid):
    organization = Organization.query.filter_by(id=oid).first()
    user = User(student_id=organization.id,
                ID_number=organization.id,
                confirmed=True,
                email=organization.email,
                username=organization.name,
                password='password',
                role_id=2
                )

    db.session.add(user)
    db.session.commit()
    # 注册时发送邮箱认证
    token = organization.generate_confirmation_token()
    send_email(organization.email, 'Register Organization Success',
               'mail_organization/success_register', user=user, token=token)
    flash('A register_success email has been sent to organization by email.')
    return render_template('auth/login.html')


@organization.route('/register_fail/<oid>', methods=['GET'])
def result_fail(oid):
    organization = Organization.query.filter_by(id=oid).first()
    token = organization.generate_confirmation_token()
    send_email(organization.email, 'Register Organization Fail',
               'mail_organization/fail_register', token=token)
    flash('A register_fail email has been sent to organization by email.')
    return render_template('auth/login.html')

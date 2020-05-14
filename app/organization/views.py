from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user

from . import organization
from .. import db
from ..models import Organization, User, Activity
from ..email import send_email
from .forms import RegisterOrganizationForm


@organization.route('/register', methods=['GET', 'POST'])
def register_organization():
    form = RegisterOrganizationForm()
    if form.validate_on_submit():
        emailfind = User.query.filter_by(email=form.email.data).first()
        if emailfind is not None:
            flash("Your email has been registered, please change your email")
            return render_template('organization/register2.html', form=form)
        usernamefind = User.query.filter_by(username=form.name.data).first()
        if usernamefind is not None:
            flash("Your organization name has been registered, please change your username")
            return render_template('organization/register2.html', form=form)
        organization = Organization(name=form.name.data,
                                    teacher=form.teacher.data,
                                    leader_student=form.leader.data,
                                    phone=form.phone.data,
                                    college=form.college.data,
                                    email=form.email.data
                                    )
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
                role_id=2,
                avatar_img='/static/Image/ico.jpeg'
                )

    db.session.add(user)
    db.session.commit()
    # 注册时发送邮箱认证
    token = organization.generate_confirmation_token()
    send_email(organization.email, 'Register Organization Success',
               'mail_organization/success_register', user=user, token=token)
    flash('A register_success email has been sent to organization by email.')
    return redirect(url_for('auth.login'))


@organization.route('/register_fail/<oid>', methods=['GET'])
def result_fail(oid):
    organization = Organization.query.filter_by(id=oid).first()
    token = organization.generate_confirmation_token()
    send_email(organization.email, 'Register Organization Fail',
               'mail_organization/fail_register', token=token)
    flash('A register_fail email has been sent to organization by email.')
    return redirect(url_for('auth.login'))


@organization.route('/new_activity', methods=['GET', 'POST'])
def organization_activity():
    if request.method == 'GET':
        return render_template('organization/new_organization.html')
    if request.method == 'POST':
        if request.form["is"] == "Yes":
            is_Agree = True
        else:
            is_Agree = False
        acti = Activity(activity_name=request.form["activity_name"],
                        activity_time=request.form["activity_time"],
                        activity_place=request.form["activity_place"],
                        activity_describe=request.form["activity_describe"],
                        Organizer=request.form["organizer"],
                        is_schoolAgree=is_Agree,
                        announcer_id=current_user.id
                        )
        db.session.add(acti)
        db.session.commit()
        flash('Your Activity Announcement has been released!')
        return redirect(url_for('main.index'))

@organization.route('/activity-list', methods=['GET', 'POST'])
def show_transaction():
    page = request.args.get('page', 1, type=int)
    pagination = Activity.query.order_by(Activity.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    transactions = pagination.items
    return render_template('organization/activity_center.html', transactions=transactions,
                           pagination=pagination)
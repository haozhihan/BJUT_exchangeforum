from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from datetime import datetime
from . import organization
from .. import db
from ..decorators import permission_required
from ..models import Organization, User, Activity, Permission
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
    return render_template('organization/organization_register.html', form=form)


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
                avatar_img='/static/Image/ico.jpeg'
                )
    db.session.add(user)
    db.session.commit()
    thisUser = User.query.filter_by(ID_number=organization.id).first()
    thisUser.role_id = 2;
    db.session.add(thisUser)
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
        return render_template('organization/new_activity.html')
    if request.method == 'POST':
        if request.form["is"] == "Yes":
            is_Agree = True
        else:
            is_Agree = False
        string = request.form["activity_time"]
        name = request.form["activity_name"]
        place = request.form["activity_place"]
        describe = request.form["activity_describe"]
        organizer = request.form["organizer"]
        if name == "" or place == "" or string == "" or describe == "" or organizer == "":
            flash("Activity information cannot be empty")
            return render_template('organization/new_activity.html')
        time_str = string
        time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
        acti = Activity(activity_name=name,
                        activity_time=time,
                        activity_place=place,
                        activity_describe=describe,
                        Organizer=organizer,
                        is_schoolAgree=is_Agree,
                        announcer_id=current_user.id
                        )
        db.session.add(acti)
        db.session.commit()
        flash('Your Activity Announcement has been released!')
        return redirect(url_for('main.index_activity'))


@organization.route('/want/<activity_id>')
@login_required
@permission_required(Permission.FOLLOW)
def want(activity_id):
    activity = Activity.query.filter_by(id=activity_id).first()
    if activity is None:
        flash('Invalid activity.')
        return redirect(url_for('main.index_activity'))
    if current_user.is_wanting(activity):
        flash('You are already wanting this post.')
        return redirect(url_for('main.index_activity'))
    current_user.want(activity)
    activity.want(current_user)
    db.session.commit()
    flash('You are now wanting this post')
    return redirect(url_for('main.index_activity'))


@organization.route('/not_want/<activity_id>')
@login_required
@permission_required(Permission.FOLLOW)
def not_want(activity_id):
    activity = Activity.query.filter_by(id=activity_id).first()
    if activity is None:
        flash('Invalid activity.')
        return redirect(url_for('main.index_activity'))
    if not current_user.is_wanting(activity):
        flash('You are not wanting this post.')
        return redirect(url_for('main.index_activity'))
    current_user.not_want(activity)
    activity.not_want(current_user)
    db.session.commit()
    flash('You are not wanting this post')
    return redirect(url_for('main.index_activity'))


@organization.route('/delete_transaction/<int:activity_id>')
@login_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if current_user == activity.announcer:
        db.session.delete(activity)
        db.session.commit()
        flash('The activity has been deleted.')
        return redirect(url_for('main.user', username=activity.announcer.username))
    else:
        flash('你没有删评论权限')
        return redirect(url_for('main.user', username=activity.announcer.username))

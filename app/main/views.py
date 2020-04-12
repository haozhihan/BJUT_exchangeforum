from flask import render_template, request, flash, redirect, url_for
from . import main
from ..models import User, db, Role
from flask_login import login_required, current_user
from .forms import EditProfileForm
# view functions for index page
# unfinished


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    users = User.query.filter_by(username=username).first_or_404
    return render_template('user.html', user=users)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.college = form.college.data
        current_user.grade = form.grade.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.college.data = current_user.college
    form.grade.data = current_user.grade
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

from operator import or_
from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response
from flask_login import login_required, current_user

from . import main
from .. import db
from ..models import Permission, Role, User, Post, Comment, Notification


# @main.route('/query-user', methods=['GET', 'POST'])
# def query_user():
#     if request.method == 'GET':
#         return render_template('queryuser.html')
#     if request.method == 'POST':
#         user_inf = request.form["user"]
#         search_user = "%" + user_inf + "%"
#         result = User.query.filter(or_(User.username.like(search_user), User.student_id.like(search_user)))
#         page = request.args.get('page', 1, type=int)
#         pagination = result.order_by(User.username.desc()).paginate(
#             page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
#             error_out=False)
#         query = pagination.items
#         return render_template('queryuser.html', query=query, title="Result of query", pagination=pagination)


@main.route('/query-post', methods=['GET', 'POST'])
def query_post():
    if request.method == 'GET':
        return render_template('querypost.html')
    if request.method == 'POST':
        post_inf = request.form["post"]
        search_post = "%" + post_inf + "%"
        result = Post.query.filter(or_(Post.title.like(search_post), Post.body.like(search_post)))
        for item in result:
            sentence = item.title + item.body
            counts = 0
            list1 = sentence.split(" ")
            for y in range(len(list1)):
                if list1[y].find(post_inf) != -1:
                    counts = counts + 1
            item.important = counts
        page = request.args.get('page', 1, type=int)
        show_newest = False
        show_hottest = False
        show_relevance = False
        if current_user.is_authenticated:
            show_newest = bool(request.cookies.get('show_newest', ''))
            show_hottest = bool(request.cookies.get('show_hottest', ''))
            show_relevance = bool(request.cookies.get('show_relevance', ''))
        if show_relevance and not show_newest and not show_hottest:
            pagination = result.order_by(Post.important.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
        elif show_newest and not show_hottest and not show_relevance:
            pagination = result.order_by(Post.timestamp.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
        elif show_hottest and not show_relevance and not show_newest:
            pagination = result.order_by(Post.comments.count().desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
        else:
            for item in result:
                item.important = 0
            for item in result:
                sentence = item.title + item.body
                counts = 0
                list1 = sentence.split(" ")
                for y in range(len(list1)):
                    if list1[y].find(post_inf) != -1:
                        counts = counts + 1
                item.important = counts * 0.4 + item.comments.count() * 0.3 + item.liker.count() * 0.3
                print("post: " + item.id + "importance" + item.important)
            pagination = result.order_by(Post.important.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
        query = pagination.items
        for item in result:
            item.important = 0
        return render_template('querypost.html', query=query, title="Result of query", pagination=pagination)


@main.route('/newest')
@login_required
def show_newest():
    resp = make_response(redirect(url_for('.quest-post')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/hottest')
@login_required
def show_hottest():
    resp = make_response(redirect(url_for('.quest-post')))
    resp.set_cookie('show_hottest', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/relevance')
@login_required
def show_relevance():
    resp = make_response(redirect(url_for('.quest-post')))
    resp.set_cookie('show_relevance', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/information')
@login_required
def show_information():
    resp = make_response(redirect(url_for('.quest-post')))
    resp.set_cookie('show_relevance', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_hottest', '', max_age=30 * 24 * 60 * 60)
    return resp

from operator import or_
from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response
from flask_login import login_required, current_user
from sqlalchemy import func

from . import main
from .. import db
from ..models import Permission, Role, User, Post, Comment, Notification, Like


@main.route('/query-user', methods=['GET', 'POST'])
def query_user():
    if request.method == 'GET':
        return render_template('queryuser.html')
    if request.method == 'POST':
        user_inf = request.form["user"]
        search_user = "%" + user_inf + "%"
        result = User.query.filter(or_(User.username.like(search_user), User.student_id.like(search_user)))
        page = request.args.get('page', 1, type=int)
        pagination = result.order_by(User.username.desc()).paginate(
            page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
            error_out=False)
        query = pagination.items
        return render_template('queryuser.html', query=query, title="Result of query", pagination=pagination)


@main.route('/query-post', methods=['GET', 'POST'])
def query_post():
    if request.method == 'GET':
        return render_template('querypost.html')
    if request.method == 'POST':
        post_inf = request.form["post"]
        search_post = "%" + post_inf + "%"
        result = Post.query.filter(or_(Post.title.like(search_post), Post.body.like(search_post)))
        for item in result:
            item.important = 0
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
            for item in result:
                item.important = 0
                com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
                item.important = com_num
            pagination = result.order_by(Post.important.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
        else:
            for item in result:
                item.important = 0
                sentence = item.title + item.body
                counts = 0
                list1 = sentence.split(" ")
                for y in range(len(list1)):
                    if list1[y].find(post_inf) != -1:
                        counts = counts + 1
                com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
                li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
                item.important = counts * 4 + 3 * com_num + 3 * li_num
                print("post: " + str(item.id) + "importance" + str(item.important))
            pagination = result.order_by(Post.important.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
        posts = pagination.items
        print(show_newest + show_relevance + show_hottest)
        for item in result:
            item.important = 0
        return render_template('querypost.html', posts=posts, title="Result of query", pagination=pagination)


@main.route('/newest')
@login_required
def show_newest():
    resp = make_response(redirect(url_for('.query_post')))
    resp.set_cookie('show_relevance', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_newest', '1', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_hottest', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/hottest')
@login_required
def show_hottest():
    resp = make_response(redirect(url_for('.query_post')))
    resp.set_cookie('show_relevance', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_newest', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_hottest', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/relevance')
@login_required
def show_relevance():
    resp = make_response(redirect(url_for('.query_post')))
    resp.set_cookie('show_relevance', '1', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_newest', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_hottest', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/information')
@login_required
def show_information():
    resp = make_response(redirect(url_for('.query_post')))
    resp.set_cookie('show_relevance', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_newest', '', max_age=30 * 24 * 60 * 60)
    resp.set_cookie('show_hottest', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/query-post', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        return render_template('querypost.html')
    if request.method == 'POST':
        inf = request.form["inf"]
        search_result = "%" + inf + "%"
        result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
        page = request.args.get('page', 1, type=int)
        for item in result:
            item.important = 0
            sentence = item.title + item.body
            counts = 0
            list1 = sentence.split(" ")
            for y in range(len(list1)):
                if list1[y].find(inf) != -1:
                    counts = counts + 1
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
            item.important = counts * 4 + 3 * com_num + 3 * li_num
        pagination = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        for item in result:
            item.important = 0
        return render_template('querypost.html', posts=posts, title="Result of query", pagination=pagination)


@main.route('/query_combination/<inf>')
def query_combination(inf):
    # if request.method == 'GET':
    #     inf = request.form["inf"]
    #     # return render_template('querypost.html', inf=inf)
    search_result = "%" + inf + "%"
    result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
    page = request.args.get('page', 1, type=int)
    for item in result:
        item.important = 0
        sentence = item.title + item.body
        counts = 0
        list1 = sentence.split(" ")
        for y in range(len(list1)):
            if list1[y].find(search_result) != -1:
                counts = counts + 1
        com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
        li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
        item.important = counts * 4 + 3 * com_num + 3 * li_num
        print("post: " + str(item.id) + "importance" + str(item.important))
    pagination = result.order_by(Post.important.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    for item in result:
        item.important = 0
    return render_template('querypost.html', posts=posts, title="Result of query", pagination=pagination)


@main.route('/query_newest/<inf>')
def query_newest(inf):
    search_result = "%" + inf + "%"
    result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
    page = request.args.get('page', 1, type=int)
    pagination = result.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('querypost.html', posts=posts, title="Result of query", pagination=pagination)


@main.route('/query_hottest/<inf>')
def query_hottest(inf):
    search_result = "%" + inf + "%"
    result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
    page = request.args.get('page', 1, type=int)
    for item in result:
        item.important = item.comments.count()
    pagination = result.order_by(Post.important.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    for item in result:
        item.important = 0
    return render_template('querypost.html', posts=posts, title="Result of query", pagination=pagination)


@main.route('/query_relevance/<inf>')
def query_relevance(inf):
    search_result = "%" + inf + "%"
    result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
    page = request.args.get('page', 1, type=int)
    for item in result:
        sentence = item.title + item.body
        counts = 0
        list1 = sentence.split(" ")
        for y in range(len(list1)):
            if list1[y].find(inf) != -1:
                counts = counts + 1
        item.important = counts
    pagination = result.order_by(Post.important.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    for item in result:
        item.important = 0
    return render_template('querypost.html', posts=posts, title="Result of query", pagination=pagination)


@main.route('/query-user/<inf>')
def query_user(inf):
    search_result = "%" + inf + "%"
    result = User.query.filter(or_(User.username.like(search_result), User.student_id.like(search_result)))
    page = request.args.get('page', 1, type=int)
    pagination = result.order_by(User.username.desc()).paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('queryuser.html', posts=posts, title="Result of query", pagination=pagination)



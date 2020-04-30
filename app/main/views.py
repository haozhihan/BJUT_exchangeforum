import os
from operator import or_

from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import main
from .forms import EditProfileForm, PostForm, UploadPhotoForm, CommentForm, PostMdForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Notification
from ..decorators import admin_required, permission_required
from ..decorators import admin_required


# 查询
# view functions for index page
# unfinished
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
def query_user():
    if request.method == 'GET':
        return render_template('querypost.html')
    if request.method == 'POST':
        post_inf = request.form["post"]
        search_post = "%" + post_inf + "%"
        result = Post.query.filter(or_(Post.title.like(search_post), Post.body.like(search_post)))
        page = request.args.get('page', 1, type=int)
        pagination = result.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        query = pagination.items
        return render_template('querypost.html', query=query, title="Result of query", pagination=pagination)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('显示的主页.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/notification')
def notification():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.notifications.order_by(Notification.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    notices = pagination.items
    return render_template('notifications.html', notices=notices,
                           pagination=pagination)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allow_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/photo', methods=['POST'])
def uploadPhoto():
    form = UploadPhotoForm()
    f = form.photo.data
    if f and allow_file(f.filename):
        filename = secure_filename(f.filename)
        f.save(os.path.join('app', 'static', 'assets', filename))
        current_user.avatar_img = '/static/assets/' + filename
        db.session.commit()
    else:
        flash("Please upload a picture of the compound rule")
    return redirect(url_for('.edit_profile'))


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UploadPhotoForm()
    if request.method == 'GET':
        return render_template('edit_profile.html', form=form)
    if request.method == 'POST':
        # 读取前端数据
        current_user.username = request.form["username"]
        current_user.college = request.form["collage"]
        current_user.grade = request.form["grade"]
        current_user.about_me = request.form["aboutme"]
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count('*') - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = Comment.query.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    print([post][0].body)
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    form.title.data = post.title
    return render_template('edit_post.html', form=form)


@main.route('/delete/<int:id>')
@login_required
def delete(id):
    comment = Comment.query.get_or_404(id)
    posts = Post.query.filter_by(id=comment.post_id).first()
    users = User.query.filter_by(id=posts.author_id).first()
    print(users.username)
    print(comment.author.username)
    print(current_user.username)
    if current_user == comment.author or current_user == users:
        db.session.delete(comment)
        db.session.commit()
        flash('The comment has been deleted.')
        return redirect(url_for('.post', id=posts.id))
    else:
        flash('你没有删评论权限')
        return redirect(url_for('.post', id=posts.id))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/like/<post_id>')
@login_required
@permission_required(Permission.FOLLOW)
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.index'))
    if current_user.is_liking(post):
        flash('You are already liking this post.')
        return redirect(url_for('.post', id=post_id))
    current_user.like(post)
    post.like(current_user)
    db.session.commit()
    flash('You are now liking this post')
    return redirect(url_for('.post', id=post_id))


@main.route('/dislike/<post_id>')
@login_required
@permission_required(Permission.FOLLOW)
def dislike(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.index'))
    if not current_user.is_liking(post):
        flash('You are not liking this post.')
        return redirect(url_for('.post', id=post_id))
    current_user.dislike(post)
    post.dislike(current_user)
    db.session.commit()
    flash('You are not liking this post')
    return redirect(url_for('.post', id=post_id))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.following.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/liked_by/<post_id>')
def liked_by(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = post.liker.paginate(
        page, per_page=current_app.config['FLASKY_LIKER_PER_PAGE'],
        error_out=False)
    liker = [{'user': item.liker, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('liker.html', post=post, title="The liker of",
                           endpoint='.liked_by', pagination=pagination,
                           liker=liker)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text1')
        if title == "":
            flash("Title cannot be None!")
            return render_template('new_post.html')
        if text == "" or text == "<p><br></p>":
            flash("Post cannot be None")
            return render_template('new_post.html')
        post = Post(title=title,
                    body=text,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash("You have just posted a posting", 'success')
        return redirect(url_for('.index'))
    return render_template('new_post.html')


@main.route('/new_post_md', methods=['GET', 'POST'])
@login_required
def new_post_md():
    form = PostMdForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        title = request.form.get('title')
        body = form.body.data
        if title == "":
            flash("Title cannot be None!")
            return render_template('new_mdpost2.html', form=form)
        post = Post(title=title,
                    body=body,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash("You have just posted a posting", 'success')
        return redirect(url_for('.index'))
    return render_template('new_mdpost2.html', form=form)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

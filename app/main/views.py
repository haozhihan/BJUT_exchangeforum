import os
from datetime import datetime
from operator import or_
from flask import render_template, redirect, url_for, flash, request, \
    current_app, make_response
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import func
from werkzeug.utils import secure_filename
from . import main
from .forms import UploadPhotoForm, CommentForm, PostMdForm
from .. import db
from ..models import Permission, User, Post, Comment, Notification, Like, Transaction, Activity, Collect, Want
from ..decorators import permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        page1 = request.args.get('page', 1, type=int)
        query1 = Post.query
        pagination1 = query1.order_by(Post.recent_activity.desc()).paginate(
            page1, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts1 = pagination1.items
        # hot
        for item in query1:
            item.important = 0
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
            item.important = 7 * com_num + 3 * li_num
        hot = query1.order_by(Post.important.desc())
        return render_template('index/index_posts.html', posts1=posts1, posts5=hot, pagination1=pagination1)
    else:
        inf = request.form["search"]
        return redirect(url_for('.query', content=inf))


@main.route('/trans', methods=['GET', 'POST'])
def index_transaction():
    if request.method == 'GET':
        page2 = request.args.get('page', 1, type=int)
        query2 = Transaction.query
        pagination2 = query2.order_by(Transaction.timestamp.desc()).paginate(
            page2, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        transactions = pagination2.items
        # hot
        query1 = Post.query
        for item in query1:
            item.important = 0
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
            item.important = 7 * com_num + 3 * li_num
        hot = query1.order_by(Post.important.desc())
        return render_template('index/index_transactions.html', transactions=transactions, posts5=hot, pagination2=pagination2)
    else:
        inf = request.form["search"]
        return redirect(url_for('.query', content=inf))


@main.route('/act', methods=['GET', 'POST'])
def index_activity():
    if request.method == 'GET':
        page3 = request.args.get('page', 1, type=int)
        query3 = Activity.query
        for activity in query3:
            if activity.activity_time < datetime.utcnow():
                activity.is_invalid = True
                db.session.add(activity)
                db.session.commit()
        pagination3 = query3.order_by(Activity.timestamp.desc()).paginate(
            page3, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        activities = pagination3.items
        #hot
        query1 = Post.query
        for item in query1:
            item.important = 0
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
            item.important = 7 * com_num + 3 * li_num
        hot = query1.order_by(Post.important.desc())
        return render_template('index/index_activities.html', activities=activities,  posts5=hot, pagination3=pagination3)
    else:
        inf = request.form["search"]
        return redirect(url_for('.query', content=inf))


@main.route('/foll', methods=['GET', 'POST'])
def index_follow():
    if request.method == 'GET':
        # hot
        query1 = Post.query
        for item in query1:
            item.important = 0
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            li_num = db.session.query(func.count(Like.liker_id)).filter_by(liked_post_id=item.id).scalar()
            item.important = 7 * com_num + 3 * li_num
        hot = query1.order_by(Post.important.desc())
        page4 = request.args.get('page4', 1, type=int)
        query4 = current_user.followed_posts
        pagination4 = query4.order_by(Post.recent_activity.desc()).paginate(
            page4, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts4 = pagination4.items
        return render_template('index/index_follows.html', posts4=posts4, posts5=hot, pagination4=pagination4)
    else:
        inf = request.form["search"]
        return redirect(url_for('.query', content=inf))


@main.route('/query/<content>', methods=['GET', 'POST'])
def query(content):
    if request.method == 'GET':
        print("get")
        inf = content
        search_result = "%" + inf + "%"
        result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
        for item in result:
            item.important = 0
            sentence = item.title + item.body
            counts = 0
            list1 = sentence.split(" ")
            for y in range(len(list1)):
                if list1[y].find(inf) != -1:
                    counts = counts + 1
            item.important = counts
        page = request.args.get('page', 1, type=int)
        pagination1 = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        relevance = pagination1.items
        pagination2 = result.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        newest = pagination2.items
        for item in result:
            item.important = 0
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            item.important = com_num
        pagination3 = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        hottest = pagination3.items
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
        pagination4 = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        combination = pagination4.items
        # print(show_newest + show_relevance + show_hottest)
        for item in result:
            item.important = 0
        return render_template('querypost.html', relevance=relevance, newest=newest, hottest=hottest,
                               combination=combination, title="Result of query", inf=inf, pagination1=pagination1,
                               pagination2=pagination2, pagination3=pagination3, pagination4=pagination4)
    if request.method == 'POST':
        inf = request.form["inf"]
        search_result = "%" + inf + "%"
        result = Post.query.filter(or_(Post.title.like(search_result), Post.body.like(search_result)))
        for item in result:
            item.important = 0
            sentence = item.title + item.body
            counts = 0
            list1 = sentence.split(" ")
            for y in range(len(list1)):
                if list1[y].find(inf) != -1:
                    counts = counts + 1
            item.important = counts
        page = request.args.get('page', 1, type=int)
        pagination1 = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        relevance = pagination1.items
        pagination2 = result.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        newest = pagination2.items
        for item in result:
            item.important = 0
            com_num = db.session.query(func.count(Comment.id)).filter_by(post_id=item.id).scalar()
            item.important = com_num
        pagination3 = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        hottest = pagination3.items
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
        pagination4 = result.order_by(Post.important.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        combination = pagination4.items
        # print(show_newest + show_relevance + show_hottest)
        for item in result:
            item.important = 0
        return render_template('querypost.html', relevance=relevance, newest=newest, hottest=hottest,
                               combination=combination, title="Result of query", inf=inf, pagination1=pagination1,
                               pagination2=pagination2, pagination3=pagination3, pagination4=pagination4)


@main.route('/query-user', methods=['GET', 'POST'])
def query_user():
    if request.method == 'GET':
        return render_template('queryuser.html')
    if request.method == 'POST':
        inf = request.form["user"]
        search_result = "%" + inf + "%"
        result = User.query.filter(or_(User.username.like(search_result), User.student_id.like(search_result)))
        page = request.args.get('page', 1, type=int)
        pagination = result.order_by(User.username.desc()).paginate(
            page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
            error_out=False)
        query = pagination.items
        return render_template('queryuser.html', query=query, title="Result of query", pagination=pagination, inf=inf)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    liking = Like.query.filter_by(liker_id=user.id)
    collecting = user.collected_transaction
    wanting = user.wanted_Activity

    posts = user.posts.order_by(Post.timestamp.desc())
    liking_posts = [{'post': item.liked_post, 'timestamp': item.timestamp} for item in liking.order_by(Like.timestamp.desc())]
    transactions = user.transactions.order_by(Transaction.timestamp.desc())
    activities = user.activities.order_by(Activity.timestamp.desc())
    collects = collecting.order_by(Collect.timestamp.desc())
    wants = wanting.order_by(Want.timestamp.desc())
    return render_template('user.html', user=user, posts=posts, liking_posts=liking_posts, activities=activities,
                           transactionsInProfile=transactions, collects=collects, wants=wants,)


@main.route('/notification')
def notification():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.notifications.order_by(Notification.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    notices = pagination.items
    return render_template('table/notifications.html', notices=notices,
                           pagination=pagination)


@main.route('/change_read/<int:id>')
def change_read(id):
    notice = Notification.query.filter_by(id=id).first()
    notice.is_read = True
    db.session.add(notice)
    db.session.commit()
    flash("You have read one notification")
    return redirect(url_for('.notification'))


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
        usernamefind = User.query.filter_by(username=request.form["username"]).first()
        if usernamefind is not None:
            flash("Your new username already exists, please change your username")
            return render_template('edit_profile.html', form=form)

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
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count('*') - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    """发表评论与回复"""
    if form.validate_on_submit():
        body = form.body.data
        if request.form.get('anonymous') == "on":
            is_anonymous = True
            username = "Anonymous"
        else:
            is_anonymous = False
            username = current_user.username
        comment = Comment(body=body,
                          post=post,
                          author=current_user._get_current_object(),
                          replied_id=request.args.get('reply'),
                          is_anonymous=is_anonymous)
        comment.post.recent_activity = datetime.utcnow()
        if comment.replied_id:
            replied = Comment.query.get_or_404(comment.replied_id)
            comment.replied = replied
            action1 = " has replied<" + comment.body + "> to your comment<" + comment.replied.body + "> in the posting "
            n1 = Notification(receiver_id=comment.replied.author_id, timestamp=datetime.utcnow(),
                              username=username, action=action1,
                              object=post.title, object_id=post.id)
            db.session.add(n1)
            db.session.commit()
            action2 = " has commented<" + comment.body + "> on your posting"
            n2 = Notification(receiver_id=post.author_id, timestamp=datetime.utcnow(),
                              username=username, action=action2,
                              object=post.title, object_id=post.id)
            db.session.add(n2)
            db.session.commit()
        else:
            action = " has commented<" + comment.body + "> on your posting"
            """传入通知信息"""
            n = Notification(receiver_id=post.author_id, timestamp=datetime.utcnow(),
                             username=username, action=action,
                             object=post.title, object_id=post.id)
            db.session.add(n)
            db.session.commit()
        db.session.add(comment)
        db.session.commit()
        if comment.is_anonymous:
            flash('Comment published anonymously')
        else:
            flash('Comment published successfully')
        return redirect(url_for('.post', id=post.id))
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    """作为中转函数通过URL传递被回复评论信息"""
    comment = Comment.query.get_or_404(comment_id)
    post1 = comment.post
    author = comment.author.username
    post1.recent_activity = datetime.utcnow()
    if comment.is_anonymous:
        author = "anonymous"
    db.session.commit()
    return redirect(url_for('.post', id=comment.post.id, reply=comment_id, author=author))


@main.route('/delete_comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    posts = Post.query.filter_by(id=comment.post_id).first()
    users = User.query.filter_by(id=posts.author_id).first()
    if current_user == comment.author or current_user == users:
        db.session.delete(comment)
        db.session.commit()
        flash('The comment has been deleted.')
        return redirect(url_for('.post', id=posts.id))
    else:
        flash('你没有删评论权限')
        return redirect(url_for('.post', id=posts.id))


@main.route('/delete_post_profile/<post_id>')
@login_required
def delete_post_inProfile(post_id):
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    flash('The posting has been deleted.')
    return redirect(url_for('.user', username=current_user.username))


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
    post.recent_activity = datetime.utcnow()
    db.session.commit()
    flash('You are now liking this post')
    return redirect(url_for('.index', id=post_id))


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
    return redirect(url_for('.index', id=post_id))


# 显示所有followers的人
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
    return render_template('table/../templates/followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


# 显示所有followed的人
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
    return render_template('table/../templates/followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


# 显示所有喜欢这个post的人
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
    return render_template('table/liker.html', post=post, title="The liker of",
                           endpoint='.liked_by', pagination=pagination,
                           liker=liker)


@main.route('/new_post_md', methods=['GET', 'POST'])
@login_required
def new_post_md():
    form = PostMdForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        title = request.form.get('title')
        body = form.body.data
        if request.form.get('anonymous') == "on":
            is_anonymous = True
        else:
            is_anonymous = False
        if title == "":
            flash("Title cannot be None!")
            return render_template('new_posting/new_mdpost.html', form=form)
        body_html = request.form['test-editormd-html-code']
        post = Post(title=title,
                    body=body,
                    body_html=body_html,
                    is_anonymous=is_anonymous,
                    author=current_user._get_current_object())
        post.recent_activity = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        if post.is_anonymous == True:
            flash("You have just posted a posting anonymously", 'success')
        else:
            flash("You have just posted a posting", 'success')
        return redirect(url_for('.index'))
    return render_template('new_posting/new_mdpost.html', form=form)

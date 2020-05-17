# The purpose of this file is to build the relevant data and contacts of users and roles in the database,
# as well as the permission settings of different users.
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from markdown import markdown
import bleach


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    ACTIVITY = 8
    MODERATE = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Organization': [Permission.FOLLOW, Permission.COMMENT,
                             Permission.WRITE, Permission.ACTIVITY],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE, ],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class Students(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    id_number = db.Column(db.String(18))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, default=1, index=True)


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following', lazy='joined')
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 以下是关于用户的基本信息，用于注册、登录以及编辑个人主页
    ID_number = db.Column(db.Integer, unique=True, index=True)
    student_id = db.Column(db.Integer, unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)

    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # 以下添加的信息是显示在用户个人主页的信息
    grade = db.Column(db.String(4))
    college = db.Column(db.String(64))
    about_me = db.Column(db.Text())

    # 以下两个变量用于刷新用户访问时间
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # 用avatar_hash来储存生成头像时产生的MD5散列值
    avatar_hash = db.Column(db.String(32))
    avatar_img = db.Column(db.String(120), nullable=True)

    # 发帖、评论与点赞
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # 关注
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower',
                                lazy='dynamic', cascade='all')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed',
                                lazy='dynamic', cascade='all')
    # 点赞
    liked_post = db.relationship('Like', back_populates='liker', lazy='dynamic', cascade='all')
    # 消息中心
    notifications = db.relationship('Notification', back_populates='receiver', lazy='dynamic')
    # 交易
    transactions = db.relationship('Transaction', back_populates='seller', lazy='dynamic')
    # Activity
    activities = db.relationship('Activity', back_populates='announcer', lazy='dynamic')
    #want
    wanted_Activity = db.relationship('Want', back_populates='wanter', lazy='dynamic', cascade='all')
    #collect
    collected_transaction = db.relationship('Collect', back_populates='collecter', lazy='dynamic', cascade='all')


    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    # 通过特定的邮箱来识别管理员身份（待改进）
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        #
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        self.follow(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    # 该方法是用于帮助用户重置密码
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    # 该方法是用于帮助用户修改电子邮箱地址
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        #
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # 该方法可以刷新用户最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # 为了避免重复编写计算 Gravatar 散列值的逻辑
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # 该方法可以使用储存散列值，或者依照gravatar_hash()重新计算散列值
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            n = Notification(receiver_id=user.id, timestamp=datetime.utcnow(),
                             username=self.username, action=" has followed ",
                             object="you")
            db.session.add(n)
            db.session.add(f)

    def like(self, post):
        if not self.is_liking(post):
            ll = Like(liker=self, liked_post=post)
            n = Notification(receiver_id=post.author_id, timestamp=datetime.utcnow(),
                             username=self.username, action=" has liked your posting ",
                             object=post.title, object_id=post.id)
            db.session.add(n)
            db.session.add(ll)

    def collect(self, transaction):
        if not self.is_collecting(transaction):
            ll = Collect(collecter=self, collected_transaction=transaction)
            n = Notification(receiver_id=transaction.seller_id, timestamp=datetime.utcnow(),
                             username=self.username, action=" has collected your posting ",
                             object=transaction.item_name, object_id=transaction.id)
            db.session.add(n)
            db.session.add(ll)

    def want(self, activity):
        if not self.is_wanting(activity):
            ll = Want(wanter=self, wanted_Activity=activity)
            n = Notification(receiver_id=activity.announcer_id, timestamp=datetime.utcnow(),
                             username=self.username, action=" has wanted your posting ",
                             object=activity.activity_name, object_id=activity.id)
            db.session.add(n)
            db.session.add(ll)

    def unfollow(self, user):
        f = self.following.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def dislike(self, post):
        ll = self.liked_post.filter_by(liked_post_id=post.id).first()
        if ll:
            db.session.delete(ll)

    def not_want(self, activity):
        ll = self.wanted_Activity.filter_by(wanted_Activity_id=activity.id).first()
        if ll:
            db.session.delete(ll)

    def not_collect(self, transaction):
        ll = self.collected_transaction.filter_by(collected_transaction_id=transaction.id).first()
        if ll:
            db.session.delete(ll)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(
            followed_id=user.id).first() is not None

    def is_liking(self, post):
        if post.id is None:
            return False
        return self.liked_post.filter_by(
            liked_post_id=post.id).first() is not None

    def is_collecting(self, transaction):
        if transaction.id is None:
            return False
        return self.collected_transaction.filter_by(
            collected_transaction_id=transaction.id).first() is not None

    def is_wanting(self, activity):
        if activity.id is None:
            return False
        return self.wanted_Activity.filter_by(
           wanted_Activity_id=activity.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.username


class Organization(UserMixin, db.Model):
    __tablename__ = 'organizations'
    # 以下是关于用户的基本信息，用于注册、登录以及编辑个人主页
    id = db.Column(db.Integer, primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)

    # 以下添加的信息是显示在用户个人主页的信息
    name = db.Column(db.String(64))
    teacher = db.Column(db.String(128))
    leader_student = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    college = db.Column(db.String(256))
    email = db.Column(db.String(64))

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_liking(self, post):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    important = db.Column(db.INT, default=0)
    recent_activity = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan', lazy='dynamic')
    liker = db.relationship('Like', back_populates='liked_post', lazy='dynamic', cascade='all')
    is_anonymous = db.Column(db.Boolean, default=False)

    def like(self, user):
        if not self.is_liked_by(user):
            ll = Like(liker=user, liked_post=self)
            db.session.add(ll)

    def dislike(self, user):
        ll = self.liker.filter_by(liker_id=user.id).first()
        if ll:
            db.session.delete(ll)

    def is_liked_by(self, user):
        if user.id is None:
            return False
        return self.liker.filter_by(
            liker_id=user.id).first() is not None

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'div', 'iframe',
                        'p', 'br', 'span', 'hr', 'src', 'class',
                        'table', 'tr', 'th']
        allowed_attrs = {'*': ['class'],
                         'a': ['href', 'rel'],
                         'img': ['src', 'alt']}
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post = db.relationship('Post', back_populates='comments', lazy='joined')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    is_anonymous = db.Column(db.Boolean, default=False)

    # 被回复的评论的id
    replied_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    # 回复
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    # 表示被回复的评论
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Like(db.Model):
    __tablename__ = 'likes'
    liker_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    liked_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    liker = db.relationship('User', back_populates='liked_post', lazy='joined')
    liked_post = db.relationship('Post', back_populates='liker', lazy='joined')


class Collect(db.Model):
    __tablename__ = 'collect'
    collecter_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    collected_transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    collecter = db.relationship('User', back_populates='collected_transaction', lazy='joined')
    collected_transaction = db.relationship('Transaction', back_populates='collecter', lazy='joined')


class Want(db.Model):
    __tablename__ = 'want'
    wanter_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    wanted_Activity_id = db.Column(db.Integer, db.ForeignKey('Activity.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    wanter = db.relationship('User', back_populates='wanted_Activity', lazy='joined')
    wanted_Activity = db.relationship('Activity', back_populates='wanter', lazy='joined')


class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), nullable=False)
    action = db.Column(db.Text, nullable=False)  # has followed \\ has like \\ has comment \\ has reply
    object = db.Column(db.String(64), nullable=False)  # you \\ your posting \\ your comment
    object_id = db.Column(db.Integer)  # posting

    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver = db.relationship('User', back_populates='notifications', lazy='joined')


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    item_name = db.Column(db.String(64), nullable=False)
    item_describe = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    transaction_mode = db.Column(db.String(64), nullable=False)
    is_sold = db.Column(db.Boolean, default=False)
    seller_WeChat = db.Column(db.Text, nullable=False)

    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    seller = db.relationship('User', back_populates='transactions', lazy='joined')
    collecter = db.relationship('Collect', back_populates='collected_transaction', lazy='dynamic', cascade='all')

    def collect(self, user):
        if not self.is_collected_by(user):
            ll = Collect(collecter=user, collected_transaction=self)
            db.session.add(ll)

    def not_collect(self, user):
        ll = self.collecter.filter_by(collecter_id=user.id).first()
        if ll:
            db.session.delete(ll)

    def is_collected_by(self, user):
        if user.id is None:
            return False
        return self.collecter.filter_by(
            collecter_id=user.id).first() is not None


class Activity(db.Model):
    __tablename__ = 'Activity'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    activity_name = db.Column(db.String(256), nullable=False)
    activity_time = db.Column(db.String(256), nullable=False)
    activity_place = db.Column(db.String(256), nullable=False)
    activity_describe = db.Column(db.String(256), nullable=False)
    Organizer = db.Column(db.String(256), nullable=False)
    is_schoolAgree = db.Column(db.Boolean, nullable=False)

    announcer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    announcer = db.relationship('User', back_populates='activities', lazy='joined')
    wanter = db.relationship('Want', back_populates='wanted_Activity', lazy='dynamic', cascade='all')

    def want(self, user):
        if not self.is_wanted_by(user):
            ll = Like(wanter=user, wanted_post=self)
            db.session.add(ll)

    def not_want(self, user):
        ll = self.wanter.filter_by(wanter_id=user.id).first()
        if ll:
            db.session.delete(ll)

    def is_wanted_by(self, user):
        if user.id is None:
            return False
        return self.wanter.filter_by(
            wanter_id=user.id).first() is not None

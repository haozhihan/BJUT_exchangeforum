from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment, Transaction, Activity


def users(count=100):
    fake = Faker()
    """fake organs"""
    o = User(student_id="99999999",
             ID_number=fake.ssn(),
             email=fake.email(),
             username="Student Union",
             password='password',
             avatar_img='/static/Image/ico.jpeg',
             confirmed=True,
             grade="Sophomore",
             college="Beijing-Dublin International college",
             about_me=fake.sentence(),
             member_since=fake.past_date())
    db.session.add(o)
    """fake users"""
    i = 0
    while i < count:
        u = User(student_id=fake.ean8(),
                 ID_number=fake.ssn(),
                 email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 role_id=1,
                 grade="Sophomore",
                 college="Beijing-Dublin International college",
                 about_me=fake.sentence(),
                 member_since=fake.past_date())
        try:
            db.session.add(u)
            db.session.commit()
            o.role_id = 2
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=200):
    fake = Faker()
    """fake posts"""
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(8000),
                 title=fake.sentence(),
                 timestamp=fake.past_date(),
                 author=u)
        if i % 10 == 0:
            p.is_anonymous = True
        db.session.add(p)
    db.session.commit()


def comments(count=300):
    fake = Faker()
    """fake comments"""
    user_count = User.query.count()
    post_count = Post.query.count()
    for i in range(count):
        comment = Comment(
            author=User.query.get(randint(0, user_count - 1)),
            body=fake.text(),
            timestamp=fake.past_date(),
            post=Post.query.get(randint(0, post_count - 1))
        )
        db.session.add(comment)
    salt = int(count * 0.1)
    for i in range(salt):
        comment = Comment(
            author=User.query.get(randint(0, user_count - 1)),
            body=fake.text(),
            timestamp=fake.past_date(),
            post=Post.query.get(randint(0, post_count - 1)),
            is_anonymous=True
        )
        db.session.add(comment)
    db.session.commit()


def transactions(count=50):
    fake = Faker()
    """fake transactions"""
    user_count = User.query.count()
    i = 0
    while i < count:
        seller = User.query.get(randint(0, user_count - 1))
        t = Transaction(
            seller=seller,
            link=fake.url(),
            item_describe=fake.sentence(),
            item_name=fake.word(),
            seller_WeChat=fake.pystr(),
            transaction_mode=fake.sentence()
        )
        db.session.add(t)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def activities(count=50):
    fake = Faker()
    """fake activities"""
    user_count = User.query.count()
    i = 1
    while i < count:
        a = Activity(
            activity_name=fake.sentence(),
            activity_time=fake.future_date(),
            activity_place=fake.address(),
            activity_describe=fake.sentence(),
            Organizer=fake.name(),
            is_schoolAgree=fake.boolean(),
            is_invalid=fake.boolean(),
            announcer=User.query.get(1),
        )
        db.session.add(a)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


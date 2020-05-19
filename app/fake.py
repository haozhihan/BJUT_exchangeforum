from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment, Organization, Activity, Transaction


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(student_id=fake.ean8(),
                 ID_number=fake.ssn(),
                 email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 role_id=1,
                 about_me=fake.sentence(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=200):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(8000),
                 title=fake.sentence(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()

    salt = int(count*0.1)
    for i in range(salt):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 title=fake.sentence(),
                 timestamp=fake.past_date(),
                 author=u,
                 is_anonymous=True)
        db.session.add(p)
    db.session.commit()


def comments(count=300):
    fake = Faker()
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


def organization(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(student_id=fake.ean8(),
                 ID_number=fake.ssn(),
                 email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 role_id=2,
                 about_me=fake.sentence(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def activity(count=100):
    fake = Faker()
    user_count = User.query.filter_by(role_id=2).count()
    for i in range(count):
        u = Activity(timestamp=fake.past_date(),
                     activity_name=fake.name(),
                     activity_time=fake.past_date(),
                     activity_place="Teaching Building 4",
                     activity_describe=fake.text(),
                     Organizer="HanHaoZhi",
                     is_schoolAgree=True,
                     is_invalid=False,
                     announcer=User.query.get(randint(0, user_count - 1)),
                     )
        db.session.add(u)
    db.session.commit()


def transaction(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = Transaction(timestamp=fake.past_date(),
                        item_name=fake.name(),
                        item_describe=fake.text(),
                        link=fake.text(),
                        transaction_mode=fake.text(),
                        is_sold=False,
                        seller_WeChat=fake.text(),
                        seller=User.query.get(randint(0, user_count - 1)),
                        )
        db.session.add(u)
    db.session.commit()
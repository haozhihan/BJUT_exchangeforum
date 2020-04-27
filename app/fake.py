from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment


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
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 title=fake.sentence(),
                 timestamp=fake.past_date(),
                 author=u)
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
    db.session.commit()



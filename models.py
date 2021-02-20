from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4


db = SQLAlchemy()


class Base(object):
    id = db.Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    modified = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


    def to_dict(cls):
        data = {
            c.key: getattr(cls, c.key) for c in inspect(cls).mapper.column_attrs
        }

        return data


class User(Base, db.Model):
    __tablename__ = 'users'


    email = db.Column(db.String(256), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    # 0 - admin
    # 1 - member
    membership_type = db.Column(db.Integer, nullable=False, default=1)
    lists = db.relationship('List', backref='users', lazy='dynamic')
    tokens = db.relationship('Token', backref='tokens', lazy='dynamic')


    @classmethod
    def generate_password(cls, password):
        return generate_password_hash(password, "sha256")


    @classmethod
    def is_match_password(cls, password_hash, password):
        return check_password_hash(password_hash, password)


class List(Base, db.Model):
    __tablename__ = 'lists'


    title = db.Column(db.String(256), nullable=False)
    cards = db.relationship('Card', backref='lists', lazy='subquery')
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)


class Card(Base, db.Model):
    __tablename__ = 'cards'


    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(512), nullable=True)
    list_id = db.Column(UUID(as_uuid=True), db.ForeignKey('lists.id'), nullable=False)
    comments = db.relationship('Comment', backref='cards', lazy='dynamic')
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)


class Comment(Base, db.Model):
    __tablename__ = 'comments'


    content = db.Column(db.String(512), nullable=False)
    card_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cards.id'), nullable=False)
    replies = db.relationship('Reply', backref='comments', lazy='dynamic')
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)


class Reply(Base, db.Model):
    __tablename__ = 'replies'


    content = db.Column(db.String(512), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('comments.id'), nullable=False)


class Token(Base, db.Model):
    __tablename__ = 'tokens'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False, default=datetime.now() + timedelta(days=30))

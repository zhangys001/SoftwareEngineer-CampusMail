# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='student')
    phone = db.Column(db.String(11), nullable=True)
    status = db.Column(db.String(10), nullable=False, default='normal')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    @property
    def is_active(self):
        return self.status == 'normal'

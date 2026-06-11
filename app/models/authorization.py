# -*- coding: utf-8 -*-
from . import db


class Authorization(db.Model):
    __tablename__ = 'authorization'

    auth_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.package_id'), nullable=False)
    authorizer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    authorizee_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    auth_code = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='valid')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

    package = db.relationship('Package', backref='authorizations')
    authorizer = db.relationship('User', foreign_keys=[authorizer_id], backref='auth_given')
    authorizee = db.relationship('User', foreign_keys=[authorizee_id], backref='auth_received')

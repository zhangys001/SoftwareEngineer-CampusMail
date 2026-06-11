# -*- coding: utf-8 -*-
from . import db


class Notification(db.Model):
    __tablename__ = 'notification'

    notif_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(10), nullable=False, default='system')
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='notifications')

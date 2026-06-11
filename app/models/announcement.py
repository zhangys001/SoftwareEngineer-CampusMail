# -*- coding: utf-8 -*-
from . import db


class Announcement(db.Model):
    __tablename__ = 'announcement'

    ann_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(db.String(15), nullable=False, default='published')
    published_at = db.Column(db.DateTime, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=True)

    publisher = db.relationship('User', backref='announcements')

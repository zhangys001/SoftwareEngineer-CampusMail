# -*- coding: utf-8 -*-
from . import db


class SendOrder(db.Model):
    __tablename__ = 'send_order'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    sender_name = db.Column(db.String(20), nullable=False)
    sender_phone = db.Column(db.String(11), nullable=False)
    receiver_name = db.Column(db.String(20), nullable=False)
    receiver_phone = db.Column(db.String(11), nullable=False)
    receiver_addr = db.Column(db.String(200), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('express_company.company_id'), nullable=False)
    item_type = db.Column(db.String(15), nullable=False, default='other')
    status = db.Column(db.String(15), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    sender = db.relationship('User', backref='send_orders')
    company = db.relationship('ExpressCompany', backref='send_orders')

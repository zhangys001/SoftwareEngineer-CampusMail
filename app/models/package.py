# -*- coding: utf-8 -*-
from . import db


class Package(db.Model):
    __tablename__ = 'package'

    package_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracking_no = db.Column(db.String(30), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('express_company.company_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelf.shelf_id'), nullable=True)
    slot_code = db.Column(db.String(10), nullable=True)
    pickup_code = db.Column(db.String(10), nullable=False)
    package_type = db.Column(db.String(10), nullable=False, default='normal')
    status = db.Column(db.String(10), nullable=False, default='pending')
    arrived_at = db.Column(db.DateTime, server_default=db.func.now())
    picked_at = db.Column(db.DateTime, nullable=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    company = db.relationship('ExpressCompany', backref='packages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_packages')
    shelf = db.relationship('Shelf', backref='packages')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='operated_packages')

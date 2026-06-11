# -*- coding: utf-8 -*-
from . import db


class PickupRecord(db.Model):
    __tablename__ = 'pickup_record'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.package_id'), nullable=False)
    picker_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    pickup_type = db.Column(db.String(10), nullable=False, default='self')
    operator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    picked_at = db.Column(db.DateTime, server_default=db.func.now())

    package = db.relationship('Package', backref='pickup_record')
    picker = db.relationship('User', foreign_keys=[picker_id], backref='pickup_records')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='pickup_operations')

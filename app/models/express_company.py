# -*- coding: utf-8 -*-
from . import db


class ExpressCompany(db.Model):
    __tablename__ = 'express_company'

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='enabled')

# -*- coding: utf-8 -*-
from . import db


class Shelf(db.Model):
    __tablename__ = 'shelf'

    shelf_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shelf_code = db.Column(db.String(10), unique=True, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False, default=20)
    used_slots = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(15), nullable=False, default='normal')

    @property
    def free_slots(self):
        return self.total_slots - self.used_slots

    @property
    def usage_rate(self):
        if self.total_slots == 0:
            return 0
        return round(self.used_slots / self.total_slots * 100)

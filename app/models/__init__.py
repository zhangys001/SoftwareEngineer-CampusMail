# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .express_company import ExpressCompany
from .shelf import Shelf
from .package import Package
from .pickup_record import PickupRecord
from .authorization import Authorization
from .send_order import SendOrder
from .announcement import Announcement
from .notification import Notification

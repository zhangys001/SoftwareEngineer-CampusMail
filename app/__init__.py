# -*- coding: utf-8 -*-
import os
from flask import Flask
from .models import db


def create_app(test_db_uri=None):
    app = Flask(__name__)

    from datetime import timedelta

    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # 固定SECRET_KEY，保证重启后session不失效；生产环境应从环境变量读取
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'campus-mail-secret-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = test_db_uri or ('sqlite:///' + os.path.join(base_dir, 'campus_mail.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Session config — 支持多用户并发登录
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_NAME'] = 'campus_mail_session'

    db.init_app(app)

    from .routes.auth import auth_bp
    from .routes.student import student_bp
    from .routes.staff import staff_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    return app

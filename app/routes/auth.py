# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('请输入账号和密码', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('账号或密码错误', 'error')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('账号已被禁用', 'error')
            return render_template('auth/login.html')

        session.permanent = True
        session['user_id'] = user.user_id
        session['role'] = user.role
        session['name'] = user.name

        if user.role == 'student':
            return redirect(url_for('student.home'))
        elif user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('admin.overview'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

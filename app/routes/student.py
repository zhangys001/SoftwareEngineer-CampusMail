# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from ..models import db, Package, ExpressCompany, Shelf, Authorization, SendOrder, User, Notification

student_bp = Blueprint('student', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/')
@login_required
def home():
    user_id = session['user_id']
    pending = Package.query.filter_by(receiver_id=user_id, status='pending').count()
    picked = Package.query.filter_by(receiver_id=user_id, status='picked').count()
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    announcements = db.session.execute(db.text("SELECT title, content FROM announcement WHERE status='published' ORDER BY published_at DESC LIMIT 1")).all()
    return render_template('student/home.html', pending=pending, picked=picked, notifications=notifications, announcements=announcements)


@student_bp.route('/packages')
@login_required
def packages():
    user_id = session['user_id']
    status_filter = request.args.get('status', '')
    q = Package.query.filter_by(receiver_id=user_id)
    if status_filter:
        q = q.filter_by(status=status_filter)
    pkg_list = q.order_by(Package.arrived_at.desc()).all()
    return render_template('student/packages.html', packages=pkg_list, status_filter=status_filter)


@student_bp.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    user_id = session['user_id']
    pkg = Package.query.filter_by(package_id=package_id, receiver_id=user_id).first_or_404()
    return render_template('student/package_detail.html', package=pkg)


@student_bp.route('/pickup/<int:package_id>')
@login_required
def pickup_code(package_id):
    user_id = session['user_id']
    pkg = Package.query.filter_by(package_id=package_id, receiver_id=user_id).first_or_404()
    return render_template('student/pickup_code.html', package=pkg)


@student_bp.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    user_id = session['user_id']
    user = User.query.get(user_id)
    companies = ExpressCompany.query.filter_by(status='enabled').all()

    if request.method == 'POST':
        receiver_name = request.form.get('receiver_name', '').strip()
        receiver_phone = request.form.get('receiver_phone', '').strip()
        receiver_addr = request.form.get('receiver_addr', '').strip()
        company_id_raw = request.form.get('company_id')
        item_type = request.form.get('item_type', 'other')

        if not receiver_name:
            flash('请输入收件人姓名', 'error')
            return redirect(url_for('student.send'))

        if not receiver_phone:
            flash('请输入收件人电话', 'error')
            return redirect(url_for('student.send'))

        if not receiver_addr:
            flash('请输入收件人地址', 'error')
            return redirect(url_for('student.send'))

        if not company_id_raw:
            flash('请选择快递公司', 'error')
            return redirect(url_for('student.send'))

        order = SendOrder(
            sender_id=user_id,
            sender_name=user.name,
            sender_phone=user.phone or '',
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_addr=receiver_addr,
            company_id=int(company_id_raw),
            item_type=item_type,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        flash('寄件预约已提交，工作人员将联系您', 'success')
        return redirect(url_for('student.send_list'))

    return render_template('student/send.html', companies=companies, user=user)


@student_bp.route('/send/list')
@login_required
def send_list():
    user_id = session['user_id']
    orders = SendOrder.query.filter_by(sender_id=user_id).order_by(SendOrder.created_at.desc()).all()
    return render_template('student/send_list.html', orders=orders)


@student_bp.route('/authorization', methods=['GET', 'POST'])
@login_required
def authorization():
    user_id = session['user_id']
    pending_packages = Package.query.filter_by(receiver_id=user_id, status='pending').all()

    if request.method == 'POST':
        package_id_raw = request.form.get('package_id')
        authorizee_username = request.form.get('authorizee_username', '').strip()

        if not package_id_raw:
            flash('请选择要授权的包裹', 'error')
            return redirect(url_for('student.authorization'))

        package_id = int(package_id_raw)

        authorizee = User.query.filter_by(username=authorizee_username, role='student').first()
        if not authorizee:
            flash('被授权人账号不存在', 'error')
            return redirect(url_for('student.authorization'))

        existing = Authorization.query.filter_by(package_id=package_id, status='valid').first()
        if existing:
            flash('该快递已有有效授权，请先撤销', 'error')
            return redirect(url_for('student.authorization'))

        import uuid
        auth_code = f"AUTH-{uuid.uuid4().hex[:8].upper()}"
        auth_record = Authorization(
            package_id=package_id,
            authorizer_id=user_id,
            authorizee_id=authorizee.user_id,
            auth_code=auth_code,
            status='valid',
            expires_at=datetime.now() + timedelta(hours=24)
        )
        db.session.add(auth_record)
        db.session.commit()
        flash(f'授权成功！授权码: {auth_code}', 'success')
        return redirect(url_for('student.authorization'))

    my_auths = Authorization.query.filter_by(authorizer_id=user_id).order_by(Authorization.created_at.desc()).all()
    return render_template('student/authorization.html', pending_packages=pending_packages, my_auths=my_auths)


@student_bp.route('/authorization/revoke/<int:auth_id>')
@login_required
def revoke_auth(auth_id):
    user_id = session['user_id']
    auth_record = Authorization.query.filter_by(auth_id=auth_id, authorizer_id=user_id, status='valid').first_or_404()
    auth_record.status = 'revoked'
    db.session.commit()
    flash('授权已撤销', 'success')
    return redirect(url_for('student.authorization'))


@student_bp.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('student/notifications.html', notifications=notifs)


@student_bp.route('/notifications/read/<int:notif_id>')
@login_required
def read_notification(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.is_read = True
    db.session.commit()
    return jsonify({'ok': True})

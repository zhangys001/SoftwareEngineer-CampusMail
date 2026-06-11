# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import db, User, Package, ExpressCompany, Announcement, PickupRecord, SendOrder
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_bp.route('/overview')
@admin_required
def overview():
    total_packages = Package.query.count()
    this_month = datetime.now().replace(day=1)
    month_packages = Package.query.filter(Package.arrived_at >= this_month).count()
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_in = Package.query.filter(Package.arrived_at >= today_start).count()
    today_out = Package.query.filter(Package.picked_at >= today_start, Package.status == 'picked').count()

    staff_count = User.query.filter_by(role='staff').count()
    student_count = User.query.filter_by(role='student').count()
    pending = Package.query.filter_by(status='pending').count()

    total_verify = PickupRecord.query.count()
    correct_verify = total_verify
    accuracy = 100.0 if total_verify == 0 else round(correct_verify / total_verify * 100, 1)

    seven_days_ago = datetime.now() - timedelta(days=7)
    trend = db.session.query(
        func.date(Package.arrived_at).label('day'),
        func.count().label('count')
    ).filter(Package.arrived_at >= seven_days_ago
    ).group_by(func.date(Package.arrived_at)).order_by(func.date(Package.arrived_at)).all()

    company_dist = db.session.query(
        ExpressCompany.company_name,
        func.count(Package.package_id).label('count')
    ).join(Package, ExpressCompany.company_id == Package.company_id
    ).group_by(ExpressCompany.company_name).all()

    return render_template('admin/overview.html',
                           total_packages=total_packages, month_packages=month_packages,
                           today_in=today_in, today_out=today_out,
                           staff_count=staff_count, student_count=student_count,
                           pending=pending, accuracy=accuracy,
                           trend=trend, company_dist=company_dist)


@admin_bp.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            username = request.form.get('username', '').strip()
            name = request.form.get('name', '').strip()
            role = request.form.get('role', 'student')
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '123456').strip()

            if User.query.filter_by(username=username).first():
                flash('该账号已存在', 'error')
                return redirect(url_for('admin.users'))

            user = User(username=username, name=name, role=role, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('用户添加成功', 'success')

        elif action == 'toggle':
            user_id = int(request.form.get('user_id'))
            user = User.query.get(user_id)
            if user:
                user.status = 'disabled' if user.status == 'normal' else 'normal'
                db.session.commit()
                flash(f'用户 {user.name} 已{"禁用" if user.status == "disabled" else "启用"}', 'success')

        return redirect(url_for('admin.users'))

    search = request.args.get('search', '').strip()
    q = User.query
    if search:
        q = q.filter(
            db.or_(User.username.contains(search), User.name.contains(search))
        )
    user_list = q.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=user_list, search=search)


@admin_bp.route('/announcements', methods=['GET', 'POST'])
@admin_required
def announcements():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            if title and content:
                ann = Announcement(title=title, content=content, publisher_id=session['user_id'])
                db.session.add(ann)
                db.session.commit()
                flash('公告已发布', 'success')

        elif action == 'withdraw':
            ann_id = int(request.form.get('ann_id'))
            ann = Announcement.query.get(ann_id)
            if ann:
                ann.status = 'withdrawn'
                db.session.commit()
                flash('公告已撤回', 'success')

        elif action == 'delete':
            ann_id = int(request.form.get('ann_id'))
            ann = Announcement.query.get(ann_id)
            if ann:
                db.session.delete(ann)
                db.session.commit()
                flash('公告已删除', 'success')

        return redirect(url_for('admin.announcements'))

    ann_list = Announcement.query.order_by(Announcement.published_at.desc()).all()
    return render_template('admin/announcements.html', announcements=ann_list)


@admin_bp.route('/stats', methods=['GET', 'POST'])
@admin_required
def stats():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    stats_data = []

    if start_date and end_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d')
            ed = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            daily = db.session.query(
                func.date(Package.arrived_at).label('day'),
                func.count().label('in_count')
            ).filter(Package.arrived_at >= sd, Package.arrived_at < ed
            ).group_by(func.date(Package.arrived_at)).all()

            daily_out = db.session.query(
                func.date(Package.picked_at).label('day'),
                func.count().label('out_count')
            ).filter(Package.picked_at >= sd, Package.picked_at < ed, Package.status == 'picked'
            ).group_by(func.date(Package.picked_at)).all()

            out_map = {str(r.day): r.out_count for r in daily_out}
            in_map = {str(r.day): r.in_count for r in daily}

            all_days = sorted(set(list(in_map.keys()) + list(out_map.keys())))
            for day_str in all_days:
                in_c = in_map.get(day_str, 0)
                out_c = out_map.get(day_str, 0)
                stats_data.append({
                    'date': day_str,
                    'in_count': in_c,
                    'out_count': out_c,
                    'retained': in_c - out_c
                })
        except ValueError:
            flash('日期格式无效', 'error')

    return render_template('admin/stats.html', stats_data=stats_data,
                           start_date=start_date, end_date=end_date)

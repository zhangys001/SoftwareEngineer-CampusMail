# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import db, Package, ExpressCompany, Shelf, User, PickupRecord, Notification, Authorization

staff_bp = Blueprint('staff', __name__)


def staff_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ('staff', 'admin'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@staff_bp.route('/')
@staff_bp.route('/dashboard')
@staff_required
def dashboard():
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())

    today_in = Package.query.filter(Package.arrived_at >= today_start).count()
    today_out = Package.query.filter(
        Package.picked_at >= today_start,
        Package.status == 'picked'
    ).count()
    pending = Package.query.filter_by(status='pending').count()
    stale = Package.query.filter(
        Package.status == 'pending',
        Package.arrived_at <= datetime.now() - timedelta(hours=72)
    ).count()

    recent_in = Package.query.filter(Package.arrived_at >= today_start).order_by(Package.arrived_at.desc()).limit(10).all()
    stale_list = Package.query.filter(
        Package.status == 'pending',
        Package.arrived_at <= datetime.now() - timedelta(hours=72)
    ).order_by(Package.arrived_at.asc()).limit(10).all()

    return render_template('staff/dashboard.html',
                           today_in=today_in, today_out=today_out,
                           pending=pending, stale=stale,
                           recent_in=recent_in, stale_list=stale_list)


@staff_bp.route('/checkin', methods=['GET', 'POST'])
@staff_required
def checkin():
    companies = ExpressCompany.query.filter_by(status='enabled').all()
    shelves = Shelf.query.filter(Shelf.status != 'disabled').order_by(Shelf.shelf_code).all()

    if request.method == 'POST':
        tracking_no = request.form.get('tracking_no', '').strip()
        company_id_raw = request.form.get('company_id')
        receiver_username = request.form.get('receiver_username', '').strip()
        shelf_id_raw = request.form.get('shelf_id')
        package_type = request.form.get('package_type', 'normal')

        if not tracking_no:
            flash('请输入快递单号', 'error')
            return redirect(url_for('staff.checkin'))

        if not company_id_raw:
            flash('请选择快递公司', 'error')
            return redirect(url_for('staff.checkin'))

        if not shelf_id_raw:
            flash('请选择分配货架', 'error')
            return redirect(url_for('staff.checkin'))

        company_id = int(company_id_raw)
        shelf_id = int(shelf_id_raw)

        existing = Package.query.filter_by(tracking_no=tracking_no).first()
        if existing:
            flash('该单号已录入，请勿重复操作', 'error')
            return redirect(url_for('staff.checkin'))

        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            flash('收件人账号不存在', 'error')
            return redirect(url_for('staff.checkin'))

        shelf = Shelf.query.get(shelf_id)
        if shelf.free_slots <= 0:
            flash('所选货架已满，请选择其他货架', 'error')
            return redirect(url_for('staff.checkin'))

        import random
        slot_num = shelf.used_slots + 1
        slot_code = f"{shelf.shelf_code}-{slot_num}"
        pickup_code = f"{shelf.shelf_code}-{slot_num:02d}"

        pkg = Package(
            tracking_no=tracking_no,
            company_id=company_id,
            receiver_id=receiver.user_id,
            shelf_id=shelf_id,
            slot_code=slot_code,
            pickup_code=pickup_code,
            package_type=package_type,
            status='pending',
            operator_id=session['user_id']
        )
        shelf.used_slots += 1
        if shelf.usage_rate >= 90:
            shelf.status = 'almost_full'

        notif = Notification(
            user_id=receiver.user_id,
            content=f'您的快递已到达驿站，取件码: {pickup_code}，货架: {slot_code}',
            type='pickup'
        )
        db.session.add(pkg)
        db.session.add(notif)
        db.session.commit()

        flash(f'快递入库成功！取件码: {pickup_code}，已通知收件人', 'success')
        return redirect(url_for('staff.checkin'))

    return render_template('staff/checkin.html', companies=companies, shelves=shelves)


@staff_bp.route('/checkout', methods=['GET', 'POST'])
@staff_required
def checkout():
    if request.method == 'POST':
        pickup_code = request.form.get('pickup_code', '').strip()
        auth_code = request.form.get('auth_code', '').strip()

        if not pickup_code:
            flash('请输入取件码或快递单号', 'error')
            return redirect(url_for('staff.checkout'))

        # 支持取件码和快递单号两种输入方式
        pkg = Package.query.filter_by(pickup_code=pickup_code, status='pending').first()
        if not pkg:
            pkg = Package.query.filter_by(tracking_no=pickup_code, status='pending').first()
        if not pkg:
            flash('未找到待出库的快递，请检查输入是否正确', 'error')
            return redirect(url_for('staff.checkout'))

        # 判断取件方式：有授权码则验证代取
        if auth_code:
            auth_record = Authorization.query.filter_by(
                package_id=pkg.package_id,
                auth_code=auth_code,
                status='valid'
            ).first()
            if not auth_record:
                flash('授权码无效或已过期，请检查后重试', 'error')
                return redirect(url_for('staff.checkout'))
            if auth_record.expires_at < datetime.now():
                auth_record.status = 'expired'
                db.session.commit()
                flash('授权码已过期，请联系发件人重新授权', 'error')
                return redirect(url_for('staff.checkout'))
            picker_id = auth_record.authorizee_id
            pickup_type = 'proxy'
            # 标记授权为已使用
            auth_record.status = 'used'
            picker_name = User.query.get(picker_id).name if picker_id else '未知'
        else:
            picker_id = pkg.receiver_id
            pickup_type = 'self'
            picker_name = pkg.receiver.name if pkg.receiver else '未知'

        pkg.status = 'picked'
        pkg.picked_at = datetime.now()

        if pkg.shelf:
            pkg.shelf.used_slots = max(0, pkg.shelf.used_slots - 1)
            if pkg.shelf.usage_rate < 90:
                pkg.shelf.status = 'normal'

        record = PickupRecord(
            package_id=pkg.package_id,
            picker_id=picker_id,
            pickup_type=pickup_type,
            operator_id=session['user_id']
        )
        db.session.add(record)
        db.session.commit()

        type_label = '授权代取' if pickup_type == 'proxy' else '本人取件'
        flash(f'核销成功！快递 {pkg.tracking_no} 已出库（{type_label}，取件人：{picker_name}）', 'success')
        return redirect(url_for('staff.checkout'))

    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_records = db.session.query(
        PickupRecord, Package.tracking_no, Package.pickup_code,
        User.name.label('picker_name')
    ).join(Package, PickupRecord.package_id == Package.package_id
    ).join(User, PickupRecord.picker_id == User.user_id
    ).filter(PickupRecord.picked_at >= today_start
    ).order_by(PickupRecord.picked_at.desc()).limit(20).all()

    return render_template('staff/checkout.html', today_records=today_records)


@staff_bp.route('/shelf')
@staff_required
def shelf():
    shelves = Shelf.query.filter(Shelf.status != 'disabled').order_by(Shelf.shelf_code).all()
    total = len(shelves)
    in_use = sum(1 for s in shelves if s.used_slots > 0)
    free = sum(1 for s in shelves if s.used_slots == 0)
    total_slots = sum(s.total_slots for s in shelves)
    used_slots = sum(s.used_slots for s in shelves)
    usage_rate = round(used_slots / total_slots * 100) if total_slots > 0 else 0

    return render_template('staff/shelf.html', shelves=shelves,
                           total=total, in_use=in_use, free=free,
                           usage_rate=usage_rate)


@staff_bp.route('/send_reminder/<int:package_id>')
@staff_required
def send_reminder(package_id):
    pkg = Package.query.get_or_404(package_id)
    notif = Notification(
        user_id=pkg.receiver_id,
        content=f'您的快递 {pkg.pickup_code} 已滞留，请尽快取件！',
        type='overtime'
    )
    db.session.add(notif)
    db.session.commit()
    flash('取件提醒已发送', 'success')
    return redirect(url_for('staff.dashboard'))

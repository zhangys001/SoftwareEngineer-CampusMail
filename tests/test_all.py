# -*- coding: utf-8 -*-
"""全模块系统测试 - 覆盖所有功能"""
import unittest
from datetime import datetime, timedelta
from app import create_app
from app.models import (db, Package, PickupRecord, Shelf, User,
                        ExpressCompany, Authorization, SendOrder,
                        Announcement, Notification)


class BaseTestCase(unittest.TestCase):
    """基础测试类"""
    def setUp(self):
        self.app = create_app(test_db_uri='sqlite://')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self._seed_data()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.engine.dispose()

    def _seed_data(self):
        """创建测试数据"""
        # 用户
        staff = User(username='STAFF001', name='王员工', role='staff', phone='13700004444')
        staff.set_password('123456')
        db.session.add(staff)

        student1 = User(username='student', name='张同学', role='student', phone='13800001111')
        student1.set_password('123456')
        db.session.add(student1)

        student2 = User(username='2021002002', name='李同学', role='student', phone='13900002222')
        student2.set_password('123456')
        db.session.add(student2)

        admin = User(username='admin', name='管理员', role='admin', phone='13300000000')
        admin.set_password('123456')
        db.session.add(admin)

        disabled_user = User(username='disabled', name='禁用用户', role='student', phone='13500009999', status='disabled')
        disabled_user.set_password('123456')
        db.session.add(disabled_user)
        db.session.flush()

        # 快递公司
        company = ExpressCompany(company_name='圆通速递')
        db.session.add(company)
        company2 = ExpressCompany(company_name='顺丰速运')
        db.session.add(company2)
        db.session.flush()

        # 货架
        shelf1 = Shelf(shelf_code='B-1', total_slots=20, used_slots=1)
        db.session.add(shelf1)
        shelf2 = Shelf(shelf_code='B-2', total_slots=20, used_slots=0)
        db.session.add(shelf2)
        # 满货架
        shelf_full = Shelf(shelf_code='B-3', total_slots=5, used_slots=5)
        db.session.add(shelf_full)
        db.session.flush()

        # 包裹
        pkg1 = Package(
            tracking_no='YT20260612001', company_id=company.company_id,
            receiver_id=student1.user_id, shelf_id=shelf1.shelf_id,
            slot_code='B-1-01', pickup_code='B-1-01', package_type='normal',
            status='pending', operator_id=staff.user_id
        )
        db.session.add(pkg1)

        pkg2 = Package(
            tracking_no='SF20260612002', company_id=company2.company_id,
            receiver_id=student2.user_id, shelf_id=shelf1.shelf_id,
            slot_code='B-1-02', pickup_code='B-1-02', package_type='document',
            status='pending', operator_id=staff.user_id
        )
        db.session.add(pkg2)

        pkg_picked = Package(
            tracking_no='ZT20260612003', company_id=company.company_id,
            receiver_id=student1.user_id, shelf_id=shelf1.shelf_id,
            slot_code='B-1-03', pickup_code='B-1-03', package_type='large',
            status='picked', operator_id=staff.user_id,
            picked_at=datetime.now() - timedelta(hours=1)
        )
        db.session.add(pkg_picked)
        db.session.flush()

        # 已有取件记录
        record = PickupRecord(
            package_id=pkg_picked.package_id, picker_id=student1.user_id,
            pickup_type='self', operator_id=staff.user_id,
            picked_at=pkg_picked.picked_at
        )
        db.session.add(record)

        # 授权记录
        auth = Authorization(
            package_id=pkg1.package_id, authorizer_id=student1.user_id,
            authorizee_id=student2.user_id, auth_code='AUTH-TEST01',
            status='valid', expires_at=datetime.now() + timedelta(hours=24)
        )
        db.session.add(auth)

        auth_used = Authorization(
            package_id=pkg_picked.package_id, authorizer_id=student1.user_id,
            authorizee_id=student2.user_id, auth_code='AUTH-USED01',
            status='used', expires_at=datetime.now() + timedelta(hours=24),
            created_at=datetime.now() - timedelta(hours=2)
        )
        db.session.add(auth_used)

        auth_expired = Authorization(
            package_id=pkg2.package_id, authorizer_id=student2.user_id,
            authorizee_id=student1.user_id, auth_code='AUTH-EXPIRED',
            status='valid', expires_at=datetime.now() - timedelta(hours=1)
        )
        db.session.add(auth_expired)

        # 寄件订单
        order = SendOrder(
            sender_id=student1.user_id, sender_name='张同学',
            sender_phone='13800001111', receiver_name='李老师',
            receiver_phone='13912345678', receiver_addr='北京市海淀区',
            company_id=company.company_id, item_type='document',
            status='pending'
        )
        db.session.add(order)

        # 公告
        ann = Announcement(
            title='测试公告', content='这是测试公告内容',
            publisher_id=admin.user_id, status='published'
        )
        db.session.add(ann)

        # 通知
        notif = Notification(
            user_id=student1.user_id, content='您的快递已到达',
            type='pickup', is_read=False
        )
        db.session.add(notif)
        db.session.commit()

        self.staff_id = staff.user_id
        self.student1_id = student1.user_id
        self.student2_id = student2.user_id
        self.admin_id = admin.user_id
        self.company_id = company.company_id
        self.shelf1_id = shelf1.shelf_id
        self.shelf_full_id = shelf_full.shelf_id
        self.pkg1_id = pkg1.package_id
        self.pkg2_id = pkg2.package_id
        self.pkg_picked_id = pkg_picked.package_id
        self.auth_id = auth.auth_id
        self.order_id = order.order_id
        self.ann_id = ann.ann_id
        self.notif_id = notif.notif_id

    def _login(self, user_id, role):
        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['role'] = role
            sess['name'] = 'test'


# ==================== 登录模块测试 ====================
class TestAuth(BaseTestCase):
    def test_login_page(self):
        """登录页面可访问"""
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)

    def test_login_success_student(self):
        """学生登录成功"""
        resp = self.client.post('/login', data={
            'username': 'student', 'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_success_staff(self):
        """员工登录成功"""
        resp = self.client.post('/login', data={
            'username': 'STAFF001', 'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_success_admin(self):
        """管理员登录成功"""
        resp = self.client.post('/login', data={
            'username': 'admin', 'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_wrong_password(self):
        """错误密码登录失败"""
        resp = self.client.post('/login', data={
            'username': 'STAFF001', 'password': 'wrong'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_empty_fields(self):
        """空字段登录失败"""
        resp = self.client.post('/login', data={
            'username': '', 'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_nonexistent_user(self):
        """不存在的用户登录失败"""
        resp = self.client.post('/login', data={
            'username': 'NOTEXIST', 'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_disabled_user(self):
        """禁用用户登录失败"""
        resp = self.client.post('/login', data={
            'username': 'disabled', 'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_logout(self):
        """退出登录"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)


# ==================== 出库核销测试 ====================
class TestCheckout(BaseTestCase):
    def test_checkout_by_pickup_code(self):
        """TC-001: 取件码出库"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg1_id)
            self.assertEqual(pkg.status, 'picked')

    def test_checkout_by_tracking_no(self):
        """TC-002: 快递单号出库"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'YT20260612001'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg1_id)
            self.assertEqual(pkg.status, 'picked')

    def test_checkout_empty_code(self):
        """TC-003: 空取件码"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={'pickup_code': ''}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg1_id)
            self.assertEqual(pkg.status, 'pending')

    def test_checkout_nonexistent(self):
        """TC-004: 不存在的取件码"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'NONEXIST'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkout_already_picked(self):
        """TC-005: 已出库包裹重复出库"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'B-1-03'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkout_shelf_decrease(self):
        """TC-006: 出库后货架数量减少"""
        self._login(self.staff_id, 'staff')
        with self.app.app_context():
            shelf = Shelf.query.get(self.shelf1_id)
            initial = shelf.used_slots
        self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        with self.app.app_context():
            shelf = Shelf.query.get(self.shelf1_id)
            self.assertEqual(shelf.used_slots, initial - 1)

    def test_checkout_creates_record(self):
        """TC-007: 出库创建取件记录"""
        self._login(self.staff_id, 'staff')
        self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        with self.app.app_context():
            record = PickupRecord.query.filter_by(package_id=self.pkg1_id).first()
            self.assertIsNotNone(record)
            self.assertEqual(record.pickup_type, 'self')

    def test_checkout_unauthorized(self):
        """TC-008: 未登录不能出库"""
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg1_id)
            self.assertEqual(pkg.status, 'pending')

    def test_checkout_with_auth_code(self):
        """TC-009: 授权码代取"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={
            'pickup_code': 'B-1-01', 'auth_code': 'AUTH-TEST01'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg1_id)
            self.assertEqual(pkg.status, 'picked')
            record = PickupRecord.query.filter_by(package_id=self.pkg1_id).first()
            self.assertEqual(record.pickup_type, 'proxy')
            self.assertEqual(record.picker_id, self.student2_id)
            auth = Authorization.query.get(self.auth_id)
            self.assertEqual(auth.status, 'used')

    def test_checkout_invalid_auth_code(self):
        """TC-010: 无效授权码代取失败"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={
            'pickup_code': 'B-1-01', 'auth_code': 'AUTH-WRONG'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg1_id)
            self.assertEqual(pkg.status, 'pending')

    def test_checkout_expired_auth_code(self):
        """过期授权码代取失败"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkout', data={
            'pickup_code': 'B-1-02', 'auth_code': 'AUTH-EXPIRED'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.pkg2_id)
            self.assertEqual(pkg.status, 'pending')


# ==================== 入库登记测试 ====================
class TestCheckin(BaseTestCase):
    def test_checkin_success(self):
        """TC-011: 正常入库"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkin', data={
            'tracking_no': 'NEW20260612099',
            'company_id': self.company_id,
            'receiver_username': 'student',
            'shelf_id': self.shelf1_id,
            'package_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.filter_by(tracking_no='NEW20260612099').first()
            self.assertIsNotNone(pkg)
            self.assertEqual(pkg.status, 'pending')

    def test_checkin_duplicate_tracking(self):
        """TC-012: 重复单号入库"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkin', data={
            'tracking_no': 'YT20260612001',
            'company_id': self.company_id,
            'receiver_username': 'student',
            'shelf_id': self.shelf1_id,
            'package_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkin_invalid_receiver(self):
        """TC-013: 不存在的收件人"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkin', data={
            'tracking_no': 'NEW20260612088',
            'company_id': self.company_id,
            'receiver_username': 'NOTEXIST',
            'shelf_id': self.shelf1_id,
            'package_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkin_full_shelf(self):
        """TC-014: 满货架入库"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkin', data={
            'tracking_no': 'NEW20260612077',
            'company_id': self.company_id,
            'receiver_username': 'student',
            'shelf_id': self.shelf_full_id,
            'package_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkin_empty_tracking(self):
        """TC-015: 空快递单号"""
        self._login(self.staff_id, 'staff')
        resp = self.client.post('/staff/checkin', data={
            'tracking_no': '',
            'company_id': self.company_id,
            'receiver_username': 'student',
            'shelf_id': self.shelf1_id,
            'package_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkin_creates_notification(self):
        """TC-018: 入库后通知收件人"""
        self._login(self.staff_id, 'staff')
        # 记录入库前的通知数量
        with self.app.app_context():
            before_count = Notification.query.filter_by(user_id=self.student1_id, type='pickup').count()

        self.client.post('/staff/checkin', data={
            'tracking_no': 'NEW20260612066',
            'company_id': self.company_id,
            'receiver_username': 'student',
            'shelf_id': self.shelf1_id,
            'package_type': 'normal'
        }, follow_redirects=True)

        with self.app.app_context():
            after_count = Notification.query.filter_by(user_id=self.student1_id, type='pickup').count()
            self.assertEqual(after_count, before_count + 1)
            # 验证存在包含取件码的通知
            pkg = Package.query.filter_by(tracking_no='NEW20260612066').first()
            notif = Notification.query.filter(
                Notification.user_id == self.student1_id,
                Notification.type == 'pickup',
                Notification.content.contains(pkg.pickup_code)
            ).first()
            self.assertIsNotNone(notif, f'未找到包含取件码{pkg.pickup_code}的通知')


# ==================== 学生端测试 ====================
class TestStudent(BaseTestCase):
    def test_student_home(self):
        """TC-026: 学生首页"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/student/')
        self.assertEqual(resp.status_code, 200)

    def test_student_packages(self):
        """TC-027: 包裹列表"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/student/packages')
        self.assertEqual(resp.status_code, 200)

    def test_student_packages_filter(self):
        """TC-028: 按状态筛选包裹"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/student/packages?status=pending')
        self.assertEqual(resp.status_code, 200)

    def test_student_package_detail(self):
        """TC-029: 包裹详情"""
        self._login(self.student1_id, 'student')
        resp = self.client.get(f'/student/package/{self.pkg1_id}')
        self.assertEqual(resp.status_code, 200)

    def test_student_pickup_code(self):
        """TC-030: 查看取件码"""
        self._login(self.student1_id, 'student')
        resp = self.client.get(f'/student/pickup/{self.pkg1_id}')
        self.assertEqual(resp.status_code, 200)

    def test_student_send_page(self):
        """TC-031: 寄件页面"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/student/send')
        self.assertEqual(resp.status_code, 200)

    def test_student_send_submit(self):
        """TC-031: 寄件预约成功"""
        self._login(self.student1_id, 'student')
        with self.app.app_context():
            before_count = SendOrder.query.filter_by(sender_id=self.student1_id).count()

        resp = self.client.post('/student/send', data={
            'receiver_name': '测试收件人',
            'receiver_phone': '13800001234',
            'receiver_addr': '测试地址',
            'company_id': self.company_id,
            'item_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            after_count = SendOrder.query.filter_by(sender_id=self.student1_id).count()
            self.assertEqual(after_count, before_count + 1)
            # 验证新订单内容
            order = SendOrder.query.filter_by(sender_id=self.student1_id, receiver_name='测试收件人').first()
            self.assertIsNotNone(order)
            self.assertEqual(order.status, 'pending')

    def test_student_send_empty_receiver_name(self):
        """TC-032: 寄件缺少收件人姓名"""
        self._login(self.student1_id, 'student')
        resp = self.client.post('/student/send', data={
            'receiver_name': '',
            'receiver_phone': '13800001234',
            'receiver_addr': '测试地址',
            'company_id': self.company_id,
            'item_type': 'normal'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_student_send_list(self):
        """TC-033: 寄件记录"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/student/send/list')
        self.assertEqual(resp.status_code, 200)

    def test_student_authorization(self):
        """TC-034: 授权代取"""
        self._login(self.student1_id, 'student')
        resp = self.client.post('/student/authorization', data={
            'package_id': self.pkg1_id,
            'authorizee_username': '2021002002'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_student_authorization_invalid_authorizee(self):
        """TC-035: 被授权人不存在"""
        self._login(self.student1_id, 'student')
        resp = self.client.post('/student/authorization', data={
            'package_id': self.pkg1_id,
            'authorizee_username': 'NOTEXIST'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_student_revoke_auth(self):
        """撤销授权"""
        self._login(self.student1_id, 'student')
        resp = self.client.get(f'/student/authorization/revoke/{self.auth_id}', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            auth = Authorization.query.get(self.auth_id)
            self.assertEqual(auth.status, 'revoked')

    def test_student_notifications(self):
        """TC-051: 通知列表"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/student/notifications')
        self.assertEqual(resp.status_code, 200)

    def test_student_read_notification(self):
        """TC-052: 标记通知已读"""
        self._login(self.student1_id, 'student')
        resp = self.client.get(f'/student/notifications/read/{self.notif_id}')
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            notif = Notification.query.get(self.notif_id)
            self.assertTrue(notif.is_read)

    def test_student_unauthorized_access(self):
        """TC-059: 未登录不能访问学生页面"""
        resp = self.client.get('/student/')
        self.assertEqual(resp.status_code, 302)


# ==================== 管理员端测试 ====================
class TestAdmin(BaseTestCase):
    def test_admin_overview(self):
        """TC-036: 数据概览"""
        self._login(self.admin_id, 'admin')
        resp = self.client.get('/admin/overview')
        self.assertEqual(resp.status_code, 200)

    def test_admin_users_list(self):
        """TC-039: 用户列表"""
        self._login(self.admin_id, 'admin')
        resp = self.client.get('/admin/users')
        self.assertEqual(resp.status_code, 200)

    def test_admin_users_search(self):
        """TC-040: 搜索用户"""
        self._login(self.admin_id, 'admin')
        resp = self.client.get('/admin/users?search=张')
        self.assertEqual(resp.status_code, 200)

    def test_admin_add_user(self):
        """TC-041: 添加用户"""
        self._login(self.admin_id, 'admin')
        resp = self.client.post('/admin/users', data={
            'action': 'add',
            'username': 'newstudent',
            'name': '新同学',
            'role': 'student',
            'phone': '13800001111',
            'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(username='newstudent').first()
            self.assertIsNotNone(user)

    def test_admin_toggle_user(self):
        """TC-042: 禁用/启用用户"""
        self._login(self.admin_id, 'admin')
        resp = self.client.post('/admin/users', data={
            'action': 'toggle',
            'user_id': self.student1_id
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            user = User.query.get(self.student1_id)
            self.assertEqual(user.status, 'disabled')

    def test_admin_announcements(self):
        """TC-043: 公告列表"""
        self._login(self.admin_id, 'admin')
        resp = self.client.get('/admin/announcements')
        self.assertEqual(resp.status_code, 200)

    def test_admin_add_announcement(self):
        """TC-043: 发布公告"""
        self._login(self.admin_id, 'admin')
        resp = self.client.post('/admin/announcements', data={
            'action': 'add',
            'title': '新公告',
            'content': '公告内容'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_admin_withdraw_announcement(self):
        """TC-044: 撤回公告"""
        self._login(self.admin_id, 'admin')
        resp = self.client.post('/admin/announcements', data={
            'action': 'withdraw',
            'ann_id': self.ann_id
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            ann = Announcement.query.get(self.ann_id)
            self.assertEqual(ann.status, 'withdrawn')

    def test_admin_stats(self):
        """TC-045: 快递统计"""
        self._login(self.admin_id, 'admin')
        resp = self.client.get('/admin/stats?start_date=2026-06-01&end_date=2026-06-30')
        self.assertEqual(resp.status_code, 200)


# ==================== 货架管理测试 ====================
class TestShelf(BaseTestCase):
    def test_shelf_list(self):
        """TC-046: 货架列表"""
        self._login(self.staff_id, 'staff')
        resp = self.client.get('/staff/shelf')
        self.assertEqual(resp.status_code, 200)

    def test_shelf_unauthorized(self):
        """TC-050: 未登录不能访问货架"""
        resp = self.client.get('/staff/shelf')
        self.assertEqual(resp.status_code, 302)


# ==================== 权限测试 ====================
class TestPermissions(BaseTestCase):
    def test_student_cannot_access_staff(self):
        """TC-056: 学生不能访问员工页面"""
        self._login(self.student1_id, 'student')
        resp = self.client.get('/staff/dashboard', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_staff_cannot_access_admin(self):
        """TC-057: 员工不能访问管理员页面"""
        self._login(self.staff_id, 'staff')
        resp = self.client.get('/admin/overview', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_unauthorized_all_pages(self):
        """TC-059: 未登录不能访问任何页面"""
        pages = ['/student/', '/staff/dashboard', '/admin/overview']
        for page in pages:
            resp = self.client.get(page)
            self.assertEqual(resp.status_code, 302)


# ==================== 通知模块测试 ====================
class TestNotification(BaseTestCase):
    def test_send_reminder(self):
        """TC-053: 员工发送取件提醒"""
        self._login(self.staff_id, 'staff')
        resp = self.client.get(f'/staff/send_reminder/{self.pkg1_id}', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            notif = Notification.query.filter_by(user_id=self.student1_id, type='overtime').first()
            self.assertIsNotNone(notif)


if __name__ == '__main__':
    unittest.main()

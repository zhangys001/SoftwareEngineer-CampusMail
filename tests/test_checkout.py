# -*- coding: utf-8 -*-
"""出库功能系统测试 - 针对已知bug的测试用例"""
import os
import unittest
import tempfile
from datetime import datetime
from app import create_app
from app.models import db, Package, PickupRecord, Shelf, User, ExpressCompany


class CheckoutTestCase(unittest.TestCase):
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
        # 创建用户
        staff = User(username='STAFF001', name='测试员工', role='staff', phone='13700004444')
        staff.set_password('123456')
        db.session.add(staff)

        student = User(username='2021002002', name='测试学生', role='student', phone='13900002222')
        student.set_password('123456')
        db.session.add(student)
        db.session.flush()

        # 创建快递公司
        company = ExpressCompany(company_name='圆通速递')
        db.session.add(company)
        db.session.flush()

        # 创建货架
        shelf = Shelf(shelf_code='B-1', total_slots=20, used_slots=1)
        db.session.add(shelf)
        db.session.flush()

        # 创建待出库包裹
        pkg = Package(
            tracking_no='TEST20260612001',
            company_id=company.company_id,
            receiver_id=student.user_id,
            shelf_id=shelf.shelf_id,
            slot_code='B-1-01',
            pickup_code='B-1-01',
            package_type='normal',
            status='pending',
            operator_id=staff.user_id
        )
        db.session.add(pkg)
        db.session.commit()

        self.staff_id = staff.user_id
        self.student_id = student.user_id
        self.package_id = pkg.package_id

    def _login_staff(self):
        """模拟员工登录"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.staff_id
            sess['role'] = 'staff'
            sess['name'] = '测试员工'

    # ========== 测试用例 ==========

    def test_checkout_by_pickup_code(self):
        """TC-001: 使用取件码正常出库"""
        self._login_staff()
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.package_id)
            self.assertEqual(pkg.status, 'picked')
            self.assertIsNotNone(pkg.picked_at)

    def test_checkout_by_tracking_no(self):
        """TC-002: 使用快递单号出库（修复后的功能）"""
        self._login_staff()
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'TEST20260612001'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.package_id)
            self.assertEqual(pkg.status, 'picked')

    def test_checkout_empty_code(self):
        """TC-003: 空取件码应报错"""
        self._login_staff()
        resp = self.client.post('/staff/checkout', data={'pickup_code': ''}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.package_id)
            self.assertEqual(pkg.status, 'pending')  # 不应改变状态

    def test_checkout_nonexistent_code(self):
        """TC-004: 不存在的取件码应报错"""
        self._login_staff()
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'NONEXISTENT'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.package_id)
            self.assertEqual(pkg.status, 'pending')  # 不应改变状态

    def test_checkout_already_picked(self):
        """TC-005: 已出库包裹不能重复出库"""
        self._login_staff()
        # 先出库
        self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        # 再次尝试出库
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_checkout_shelf_count_decrease(self):
        """TC-006: 出库后货架已用位应减少"""
        self._login_staff()
        with self.app.app_context():
            shelf = Shelf.query.filter_by(shelf_code='B-1').first()
            initial_used = shelf.used_slots

        self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)

        with self.app.app_context():
            shelf = Shelf.query.filter_by(shelf_code='B-1').first()
            self.assertEqual(shelf.used_slots, initial_used - 1)

    def test_checkout_creates_record(self):
        """TC-007: 出库应创建取件记录"""
        self._login_staff()
        self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        with self.app.app_context():
            record = PickupRecord.query.filter_by(package_id=self.package_id).first()
            self.assertIsNotNone(record)
            self.assertEqual(record.pickup_type, 'self')

    def test_unauthorized_checkout(self):
        """TC-008: 未登录不能出库"""
        resp = self.client.post('/staff/checkout', data={'pickup_code': 'B-1-01'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            pkg = Package.query.get(self.package_id)
            self.assertEqual(pkg.status, 'pending')


if __name__ == '__main__':
    unittest.main()

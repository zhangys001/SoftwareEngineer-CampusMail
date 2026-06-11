# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime, timedelta
from app import create_app
from app.models import db
from app.models.user import User
from app.models.express_company import ExpressCompany
from app.models.shelf import Shelf
from app.models.package import Package
from app.models.pickup_record import PickupRecord
from app.models.send_order import SendOrder
from app.models.announcement import Announcement
from app.models.notification import Notification

app = create_app()


def init_db():
    """Initialize database and seed rich sample data."""
    with app.app_context():
        db.create_all()

        if User.query.first():
            print('Database already has data. Skipping seed.')
            return

        # ── Users ──
        users_data = [
            ('student', '张同学', 'student', '13800001111', '123456'),
            ('2021002002', '李同学', 'student', '13900002222', '123456'),
            ('2021003005', '王同学', 'student', '13600003333', '123456'),
            ('2021004012', '赵同学', 'student', '13500006666', '123456'),
            ('2021005018', '陈同学', 'student', '13400007777', '123456'),
            ('STAFF001', '王员工', 'staff', '13700004444', '123456'),
            ('STAFF002', '李员工', 'staff', '13500005555', '123456'),
            ('admin', '系统管理员', 'admin', '13300000000', '123456'),
        ]
        users = []
        for uname, name, role, phone, pwd in users_data:
            u = User(username=uname, name=name, role=role, phone=phone)
            u.set_password(pwd)
            db.session.add(u)
            users.append(u)
        db.session.flush()

        student_ids = [u.user_id for u in users if u.role == 'student']
        staff_id = [u.user_id for u in users if u.role == 'staff'][0]

        # ── Express Companies ──
        companies_data = ['圆通速递', '中通快递', '韵达快递', '申通快递', '顺丰速运', '京东物流', '极兔速递', '邮政EMS']
        companies = []
        for cname in companies_data:
            c = ExpressCompany(company_name=cname)
            db.session.add(c)
            companies.append(c)
        db.session.flush()

        # ── Shelves ──
        shelves = []
        for letter in ['A', 'B', 'C']:
            for num in range(1, 4):
                s = Shelf(shelf_code=f'{letter}-{num}', total_slots=20, used_slots=0)
                db.session.add(s)
                shelves.append(s)
        db.session.flush()

        # ── Packages (mix of pending and picked) ──
        now = datetime.now()
        packages_data = [
            # (tracking_no, company_idx, receiver_idx, shelf_idx, slot, pickup_code, type, status, hours_ago)
            ('YT20260610001', 0, 0, 0, 'A-1-01', 'A-1-01', 'normal', 'picked', 48),
            ('YT20260610002', 0, 1, 0, 'A-1-02', 'A-1-02', 'document', 'picked', 46),
            ('ZT20260610003', 1, 0, 1, 'A-2-01', 'A-2-01', 'normal', 'picked', 44),
            ('YD20260610004', 2, 2, 1, 'A-2-02', 'A-2-02', 'large', 'picked', 42),
            ('ST20260610005', 3, 3, 2, 'A-3-01', 'A-3-01', 'fragile', 'picked', 40),
            ('SF20260610006', 4, 4, 2, 'A-3-02', 'A-3-02', 'normal', 'picked', 38),
            ('JD20260610007', 5, 0, 0, 'A-1-03', 'A-1-03', 'normal', 'picked', 36),
            ('YT20260610008', 0, 1, 0, 'A-1-04', 'A-1-04', 'books', 'picked', 34),
            ('ZT20260610009', 1, 2, 1, 'A-2-03', 'A-2-03', 'normal', 'picked', 32),
            ('JT20260610010', 6, 3, 1, 'A-2-04', 'A-2-04', 'normal', 'picked', 30),
            # Pending packages (still in shelf)
            ('YT20260611001', 0, 0, 0, 'B-1-01', 'B-1-01', 'normal', 'pending', 6),
            ('ZT20260611002', 1, 0, 0, 'B-1-02', 'B-1-02', 'document', 'pending', 5),
            ('YD20260611003', 2, 1, 1, 'B-2-01', 'B-2-01', 'normal', 'pending', 4),
            ('SF20260611004', 4, 1, 1, 'B-2-02', 'B-2-02', 'electronics', 'pending', 3),
            ('JD20260611005', 5, 2, 2, 'B-3-01', 'B-3-01', 'normal', 'pending', 2),
            ('YT20260611006', 0, 3, 2, 'B-3-02', 'B-3-02', 'clothing', 'pending', 1),
            ('ZT20260611007', 1, 4, 0, 'C-1-01', 'C-1-01', 'normal', 'pending', 1),
            ('EMS20260611008', 7, 0, 0, 'C-1-02', 'C-1-02', 'document', 'pending', 0.5),
        ]

        packages = []
        for (t_no, co_i, re_i, sh_i, slot, p_code, p_type, status, hrs) in packages_data:
            arrived = now - timedelta(hours=hrs)
            picked = arrived + timedelta(hours=random.randint(1, 3)) if status == 'picked' else None
            pkg = Package(
                tracking_no=t_no,
                company_id=companies[co_i].company_id,
                receiver_id=student_ids[re_i],
                shelf_id=shelves[sh_i].shelf_id,
                slot_code=slot,
                pickup_code=p_code,
                package_type=p_type,
                status=status,
                arrived_at=arrived,
                picked_at=picked,
                operator_id=staff_id,
            )
            db.session.add(pkg)
            packages.append(pkg)
        db.session.flush()

        # Update shelf used_slots based on pending packages
        shelf_usage = {}
        for pkg in packages:
            if pkg.status == 'pending' and pkg.shelf_id:
                shelf_usage[pkg.shelf_id] = shelf_usage.get(pkg.shelf_id, 0) + 1
        for s in shelves:
            s.used_slots = shelf_usage.get(s.shelf_id, 0)
            if s.usage_rate >= 90:
                s.status = 'almost_full'

        # ── Pickup Records (for picked packages) ──
        for pkg in packages:
            if pkg.status == 'picked':
                record = PickupRecord(
                    package_id=pkg.package_id,
                    picker_id=pkg.receiver_id,
                    pickup_type='self',
                    operator_id=staff_id,
                    picked_at=pkg.picked_at,
                )
                db.session.add(record)

        # ── Send Orders ──
        orders_data = [
            (0, '张同学', '13800001111', '李老师', '13912345678', '北京市海淀区清华大学', 0, 'document', 'completed'),
            (0, '张同学', '13800001111', '妈妈', '13800009999', '上海市浦东新区陆家嘴', 4, 'clothing', 'pending'),
            (1, '李同学', '13900002222', '女朋友', '13700008888', '杭州市西湖区浙江大学', 1, 'books', 'pending'),
            (3, '赵同学', '13500006666', '爸爸', '13600007777', '广州市天河区珠江新城', 5, 'electronics', 'processing'),
        ]
        for (si, sn, sp, rn, ra, addr, ci, it, st) in orders_data:
            order = SendOrder(
                sender_id=student_ids[si],
                sender_name=sn,
                sender_phone=sp,
                receiver_name=rn,
                receiver_phone=ra,
                receiver_addr=addr,
                company_id=companies[ci].company_id,
                item_type=it,
                status=st,
                created_at=now - timedelta(hours=random.randint(1, 72)),
            )
            db.session.add(order)

        # ── Announcements ──
        anns_data = [
            ('双十一期间快递取件提醒', '双十一期间快递量较大，请收到通知后24小时内取件，超时将退回快递柜。', 'published'),
            ('驿站五一假期运营时间调整', '五一假期期间驿站运营时间调整为 9:00-18:00，假期结束后恢复正常。', 'published'),
            ('关于规范大件包裹存放的通知', '大件包裹请存放至指定区域，不要占用普通货架位置。', 'withdrawn'),
        ]
        for title, content, status in anns_data:
            ann = Announcement(
                title=title,
                content=content,
                publisher_id=[u.user_id for u in users if u.role == 'admin'][0],
                status=status,
                published_at=now - timedelta(days=random.randint(1, 7)),
            )
            db.session.add(ann)

        # ── Notifications ──
        notifs_data = [
            (0, '您的快递 A-1-01 已到达驿站，请尽快取件', 'pickup'),
            (0, '您的快递 B-1-01 已到达驿站，取件码: B-1-01', 'pickup'),
            (1, '您的快递 B-2-01 已到达驿站，取件码: B-2-01', 'pickup'),
            (0, '您的快递 A-1-03 已滞留3天，请尽快取件', 'overtime'),
            (2, '系统维护通知：今晚22:00-23:00将进行系统维护', 'system'),
        ]
        for uid, content, ntype in notifs_data:
            notif = Notification(
                user_id=student_ids[uid],
                content=content,
                type=ntype,
                is_read=random.choice([True, False]),
                created_at=now - timedelta(hours=random.randint(1, 48)),
            )
            db.session.add(notif)

        db.session.commit()
        print('Database seeded with rich sample data!')
        print(f'  - {len(users)} users')
        print(f'  - {len(companies)} express companies')
        print(f'  - {len(shelves)} shelves')
        print(f'  - {len(packages)} packages ({sum(1 for p in packages if p.status=="pending")} pending, {sum(1 for p in packages if p.status=="picked")} picked)')
        print(f'  - {len(orders_data)} send orders')
        print(f'  - {len(anns_data)} announcements')
        print(f'  - {len(notifs_data)} notifications')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

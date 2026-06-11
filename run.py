# -*- coding: utf-8 -*-
from app import create_app
from app.models import db
from app.models.user import User
from app.models.express_company import ExpressCompany
from app.models.shelf import Shelf

app = create_app()


def init_db():
    """Initialize database and seed sample data."""
    with app.app_context():
        db.create_all()

        if User.query.first():
            return

        # Seed users
        users = [
            ('student', '张同学', 'student', '13800001111', '123456'),
            ('2021002002', '李同学', 'student', '13900002222', '123456'),
            ('2021003005', '王同学', 'student', '13600003333', '123456'),
            ('STAFF001', '王员工', 'staff', '13700004444', '123456'),
            ('STAFF002', '李员工', 'staff', '13500005555', '123456'),
            ('admin', '系统管理员', 'admin', '13300000000', '123456'),
        ]
        for uname, name, role, phone, pwd in users:
            u = User(username=uname, name=name, role=role, phone=phone)
            u.set_password(pwd)
            db.session.add(u)

        # Seed express companies
        companies = ['圆通速递', '中通快递', '韵达快递', '申通快递', '顺丰速运', '京东物流', '极兔速递', '邮政EMS']
        for cname in companies:
            db.session.add(ExpressCompany(company_name=cname))

        # Seed shelves
        for letter in ['A', 'B', 'C']:
            for num in range(1, 4):
                db.session.add(Shelf(shelf_code=f'{letter}-{num}', total_slots=20, used_slots=0))

        db.session.commit()
        print('Database initialized with sample data.')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

# 📦 校园快递收发系统

> 软件工程课程设计（第9组）— 基于 Flask 的校园快递全生命周期管理系统

## 📋 项目简介

本系统为校园驿站提供一站式快递收发管理解决方案，覆盖快递入库、存储、出库、寄件全流程。支持学生、驿站员工、管理员三种角色，实现快递信息的数字化管理。

## 🎯 功能模块

### 学生端（H5 移动端）

| 功能 | 说明 |
|------|------|
| 📦 快递查询 | 通过取件码或快递单号查询包裹状态 |
| 📋 我的快递 | 查看待取件/已取件快递列表 |
| 📱 扫码取件 | 出示取件码供工作人员核销出库 |
| ✉️ 预约寄件 | 在线填写寄件信息并提交预约 |
| 🤝 代取授权 | 生成授权码，授权其他同学代为取件 |
| 🔔 消息通知 | 接收取件提醒、滞留预警等通知 |

### 员工端

| 功能 | 说明 |
|------|------|
| 📊 工作台 | 今日入库/出库统计、滞留件预警 |
| 📥 快递入库 | 扫描单号、分配货架、自动生成取件码 |
| 📤 出库核销 | 支持取件码/快递单号/授权码三种方式出库 |
| 🗄️ 货架管理 | 查看货架状态、库位使用率 |

### 管理员端

| 功能 | 说明 |
|------|------|
| 📈 数据概览 | 运营指标、趋势图、快递公司分布 |
| 👥 用户管理 | 增删改查用户账号、启用/禁用 |
| 📢 公告管理 | 发布/撤回系统公告 |
| 📊 快递统计 | 按日期范围查询并导出报表 |

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3 + Flask + SQLAlchemy |
| 数据库 | SQLite（支持 MySQL 迁移） |
| 前端 | HTML + CSS + Jinja2 模板引擎 |
| 认证 | Flask Session + 密码哈希（scrypt） |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装与运行

```bash
# 1. 克隆项目
git clone https://github.com/zhangys001/SoftwareEngineer-CampusMail.git
cd SoftwareEngineer-CampusMail

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务（自动初始化数据库并填充示例数据）
python run.py
```

访问 http://localhost:5000

### 测试账号

| 角色 | 账号 | 密码 | 说明 |
|------|------|------|------|
| 学生 | student | 123456 | 张同学 |
| 学生 | 2021002002 | 123456 | 李同学 |
| 员工 | STAFF001 | 123456 | 王员工 |
| 员工 | STAFF002 | 123456 | 李员工 |
| 管理员 | admin | 123456 | 系统管理员 |

## 📁 项目结构

```
SoftwareEngineer-CampusMail/
├── run.py                      # 入口文件（含数据库初始化）
├── requirements.txt            # Python 依赖
├── campus_mail.db              # SQLite 数据库（运行后自动生成）
│
├── app/                        # Flask 应用
│   ├── __init__.py             # 应用工厂函数
│   ├── models/                 # 数据模型（9 张表）
│   │   ├── user.py             # 用户表
│   │   ├── package.py          # 包裹表（核心）
│   │   ├── shelf.py            # 货架表
│   │   ├── pickup_record.py    # 取件记录表
│   │   ├── authorization.py    # 代取授权表
│   │   ├── send_order.py       # 寄件订单表
│   │   ├── express_company.py  # 快递公司表
│   │   ├── announcement.py     # 公告表
│   │   └── notification.py     # 通知表
│   ├── routes/                 # 路由控制器
│   │   ├── auth.py             # 登录认证
│   │   ├── student.py          # 学生端 API
│   │   ├── staff.py            # 员工端 API
│   │   └── admin.py            # 管理员端 API
│   └── templates/              # 页面模板
│       ├── auth/               # 登录页
│       ├── student/            # 学生端页面
│       ├── staff/              # 员工端页面
│       └── admin/              # 管理员端页面
│
└── tests/                      # 单元测试
    ├── test_checkout.py        # 出库功能测试（8 个用例）
    └── generate_test_report.py # 测试报告生成脚本
```

## 🗃️ 数据库设计

系统共 9 张数据表：

```
user（用户）──┐
              ├── package（包裹）── pickup_record（取件记录）
express_company（快递公司）──┘         │
              │                       └── authorization（代取授权）
shelf（货架）──┘
              
send_order（寄件订单）
announcement（公告）
notification（通知）
```

## 🧪 测试

```bash
# 运行出库功能单元测试
python -m unittest tests.test_checkout -v

# 生成测试报告 XLS
cd tests
python generate_test_report.py
```

## 🐛 已修复的 BUG

| 编号 | 模块 | 问题 | 严重度 |
|------|------|------|--------|
| BUG-001 | 出库核销 | 仅支持取件码，不支持快递单号 | 高 |
| BUG-002 | 出库核销 | 错误提示信息不准确 | 中 |
| BUG-003 | 出库核销 | 空码提示不友好 | 低 |
| BUG-004 | 入库/寄件/授权 | 表单空值导致 500 错误 | 中 |
| BUG-005 | 出库核销 | 模板标签与功能不一致 | 低 |
| BUG-006 | 代取授权 | 出库不支持授权码代取 | 高 |

## 📄 相关文档

- 测试用例 & BUG 清单：`范例及模版/3.系统测试/测试用例&BUG清单_第9组.xls`
- 功能设计文档：`功能设计/`
- 程序设计图：`程序设计图/`

## 👥 第 9 组成员

- 张煜晟（24050407）
- 其他成员...

## 📝 开发日志

| 日期 | 内容 |
|------|------|
| 2026-06-11 | 完成基础功能开发，提交初版 |
| 2026-06-12 | 修复出库/入库/代取授权等 6 个 BUG |
| 2026-06-12 | 添加单元测试，生成测试报告 |

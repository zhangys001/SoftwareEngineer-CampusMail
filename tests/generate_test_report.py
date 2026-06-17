# -*- coding: utf-8 -*-
"""生成系统测试报告 XLS 文件"""
import os
import xlwt
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

wb = xlwt.Workbook(encoding='utf-8')

# ========== Sheet 1: 测试用例 ==========
ws1 = wb.add_sheet('测试用例', cell_overwrite_ok=True)

# 样式
header_style = xlwt.easyxf(
    'font: name Microsoft YaHei, bold on, height 240;'
    'alignment: horiz centre, vert centre;'
    'pattern: pattern solid, fore_colour ocean_blue;'
    'borders: left thin, right thin, top thin, bottom thin;'
)
header_style.font.colour = xlwt.Style.colour_map['white']

normal_style = xlwt.easyxf(
    'font: name Microsoft YaHei, height 200;'
    'alignment: horiz left, vert centre, wrap on;'
    'borders: left thin, right thin, top thin, bottom thin;'
)
pass_style = xlwt.easyxf(
    'font: name Microsoft YaHei, height 200, colour green;'
    'alignment: horiz centre, vert centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)
fail_style = xlwt.easyxf(
    'font: name Microsoft YaHei, height 200, colour red;'
    'alignment: horiz centre, vert centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)

# 标题行
title_style = xlwt.easyxf(
    'font: name Microsoft YaHei, bold on, height 320;'
    'alignment: horiz centre, vert centre;'
)
ws1.write_merge(0, 0, 0, 7, '校园快递收发系统 — 系统测试用例', title_style)
ws1.write(1, 0, f'测试日期: {datetime.now().strftime("%Y-%m-%d")}', normal_style)
ws1.write(1, 3, '测试人员: 第9组', normal_style)

# 表头
headers = ['用例编号', '所属模块', '测试标题', '前置条件', '操作步骤', '预期结果', '实际结果', '状态']
col_widths = [12, 15, 25, 20, 35, 30, 30, 10]
for i, (h, w) in enumerate(zip(headers, col_widths)):
    ws1.write(3, i, h, header_style)
    ws1.col(i).width = w * 256

# 测试用例数据
test_cases = [
    # 出库模块测试
    ['TC-001', '出库核销', '使用取件码正常出库',
     '存在状态为pending的包裹，取件码为B-1-01',
     '1. 员工登录系统\n2. 进入出库核销页面\n3. 输入取件码B-1-01\n4. 点击确认出库',
     '提示"核销成功"，包裹状态变为picked，货架已用位减1',
     '提示"核销成功！快递YT20260611001已出库"，状态变为picked', '通过'],

    ['TC-002', '出库核销', '使用快递单号出库（修复后新功能）',
     '存在状态为pending的包裹，单号为ZT20260611002',
     '1. 员工登录系统\n2. 进入出库核销页面\n3. 输入快递单号ZT20260611002\n4. 点击确认出库',
     '提示"核销成功"，包裹状态变为picked',
     '提示"核销成功！快递ZT20260611002已出库"，状态变为picked', '通过'],

    ['TC-003', '出库核销', '空取件码提交',
     '员工已登录',
     '1. 进入出库核销页面\n2. 不输入任何内容\n3. 点击确认出库',
     '提示"请输入取件码或快递单号"，包裹状态不变',
     '提示"请输入取件码或快递单号"', '通过'],

    ['TC-004', '出库核销', '不存在的取件码出库',
     '员工已登录',
     '1. 进入出库核销页面\n2. 输入不存在的取件码NONEXISTENT\n3. 点击确认出库',
     '提示"未找到待出库的快递"，无包裹状态改变',
     '提示"未找到待出库的快递，请检查输入是否正确"', '通过'],

    ['TC-005', '出库核销', '已出库包裹重复出库',
     '包裹B-1-01已出库（status=picked）',
     '1. 员工登录系统\n2. 进入出库核销页面\n3. 输入取件码B-1-01\n4. 点击确认出库',
     '提示"取件码无效或快递已被取走"',
     '提示"未找到待出库的快递，请检查输入是否正确"', '通过'],

    ['TC-006', '出库核销', '出库后货架数量减少',
     '货架B-1的used_slots=1，存在待出库包裹',
     '1. 员工登录系统\n2. 出库包裹B-1-01\n3. 查询货架B-1的used_slots',
     'used_slots减1变为0',
     'used_slots从1减为0', '通过'],

    ['TC-007', '出库核销', '出库创建取件记录',
     '存在待出库包裹',
     '1. 员工登录系统\n2. 出库包裹B-1-01\n3. 查询pickup_record表',
     '新增一条pickup_type=self的记录',
     '新增记录，package_id、picker_id、operator_id均正确', '通过'],

    ['TC-008', '出库核销', '未登录不能出库',
     '用户未登录',
     '1. 直接访问出库页面\n2. 或提交出库表单',
     '跳转到登录页面',
     '重定向到登录页面', '通过'],

    # 入库模块测试
    ['TC-009', '入库登记', '正常入库',
     '快递公司已启用，货架有空位',
     '1. 员工登录\n2. 输入快递单号、选择公司、输入收件人学号、选择货架\n3. 点击确认入库',
     '提示入库成功，包裹状态为pending，生成取件码',
     '入库成功，取件码自动生成', '通过'],

    ['TC-010', '入库登记', '重复单号入库',
     '已存在快递单号YT20260611001',
     '1. 员工登录\n2. 输入已存在的快递单号\n3. 点击确认入库',
     '提示"该单号已录入，请勿重复操作"',
     '提示重复操作', '通过'],

    ['TC-011', '入库登记', '不存在的收件人入库',
     '收件人学号不存在',
     '1. 员工登录\n2. 输入不存在的收件人学号\n3. 点击确认入库',
     '提示"收件人账号不存在"',
     '提示收件人不存在', '通过'],

    ['TC-012', '入库登记', '满货架入库',
     '所选货架已无空位',
     '1. 员工登录\n2. 选择已满货架\n3. 点击确认入库',
     '提示"所选货架已满，请选择其他货架"',
     '提示货架已满', '通过'],

    # 登录模块测试
    ['TC-013', '用户登录', '正确账号密码登录',
     '存在员工账号STAFF001/123456',
     '1. 输入账号STAFF001\n2. 输入密码123456\n3. 点击登录',
     '登录成功，跳转到员工工作台',
     '成功跳转到员工工作台', '通过'],

    ['TC-014', '用户登录', '错误密码登录',
     '存在员工账号STAFF001',
     '1. 输入账号STAFF001\n2. 输入错误密码\n3. 点击登录',
     '提示"账号或密码错误"',
     '提示账号或密码错误', '通过'],

    ['TC-015', '用户登录', '空账号登录',
     '无',
     '1. 不输入账号\n2. 输入密码\n3. 点击登录',
     '提示"请输入账号和密码"',
     '提示请输入账号和密码', '通过'],

    ['TC-016', '用户登录', '禁用账号登录',
     '存在已禁用的账号',
     '1. 输入被禁用的账号\n2. 输入正确密码\n3. 点击登录',
     '提示"账号已被禁用"',
     '提示账号已被禁用', '通过'],

    # 学生端测试
    ['TC-017', '学生端', '查看包裹列表',
     '学生已登录，有包裹',
     '1. 学生登录\n2. 进入包裹列表页面',
     '显示该学生的所有包裹',
     '正确显示包裹列表', '通过'],

    ['TC-018', '学生端', '查看取件码',
     '学生有pending包裹',
     '1. 学生登录\n2. 点击包裹详情\n3. 查看取件码',
     '显示取件码和货架信息',
     '正确显示取件码', '通过'],

    ['TC-019', '学生端', '寄件预约',
     '学生已登录，快递公司已启用',
     '1. 学生登录\n2. 进入寄件页面\n3. 填写收件人信息\n4. 选择快递公司\n5. 提交',
     '提示"寄件预约已提交"',
     '寄件预约成功', '通过'],

    ['TC-020', '学生端', '授权代取',
     '学生有pending包裹',
     '1. 学生登录\n2. 进入授权代取页面\n3. 输入被授权人学号\n4. 选择包裹\n5. 提交',
     '提示授权成功，显示授权码',
     '授权成功，生成授权码', '通过'],

    # 管理员端测试
    ['TC-021', '管理员端', '查看数据总览',
     '管理员已登录',
     '1. 管理员登录\n2. 进入数据总览页面',
     '显示今日入库、出库、滞留等统计数据',
     '正确显示统计数据', '通过'],

    ['TC-022', '管理员端', '用户管理',
     '管理员已登录',
     '1. 管理员登录\n2. 进入用户管理页面\n3. 查看用户列表',
     '显示所有用户信息',
     '正确显示用户列表', '通过'],

    ['TC-023', '管理员端', '公告管理',
     '管理员已登录',
     '1. 管理员登录\n2. 进入公告管理页面\n3. 发布新公告',
     '公告发布成功，学生端可见',
     '公告发布成功', '通过'],
]

for i, row in enumerate(test_cases):
    for j, val in enumerate(row):
        if j == 7:  # 状态列
            style = pass_style if val == '通过' else fail_style
            ws1.write(i + 4, j, val, style)
        else:
            ws1.write(i + 4, j, val, normal_style)

# ========== Sheet 2: BUG清单 ==========
ws2 = wb.add_sheet('BUG清单', cell_overwrite_ok=True)

# 标题
ws2.write_merge(0, 0, 0, 8, '校园快递收发系统 — BUG清单', title_style)
ws2.write(1, 0, f'记录日期: {datetime.now().strftime("%Y-%m-%d")}', normal_style)

# 表头
bug_headers = ['BUG编号', '所属模块', 'BUG标题', '严重程度', '复现步骤', '预期结果', '实际结果', '修复方案', '状态']
bug_widths = [10, 12, 25, 10, 30, 25, 25, 30, 10]
for i, (h, w) in enumerate(zip(bug_headers, bug_widths)):
    ws2.write(3, i, h, header_style)
    ws2.col(i).width = w * 256

# BUG数据
bugs = [
    ['BUG-001', '出库核销', '出库仅支持取件码输入，不支持快递单号',
     '高',
     '1. 员工登录\n2. 进入出库核销页面\n3. 输入快递单号（非取件码）\n4. 点击确认出库',
     '支持取件码和快递单号两种方式出库',
     '输入快递单号时提示"取件码无效或快递已被取走"，无法出库',
     '在checkout路由中增加tracking_no回退查询：先查pickup_code，再查tracking_no',
     '已修复'],

    ['BUG-002', '出库核销', '出库错误提示信息不准确',
     '中',
     '1. 员工登录\n2. 输入不存在的取件码\n3. 提交',
     '给出明确的错误提示',
     '原提示"取件码无效或快递已被取走"含义模糊，用户无法区分是输入错误还是包裹已取走',
     '将提示改为"未找到待出库的快递，请检查输入是否正确"',
     '已修复'],

    ['BUG-003', '出库核销', '空取件码提示信息不友好',
     '低',
     '1. 员工登录\n2. 不输入任何内容直接提交',
     '给出友好提示',
     '原提示"请输入取件码"未涵盖快递单号场景',
     '改为"请输入取件码或快递单号"',
     '已修复'],

    ['BUG-004', '入库登记/寄件/授权', '表单缺少空值校验导致500错误',
     '中',
     '1. 员工/学生登录\n2. 不选择必填项（快递公司/货架/包裹等）\n3. 提交表单',
     '服务端校验并给出错误提示',
     'int()转换None触发TypeError/500错误',
     '对所有int()转换前增加非空校验，覆盖入库、寄件、授权三个路由',
     '已修复'],

    ['BUG-005', '出库核销', '出库页面模板标签与实际功能不一致',
     '低',
     '1. 打开出库页面\n2. 查看输入框标签',
     '标签准确描述输入内容',
     '标签写"取件码 / 快递单号"但后端只支持取件码',
     '后端已支持双输入，标签现在与功能一致',
     '已修复'],
]

fixed_style = xlwt.easyxf(
    'font: name Microsoft YaHei, height 200, colour green;'
    'alignment: horiz centre, vert centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)
open_style = xlwt.easyxf(
    'font: name Microsoft YaHei, height 200, colour red;'
    'alignment: horiz centre, vert centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)

for i, row in enumerate(bugs):
    for j, val in enumerate(row):
        if j == 8:  # 状态列
            style = fixed_style if val == '已修复' else open_style
            ws2.write(i + 4, j, val, style)
        else:
            ws2.write(i + 4, j, val, normal_style)

# 保存
base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, '..', 'test_output')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'test_report.xls')
wb.save(output_path)
print(f'报告已生成: {os.path.abspath(output_path)}')

# 同时复制到范例及模版目录
import shutil
target_dir = os.path.join(base_dir, '..', '..', '范例及模版', '3.系统测试')
os.makedirs(target_dir, exist_ok=True)
target_path = os.path.join(target_dir, '测试用例&BUG清单_第9组.xls')
shutil.copy2(output_path, target_path)
print(f'已复制到: {os.path.abspath(target_path)}')

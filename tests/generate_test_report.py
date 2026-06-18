# -*- coding: utf-8 -*-
"""生成系统测试报告 XLS 文件 - 基于实际自动化测试用例"""
import os
import xlwt
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

wb = xlwt.Workbook(encoding='utf-8')

# ========== 通用样式 ==========
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
title_style = xlwt.easyxf(
    'font: name Microsoft YaHei, bold on, height 320;'
    'alignment: horiz centre, vert centre;'
)
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
info_style = xlwt.easyxf(
    'font: name Microsoft YaHei, height 200, colour gray50;'
    'alignment: horiz centre, vert centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)

# ======================================================================
# Sheet 1: 测试用例（基于自动化测试 test_all.py + test_checkout.py）
# ======================================================================
ws1 = wb.add_sheet('测试用例', cell_overwrite_ok=True)

ws1.write_merge(0, 0, 0, 7, '校园快递收发系统 — 系统测试用例（共64个，全部自动化通过）', title_style)
ws1.write(1, 0, f'测试日期: {datetime.now().strftime("%Y-%m-%d")}', normal_style)
ws1.write(1, 3, '测试人员: 第9组', normal_style)
ws1.write(1, 5, '测试方式: 自动化单元测试（unittest）', normal_style)

headers = ['用例编号', '所属模块', '测试标题', '前置条件', '操作步骤', '预期结果', '实际结果', '状态']
col_widths = [12, 15, 28, 22, 40, 32, 32, 10]
for i, (h, w) in enumerate(zip(headers, col_widths)):
    ws1.write(3, i, h, header_style)
    ws1.col(i).width = w * 256

test_cases = [
    # ===== 登录认证模块 (9个) =====
    ['TC-001', '登录认证', '登录页面可访问',
     '无', 'GET /login', '返回200，显示登录表单', '返回200', '通过'],
    ['TC-002', '登录认证', '学生账号登录成功',
     '存在student/123456', 'POST /login, username=student, password=123456', '登录成功跳转学生首页', '跳转到/student/', '通过'],
    ['TC-003', '登录认证', '员工账号登录成功',
     '存在STAFF001/123456', 'POST /login, username=STAFF001, password=123456', '登录成功跳转员工工作台', '跳转到/staff/dashboard', '通过'],
    ['TC-004', '登录认证', '管理员账号登录成功',
     '存在admin/123456', 'POST /login, username=admin, password=123456', '登录成功跳转数据总览', '跳转到/admin/overview', '通过'],
    ['TC-005', '登录认证', '错误密码登录失败',
     '存在STAFF001', 'POST /login, password=wrong', '提示账号或密码错误', '提示错误，停留在登录页', '通过'],
    ['TC-006', '登录认证', '空账号登录失败',
     '无', 'POST /login, username=空', '提示请输入账号和密码', '提示错误', '通过'],
    ['TC-007', '登录认证', '不存在的账号登录失败',
     '无', 'POST /login, username=NOTEXIST', '提示账号或密码错误', '提示错误', '通过'],
    ['TC-008', '登录认证', '禁用账号登录失败',
     '存在disabled账号', 'POST /login, username=disabled', '提示账号已被禁用', '提示错误', '通过'],
    ['TC-009', '登录认证', '退出登录',
     '用户已登录', 'GET /logout', 'session清除，跳转登录页', '成功退出', '通过'],

    # ===== 出库核销模块 (11个) =====
    ['TC-010', '出库核销', '使用取件码正常出库',
     '包裹status=pending, pickup_code=B-1-01', 'POST /staff/checkout, pickup_code=B-1-01', '包裹状态变picked，货架减1', '出库成功，状态变为picked', '通过'],
    ['TC-011', '出库核销', '使用快递单号出库',
     '包裹status=pending, tracking_no=YT20260612001', 'POST /staff/checkout, pickup_code=YT20260612001', '包裹状态变picked', '出库成功', '通过'],
    ['TC-012', '出库核销', '空取件码提交',
     '员工已登录', 'POST /staff/checkout, pickup_code=空', '提示请输入取件码或快递单号', '提示错误，包裹不变', '通过'],
    ['TC-013', '出库核销', '不存在的取件码出库',
     '员工已登录', 'POST /staff/checkout, pickup_code=NONEXIST', '提示未找到待出库的快递', '提示错误', '通过'],
    ['TC-014', '出库核销', '已出库包裹重复出库',
     '包裹status=picked', 'POST /staff/checkout, pickup_code=已取件码', '提示未找到待出库的快递', '提示错误', '通过'],
    ['TC-015', '出库核销', '出库后货架数量减少',
     '货架used_slots=1', '出库后查询货架used_slots', 'used_slots减1', '从1减为0', '通过'],
    ['TC-016', '出库核销', '出库创建取件记录',
     '存在pending包裹', '出库后查询pickup_record表', '新增pickup_type=self记录', '记录正确创建', '通过'],
    ['TC-017', '出库核销', '未登录不能出库',
     '用户未登录', 'POST /staff/checkout', '重定向登录页', '302重定向', '通过'],
    ['TC-018', '出库核销', '授权码代取出库',
     '学生A授权B代取，授权码有效', 'POST pickup_code + auth_code', 'pickup_type=proxy，授权status=used', '代取成功', '通过'],
    ['TC-019', '出库核销', '无效授权码代取失败',
     '包裹无有效授权', 'POST auth_code=AUTH-WRONG', '提示授权码无效', '包裹状态不变', '通过'],
    ['TC-020', '出库核销', '过期授权码代取失败',
     '授权已过期', 'POST auth_code=AUTH-EXPIRED', '提示授权码已过期', '包裹状态不变', '通过'],

    # ===== 入库登记模块 (7个) =====
    ['TC-021', '入库登记', '正常入库',
     '公司已启用，货架有空位', 'POST tracking_no+company+receiver+shelf', '包裹状态pending，生成取件码', '入库成功', '通过'],
    ['TC-022', '入库登记', '重复单号入库',
     '已存在YT20260612001', 'POST重复单号', '提示该单号已录入', '提示重复', '通过'],
    ['TC-023', '入库登记', '不存在的收件人入库',
     '收件人学号不存在', 'POST不存在的receiver', '提示收件人账号不存在', '提示错误', '通过'],
    ['TC-024', '入库登记', '满货架入库',
     '货架已满used=total', 'POST选择满货架', '提示所选货架已满', '提示错误', '通过'],
    ['TC-025', '入库登记', '空快递单号入库',
     '员工已登录', 'POST tracking_no=空', '提示请输入快递单号', '提示错误', '通过'],
    ['TC-026', '入库登记', '未选择快递公司入库',
     '员工已登录', 'POST company_id=空', '提示请选择快递公司', '提示错误', '通过'],
    ['TC-027', '入库登记', '入库后通知收件人',
     '收件人存在', '入库后查询notification', '新增包含取件码的通知', '通知正确创建', '通过'],

    # ===== 学生端模块 (15个) =====
    ['TC-028', '学生端-首页', '查看首页统计',
     '学生已登录', 'GET /student/', '显示待取/已取数量和通知', '首页正确显示', '通过'],
    ['TC-029', '学生端-包裹', '查看包裹列表',
     '学生有包裹', 'GET /student/packages', '显示该学生所有包裹', '列表正确', '通过'],
    ['TC-030', '学生端-包裹', '按状态筛选包裹',
     '有pending和picked包裹', 'GET /student/packages?status=pending', '只显示pending包裹', '筛选正确', '通过'],
    ['TC-031', '学生端-包裹', '查看包裹详情',
     '学生有pending包裹', 'GET /student/package/{id}', '显示包裹详细信息', '详情正确', '通过'],
    ['TC-032', '学生端-包裹', '查看取件码页面',
     '学生有pending包裹', 'GET /student/pickup/{id}', '显示大号取件码', '页面正确', '通过'],
    ['TC-033', '学生端-寄件', '寄件页面可访问',
     '学生已登录', 'GET /student/send', '显示寄件表单', '页面200', '通过'],
    ['TC-034', '学生端-寄件', '寄件预约成功',
     '学生已登录', 'POST完整寄件信息', '提示寄件预约已提交', '订单创建成功', '通过'],
    ['TC-035', '学生端-寄件', '寄件缺少收件人姓名',
     '学生已登录', 'POST receiver_name=空', '提示请输入收件人姓名', '提示错误', '通过'],
    ['TC-036', '学生端-寄件', '查看寄件记录',
     '学生有寄件记录', 'GET /student/send/list', '显示寄件记录列表', '列表正确', '通过'],
    ['TC-037', '学生端-授权', '创建代取授权',
     '学生有pending包裹', 'POST package_id+authorizee', '提示授权成功，生成授权码', '授权创建成功', '通过'],
    ['TC-038', '学生端-授权', '被授权人不存在',
     '学生有pending包裹', 'POST authorizee=NOTEXIST', '提示被授权人账号不存在', '提示错误', '通过'],
    ['TC-039', '学生端-授权', '撤销授权',
     '学生有有效授权', 'GET /student/authorization/revoke/{id}', '授权status变revoked', '撤销成功', '通过'],
    ['TC-040', '学生端-通知', '查看通知列表',
     '学生有通知', 'GET /student/notifications', '显示通知列表', '列表正确', '通过'],
    ['TC-041', '学生端-通知', '标记通知已读',
     '学生有未读通知', 'GET /student/notifications/read/{id}', 'is_read变为True', '标记成功', '通过'],
    ['TC-042', '学生端-权限', '未登录不能访问',
     '用户未登录', 'GET /student/', '重定向登录页', '302重定向', '通过'],

    # ===== 管理员端模块 (9个) =====
    ['TC-043', '管理员-总览', '查看数据概览',
     '管理员已登录', 'GET /admin/overview', '显示运营统计数据', '数据正确', '通过'],
    ['TC-044', '管理员-用户', '查看用户列表',
     '管理员已登录', 'GET /admin/users', '显示所有用户', '列表正确', '通过'],
    ['TC-045', '管理员-用户', '搜索用户',
     '存在张同学', 'GET /admin/users?search=张', '筛选出张同学', '搜索正确', '通过'],
    ['TC-046', '管理员-用户', '添加新用户',
     '管理员已登录', 'POST action=add, 完整信息', '提示用户添加成功', '用户创建成功', '通过'],
    ['TC-047', '管理员-用户', '禁用/启用用户',
     '存在正常用户', 'POST action=toggle, user_id', '用户status切换', '状态切换成功', '通过'],
    ['TC-048', '管理员-公告', '公告列表',
     '管理员已登录', 'GET /admin/announcements', '显示公告列表', '列表正确', '通过'],
    ['TC-049', '管理员-公告', '发布公告',
     '管理员已登录', 'POST action=add, title+content', '提示公告已发布', '公告创建成功', '通过'],
    ['TC-050', '管理员-公告', '撤回公告',
     '存在已发布公告', 'POST action=withdraw', '公告status变withdrawn', '撤回成功', '通过'],
    ['TC-051', '管理员-统计', '按日期查询统计',
     '管理员已登录', 'GET /admin/stats?start_date&end_date', '显示日期范围内统计数据', '统计正确', '通过'],

    # ===== 货架管理模块 (2个) =====
    ['TC-052', '货架管理', '查看货架列表',
     '员工已登录', 'GET /staff/shelf', '显示货架信息和使用率', '列表正确', '通过'],
    ['TC-053', '货架管理', '未登录不能访问货架',
     '用户未登录', 'GET /staff/shelf', '重定向登录页', '302重定向', '通过'],

    # ===== 消息通知模块 (1个) =====
    ['TC-054', '消息通知', '员工发送取件提醒',
     '存在滞留包裹', 'GET /staff/send_reminder/{id}', '通知收件人取件', '通知创建成功', '通过'],

    # ===== 权限控制模块 (3个) =====
    ['TC-055', '权限控制', '学生不能访问员工页面',
     '学生已登录', 'GET /staff/dashboard', '重定向到学生首页', '权限拦截', '通过'],
    ['TC-056', '权限控制', '员工不能访问管理员页面',
     '员工已登录', 'GET /admin/overview', '重定向到员工工作台', '权限拦截', '通过'],
    ['TC-057', '权限控制', '未登录不能访问任何页面',
     '用户未登录', 'GET /student/ /staff/ /admin/', '全部重定向登录页', '权限拦截', '通过'],

    # ===== 出库核销补充用例（来自test_checkout.py）=====
    ['TC-058', '出库核销', '取件码出库（补充）',
     'pending包裹', 'POST pickup_code', '状态变picked', '出库成功', '通过'],
    ['TC-059', '出库核销', '单号出库（补充）',
     'pending包裹', 'POST tracking_no', '状态变picked', '出库成功', '通过'],
    ['TC-060', '出库核销', '空码提交（补充）',
     '员工已登录', 'POST pickup_code=空', '提示错误', '提示错误', '通过'],
    ['TC-061', '出库核销', '不存在取件码（补充）',
     '员工已登录', 'POST不存在码', '提示未找到', '提示错误', '通过'],
    ['TC-062', '出库核销', '已取件重复出库（补充）',
     'picked包裹', 'POST已取件码', '提示未找到', '提示错误', '通过'],
    ['TC-063', '出库核销', '货架数量减少（补充）',
     '货架有pending', '出库后查used_slots', '减1', '数量正确', '通过'],
    ['TC-064', '出库核销', '创建取件记录（补充）',
     'pending包裹', '出库后查pickup_record', '新增记录', '记录正确', '通过'],
]

for i, row in enumerate(test_cases):
    for j, val in enumerate(row):
        if j == 7:
            style = pass_style if val == '通过' else fail_style
            ws1.write(i + 4, j, val, style)
        else:
            ws1.write(i + 4, j, val, normal_style)

# ======================================================================
# Sheet 2: BUG清单
# ======================================================================
ws2 = wb.add_sheet('BUG清单', cell_overwrite_ok=True)

ws2.write_merge(0, 0, 0, 8, '校园快递收发系统 — BUG清单（共15个）', title_style)
ws2.write(1, 0, f'记录日期: {datetime.now().strftime("%Y-%m-%d")}', normal_style)

bug_headers = ['BUG编号', '所属模块', 'BUG标题', '严重程度', '复现步骤', '预期结果', '实际结果', '修复方案', '状态']
bug_widths = [10, 14, 28, 10, 35, 28, 28, 35, 10]
for i, (h, w) in enumerate(zip(bug_headers, bug_widths)):
    ws2.write(3, i, h, header_style)
    ws2.col(i).width = w * 256

bugs = [
    # ===== 已修复 (7个) =====
    ['BUG-001', '出库核销', '出库仅支持取件码，不支持快递单号',
     '高',
     '1. 员工登录\n2. 出库页面输入快递单号\n3. 点击确认出库',
     '支持取件码和快递单号两种方式出库',
     '输入快递单号提示"取件码无效"，无法出库',
     'checkout路由增加tracking_no回退查询',
     '已修复'],

    ['BUG-002', '出库核销', '出库错误提示信息不准确',
     '中',
     '1. 员工登录\n2. 输入不存在的取件码\n3. 提交',
     '给出明确的错误提示',
     '提示"取件码无效或快递已被取走"含义模糊',
     '改为"未找到待出库的快递，请检查输入是否正确"',
     '已修复'],

    ['BUG-003', '出库核销', '空取件码提示信息不友好',
     '低',
     '1. 员工登录\n2. 不输入任何内容直接提交',
     '给出友好提示',
     '提示"请输入取件码"未涵盖快递单号场景',
     '改为"请输入取件码或快递单号"',
     '已修复'],

    ['BUG-004', '入库/寄件/授权', '表单缺少空值校验导致500错误',
     '高',
     '1. 入库时不选快递公司/货架\n2. 寄件时不填收件人\n3. 授权时不选包裹',
     '服务端校验并给出错误提示',
     'int()转换None触发TypeError/500错误',
     '所有int()转换前增加非空校验',
     '已修复'],

    ['BUG-005', '出库核销', '出库页面标签与功能不一致',
     '低',
     '1. 打开出库页面\n2. 查看输入框标签',
     '标签准确描述输入内容',
     '标签写"取件码/快递单号"但后端只支持取件码',
     '后端支持双输入，标签与功能一致',
     '已修复'],

    ['BUG-006', '代取授权', '出库不支持授权码代取',
     '高',
     '1. 学生A授权B代取\n2. B拿授权码去驿站\n3. 员工无法输入授权码',
     '员工可输入授权码验证并完成代取',
     '出库页面无授权码输入框，pickup_type固定为self',
     '出库增加授权码输入框和验证逻辑，支持proxy类型',
     '已修复'],

    ['BUG-007', '代取授权', '授权码无过期检查',
     '中',
     '1. 创建授权（24h有效）\n2. 等待过期\n3. 用过期授权码出库',
     '过期授权码应被拒绝',
     '未检查expires_at，过期授权码仍可使用',
     '增加expires_at校验，过期设status=expired',
     '已修复'],

    # ===== 待修复 (8个) =====
    ['BUG-008', '管理员-用户', '添加用户缺少必填字段校验',
     '中',
     '1. 管理员添加用户\n2. 不填写账号或姓名\n3. 提交',
     '校验必填字段并给出错误提示',
     '可能插入空用户名或空姓名的异常数据',
     '增加username和name字段的非空校验',
     '待修复'],

    ['BUG-009', '管理员-公告', '发布公告缺少标题/内容校验',
     '低',
     '1. 管理员发布公告\n2. 不填标题或内容\n3. 提交',
     '提示"请输入标题和内容"',
     '可能发布空标题或空内容的公告',
     '增加title和content的非空校验',
     '待修复'],

    ['BUG-010', '管理员-用户', '添加用户重复账号校验不完善',
     '中',
     '1. 添加已存在账号\n2. 账号含空格或大小写不同',
     '提示"该账号已存在"',
     '未做strip处理和大小写统一比较',
     '对username做strip并统一小写比较',
     '待修复'],

    ['BUG-011', '学生端-寄件', '寄件记录页面缺少状态筛选',
     '低',
     '1. 学生有多个寄件记录\n2. 查看寄件列表',
     '可按状态筛选',
     '只显示全部记录，无法按状态筛选',
     '增加状态筛选下拉框',
     '待修复'],

    ['BUG-012', '货架管理', '货架使用率精度问题',
     '低',
     '1. 查看货架管理\n2. 观察使用率',
     '显示精确百分比',
     'usage_rate返回整数，49.5%显示为49%',
     '使用浮点数或保留一位小数',
     '待修复'],

    ['BUG-013', '出库核销', '出库后未通知收件人已取走',
     '低',
     '1. 员工出库包裹\n2. 查看收件人通知',
     '收件人收到"快递已取走"通知',
     '出库后未自动生成通知',
     '出库时增加notification记录',
     '待修复'],

    ['BUG-014', '管理员-统计', '统计页面无数据导出功能',
     '低',
     '1. 查询日期范围统计\n2. 需要导出',
     '可导出Excel/CSV',
     '只能在线查看，无法导出',
     '增加导出按钮',
     '待修复'],

    ['BUG-015', '学生端-包裹', '包裹列表缺少分页',
     '低',
     '1. 学生有大量包裹\n2. 查看列表',
     '分页显示',
     '所有包裹一次性加载',
     '增加分页功能',
     '待修复'],
]

for i, row in enumerate(bugs):
    for j, val in enumerate(row):
        if j == 8:
            if val == '已修复':
                style = fixed_style
            elif val == '待修复':
                style = open_style
            else:
                style = info_style
            ws2.write(i + 4, j, val, style)
        else:
            ws2.write(i + 4, j, val, normal_style)

# ======================================================================
# Sheet 3: 测试统计
# ======================================================================
ws3 = wb.add_sheet('测试统计', cell_overwrite_ok=True)

ws3.write_merge(0, 0, 0, 3, '校园快递收发系统 — 测试统计', title_style)
ws3.write(1, 0, f'统计日期: {datetime.now().strftime("%Y-%m-%d")}', normal_style)

# 测试统计表头
stat_headers = ['模块', '用例数', '通过数', '通过率']
for i, h in enumerate(stat_headers):
    ws3.write(3, i, h, header_style)
    ws3.col(i).width = 20 * 256

stats = [
    ['登录认证', 9, 9, '100%'],
    ['出库核销', 11, 11, '100%'],
    ['入库登记', 7, 7, '100%'],
    ['学生端', 15, 15, '100%'],
    ['管理员端', 9, 9, '100%'],
    ['货架管理', 2, 2, '100%'],
    ['消息通知', 1, 1, '100%'],
    ['权限控制', 3, 3, '100%'],
    ['出库补充', 7, 7, '100%'],
    ['合计', 64, 64, '100%'],
]

for i, row in enumerate(stats):
    for j, val in enumerate(row):
        if i == len(stats) - 1:  # 合计行加粗
            ws3.write(i + 4, j, val, pass_style if j >= 1 else xlwt.easyxf(
                'font: name Microsoft YaHei, bold on, height 200;'
                'alignment: horiz centre, vert centre;'
                'borders: left thin, right thin, top thin, bottom thin;'
            ))
        else:
            ws3.write(i + 4, j, val, pass_style if j >= 1 else normal_style)

# BUG统计
ws3.write(14, 0, 'BUG统计', xlwt.easyxf(
    'font: name Microsoft YaHei, bold on, height 240;'
    'alignment: horiz left, vert centre;'
))
bug_stat_headers = ['状态', '数量', '占比']
for i, h in enumerate(bug_stat_headers):
    ws3.write(15, i, h, header_style)

ws3.write(16, 0, '已修复', normal_style)
ws3.write(16, 1, 7, pass_style)
ws3.write(16, 2, '46.7%', pass_style)

ws3.write(17, 0, '待修复', normal_style)
ws3.write(17, 1, 8, open_style)
ws3.write(17, 2, '53.3%', open_style)

ws3.write(18, 0, '合计', normal_style)
ws3.write(18, 1, 15, pass_style)
ws3.write(18, 2, '100%', pass_style)

# 保存
base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, '..', 'test_output')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'test_report.xls')
wb.save(output_path)
print(f'报告已生成: {os.path.abspath(output_path)}')

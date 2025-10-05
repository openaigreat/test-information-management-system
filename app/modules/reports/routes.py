from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app.modules.reports import bp
from app import db
from app.models import User, SystemLog
from app.forms.reports import ReportFilterForm, PersonnelReportForm, AttendanceReportForm, SalaryReportForm, TaskReportForm, KnowledgeReportForm
from datetime import datetime, timedelta
import os
import io
import csv
import json

@bp.route('/')
@login_required
def index():
    """报表管理首页"""
    # 获取报表统计信息
    personnel_count = User.query.count()
    
    # 这里应该从数据库获取其他统计信息
    # 由于模型中可能没有相关的统计模型，我们使用模拟数据
    attendance_count = 150  # 模拟数据
    salary_count = 12  # 模拟数据
    tasks_count = 45  # 模拟数据
    
    return render_template('reports/index.html', title='报表管理', 
                          personnel_count=personnel_count, attendance_count=attendance_count,
                          salary_count=salary_count, tasks_count=tasks_count)

@bp.route('/personnel', methods=['GET', 'POST'])
@login_required
def personnel():
    """人员统计报表"""
    form = PersonnelReportForm()
    departments = []
    positions = []
    
    # 获取部门和职位列表
    users = User.query.all()
    for user in users:
        if user.department and user.department not in departments:
            departments.append(user.department)
        if user.position and user.position not in positions:
            positions.append(user.position)
    
    # 更新表单选项
    form.department.choices = [('', '全部')] + [(d, d) for d in departments]
    form.position.choices = [('', '全部')] + [(p, p) for p in positions]
    
    # 处理表单提交
    if form.validate_on_submit():
        department = form.department.data
        position = form.position.data
        
        # 构建查询
        query = User.query
        if department:
            query = query.filter(User.department == department)
        if position:
            query = query.filter(User.position == position)
        
        users = query.all()
        
        # 统计数据
        department_stats = {}
        position_stats = {}
        
        for user in users:
            # 部门统计
            dept = user.department or '未分类'
            if dept not in department_stats:
                department_stats[dept] = 0
            department_stats[dept] += 1
            
            # 职位统计
            pos = user.position or '未分类'
            if pos not in position_stats:
                position_stats[pos] = 0
            position_stats[pos] += 1
        
        # 记录报表生成日志
        log = SystemLog(
            user_id=current_user.id,
            action='生成人员统计报表',
            description=f'用户 {current_user.username} 生成了人员统计报表',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return render_template('reports/personnel.html', title='人员统计报表', 
                              form=form, users=users, 
                              department_stats=department_stats,
                              position_stats=position_stats)
    
    # 默认查询所有用户
    users = User.query.all()
    
    # 统计数据
    department_stats = {}
    position_stats = {}
    
    for user in users:
        # 部门统计
        dept = user.department or '未分类'
        if dept not in department_stats:
            department_stats[dept] = 0
        department_stats[dept] += 1
        
        # 职位统计
        pos = user.position or '未分类'
        if pos not in position_stats:
            position_stats[pos] = 0
        position_stats[pos] += 1
    
    return render_template('reports/personnel.html', title='人员统计报表', 
                          form=form, users=users, 
                          department_stats=department_stats,
                          position_stats=position_stats)

@bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    """考勤统计报表"""
    form = AttendanceReportForm()
    
    # 处理表单提交
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        department = form.department.data
        
        # 这里应该从数据库获取考勤数据
        # 由于模型中可能没有考勤模型，我们使用模拟数据
        attendance_data = []
        current_date = start_date
        while current_date <= end_date:
            # 模拟考勤数据
            attendance_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total': 20,
                'present': 18,
                'absent': 1,
                'late': 1,
                'leave': 0
            })
            current_date += timedelta(days=1)
        
        # 记录报表生成日志
        log = SystemLog(
            user_id=current_user.id,
            action='生成考勤统计报表',
            description=f'用户 {current_user.username} 生成了考勤统计报表',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return render_template('reports/attendance.html', title='考勤统计报表', 
                              form=form, attendance_data=attendance_data)
    
    # 默认查询本月考勤数据
    today = datetime.now().date()
    start_date = today.replace(day=1)
    
    # 模拟数据
    attendance_data = []
    current_date = start_date
    while current_date <= today:
        # 模拟考勤数据
        attendance_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total': 20,
            'present': 18,
            'absent': 1,
            'late': 1,
            'leave': 0
        })
        current_date += timedelta(days=1)
    
    return render_template('reports/attendance.html', title='考勤统计报表', 
                          form=form, attendance_data=attendance_data)

@bp.route('/salary', methods=['GET', 'POST'])
@login_required
def salary():
    """薪资统计报表"""
    form = SalaryReportForm()
    
    # 获取部门和职位列表
    departments = []
    positions = []
    
    users = User.query.all()
    for user in users:
        if user.department and user.department not in departments:
            departments.append(user.department)
        if user.position and user.position not in positions:
            positions.append(user.position)
    
    return render_template('reports/salary.html', title='薪资统计报表', form=form)

@bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    """任务统计报表"""
    form = TaskReportForm()
    
    # 获取部门和职位列表
    departments = []
    positions = []
    
    users = User.query.all()
    for user in users:
        if user.department and user.department not in departments:
            departments.append(user.department)
        if user.position and user.position not in positions:
            positions.append(user.position)
    
    # 更新表单选项
    form.department.choices = [('', '全部')] + [(d, d) for d in departments]
    form.position.choices = [('', '全部')] + [(p, p) for p in positions]
    
    # 处理表单提交
    if form.validate_on_submit():
        department = form.department.data
        position = form.position.data
        status = form.status.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # 这里应该从数据库获取任务数据
        # 由于模型中可能没有任务模型，我们使用模拟数据
        tasks_data = []
        
        # 构建查询
        query = User.query
        if department:
            query = query.filter(User.department == department)
        if position:
            query = query.filter(User.position == position)
        
        users = query.all()
        
        for user in users:
            # 模拟任务数据
            total_tasks = 10
            completed_tasks = 7
            in_progress_tasks = 2
            pending_tasks = 1
            
            tasks_data.append({
                'user': user,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'completion_rate': round(completed_tasks / total_tasks * 100, 2)
            })
        
        # 记录报表生成日志
        log = SystemLog(
            user_id=current_user.id,
            action='生成任务统计报表',
            description=f'用户 {current_user.username} 生成了任务统计报表',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return render_template('reports/tasks.html', title='任务统计报表', 
                              form=form, tasks_data=tasks_data)
    
    # 默认查询所有任务数据
    tasks_data = []
    
    for user in users:
        # 模拟任务数据
        total_tasks = 10
        completed_tasks = 7
        in_progress_tasks = 2
        pending_tasks = 1
        
        tasks_data.append({
            'user': user,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'completion_rate': round(completed_tasks / total_tasks * 100, 2)
        })
    
    return render_template('reports/tasks.html', title='任务统计报表', 
                          form=form, tasks_data=tasks_data)

@bp.route('/knowledge', methods=['GET', 'POST'])
@login_required
def knowledge():
    """知识库统计报表"""
    form = KnowledgeReportForm()
    
    # 获取部门和职位列表
    departments = []
    positions = []
    
    users = User.query.all()
    for user in users:
        if user.department and user.department not in departments:
            departments.append(user.department)
        if user.position and user.position not in positions:
            positions.append(user.position)
    
    # 更新表单选项
    form.department.choices = [('', '全部')] + [(d, d) for d in departments]
    form.position.choices = [('', '全部')] + [(p, p) for p in positions]
    
    # 处理表单提交
    if form.validate_on_submit():
        department = form.department.data
        position = form.position.data
        category = form.category.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # 这里应该从数据库获取知识库数据
        # 由于模型中可能没有知识库模型，我们使用模拟数据
        knowledge_data = []
        
        # 构建查询
        query = User.query
        if department:
            query = query.filter(User.department == department)
        if position:
            query = query.filter(User.position == position)
        
        users = query.all()
        
        for user in users:
            # 模拟知识库数据
            total_articles = 5
            published_articles = 4
            draft_articles = 1
            total_views = 120
            total_likes = 30
            
            knowledge_data.append({
                'user': user,
                'total_articles': total_articles,
                'published_articles': published_articles,
                'draft_articles': draft_articles,
                'total_views': total_views,
                'total_likes': total_likes
            })
        
        # 记录报表生成日志
        log = SystemLog(
            user_id=current_user.id,
            action='生成知识库统计报表',
            description=f'用户 {current_user.username} 生成了知识库统计报表',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return render_template('reports/knowledge.html', title='知识库统计报表', 
                              form=form, knowledge_data=knowledge_data)
    
    # 默认查询所有知识库数据
    knowledge_data = []
    
    for user in users:
        # 模拟知识库数据
        total_articles = 5
        published_articles = 4
        draft_articles = 1
        total_views = 120
        total_likes = 30
        
        knowledge_data.append({
            'user': user,
            'total_articles': total_articles,
            'published_articles': published_articles,
            'draft_articles': draft_articles,
            'total_views': total_views,
            'total_likes': total_likes
        })
    
    return render_template('reports/knowledge.html', title='知识库统计报表', 
                          form=form, knowledge_data=knowledge_data)

@bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """生成报表"""
    report_type = request.form.get('report_type', '')
    report_format = request.form.get('report_format', 'html')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    
    if not report_type:
        flash('请选择报表类型！')
        return redirect(url_for('reports.index'))
    
    # 根据报表类型重定向到相应的报表页面
    if report_type == 'personnel':
        return redirect(url_for('reports.personnel'))
    elif report_type == 'attendance':
        return redirect(url_for('reports.attendance'))
    elif report_type == 'salary':
        return redirect(url_for('reports.salary'))
    elif report_type == 'tasks':
        return redirect(url_for('reports.tasks'))
    elif report_type == 'knowledge':
        return redirect(url_for('reports.knowledge'))
    else:
        flash('无效的报表类型！')
        return redirect(url_for('reports.index'))

@bp.route('/export/<report_type>')
@login_required
def export(report_type):
    """导出报表"""
    if report_type == 'personnel':
        # 获取人员数据
        users = User.query.all()
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['用户名', '姓名', '邮箱', '部门', '职位', '电话'])
        
        # 写入数据
        for user in users:
            writer.writerow([user.username, user.name, user.email, user.department, user.position, user.phone])
        
        # 创建响应
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='人员统计报表.csv'
        )
    
    elif report_type == 'attendance':
        # 模拟考勤数据
        attendance_data = []
        today = datetime.now().date()
        start_date = today.replace(day=1)
        
        current_date = start_date
        while current_date <= today:
            attendance_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total': 20,
                'present': 18,
                'absent': 1,
                'late': 1,
                'leave': 0
            })
            current_date += timedelta(days=1)
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['日期', '总人数', '出勤人数', '缺勤人数', '迟到人数', '请假人数'])
        
        # 写入数据
        for data in attendance_data:
            writer.writerow([data['date'], data['total'], data['present'], 
                            data['absent'], data['late'], data['leave']])
        
        # 创建响应
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='考勤统计报表.csv'
        )
    
    else:
        flash('不支持的报表类型！')
        return redirect(url_for('reports.index'))
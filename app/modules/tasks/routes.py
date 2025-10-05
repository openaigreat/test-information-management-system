from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app.modules.tasks import bp
from app import db

@bp.route('/tasks')
@login_required
def index():
    """任务管理首页"""
    # 这里应该从数据库获取任务列表，暂时使用空列表
    tasks = []
    return render_template('tasks/index.html', title='任务管理', tasks=tasks)

@bp.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加任务"""
    if request.method == 'POST':
        # 这里应该处理表单数据并保存到数据库
        flash('任务添加成功！')
        return redirect(url_for('tasks.index'))
    
    return render_template('tasks/add.html', title='添加任务')

@bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """编辑任务"""
    # 这里应该从数据库获取任务信息
    if request.method == 'POST':
        # 这里应该处理表单数据并更新到数据库
        flash('任务更新成功！')
        return redirect(url_for('tasks.index'))
    
    return render_template('tasks/edit.html', title='编辑任务')

@bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    """删除任务"""
    # 这里应该从数据库删除任务
    flash('任务删除成功！')
    return redirect(url_for('tasks.index'))

@bp.route('/tasks/view/<int:task_id>')
@login_required
def view(task_id):
    """查看任务详情"""
    # 这里应该从数据库获取任务详情
    return render_template('tasks/view.html', title='任务详情')

@bp.route('/tasks/my')
@login_required
def my_tasks():
    """我的任务"""
    # 这里应该从数据库获取当前用户的任务列表
    return render_template('tasks/my_tasks.html', title='我的任务')

@bp.route('/tasks/complete/<int:task_id>', methods=['POST'])
@login_required
def complete(task_id):
    """完成任务"""
    # 这里应该更新任务状态为已完成
    flash('任务已完成！')
    return redirect(url_for('tasks.my_tasks'))
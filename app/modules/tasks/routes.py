from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.modules.tasks import bp
from app.modules.tasks.forms import TaskForm
from app.models import Task, TaskComment, User
from app import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """任务管理首页"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    assignee_id = request.args.get('assignee_id')
    
    query = Task.query
    
    if status:
        query = query.filter_by(status=status)
    
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    
    tasks = query.order_by(Task.due_date.asc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有状态和任务负责人用于筛选
    statuses = db.session.query(Task.status).distinct().all()
    assignees = db.session.query(User).join(Task, User.id == Task.assignee_id).distinct().all()
    
    # 计算任务状态统计
    all_tasks = Task.query.all()
    in_progress_count = sum(1 for t in all_tasks if t.status == 'in_progress')
    completed_count = sum(1 for t in all_tasks if t.status == 'completed')
    overdue_count = sum(1 for t in all_tasks if t.status == 'overdue')
    
    return render_template('tasks/index.html', title='任务管理', 
                         tasks=tasks, statuses=statuses, assignees=assignees,
                         in_progress_count=in_progress_count, completed_count=completed_count,
                         overdue_count=overdue_count)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加任务"""
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            assignee_id=form.assignee_id.data,
            project_id=form.project_id.data if form.project_id.data != 0 else None,
            start_date=form.start_date.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            status=form.status.data,
            estimated_hours=form.estimated_hours.data,
            actual_hours=form.actual_hours.data,
            progress=form.progress.data,
            notes=form.notes.data,
            creator_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        flash('任务添加成功！')
        return redirect(url_for('tasks.index'))
    
    return render_template('tasks/add.html', title='添加任务', form=form)

@bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """编辑任务"""
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.assignee_id = form.assignee_id.data
        task.project_id = form.project_id.data if form.project_id.data != 0 else None
        task.start_date = form.start_date.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.status = form.status.data
        task.estimated_hours = form.estimated_hours.data
        task.actual_hours = form.actual_hours.data
        task.progress = form.progress.data
        task.notes = form.notes.data
        
        db.session.commit()
        flash('任务更新成功！')
        return redirect(url_for('tasks.index'))
    
    return render_template('tasks/edit.html', title='编辑任务', form=form, task=task)

@bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    """删除任务"""
    task = Task.query.get_or_404(task_id)
    
    # 删除相关任务评论
    TaskComment.query.filter_by(task_id=task_id).delete()
    
    db.session.delete(task)
    db.session.commit()
    flash('任务删除成功！')
    return redirect(url_for('tasks.index'))

@bp.route('/view/<int:task_id>')
@login_required
def view(task_id):
    """查看任务详情"""
    task = Task.query.get_or_404(task_id)
    
    # 获取任务评论
    comments = db.session.query(TaskComment, User).join(
        User, TaskComment.user_id == User.id
    ).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at.desc()).all()
    
    return render_template('tasks/view.html', title='任务详情', task=task, comments=comments)

@bp.route('/my')
@login_required
def my_tasks():
    """我的任务"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Task.query.filter_by(assignee_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.order_by(Task.due_date.asc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有状态用于筛选
    statuses = db.session.query(Task.status).distinct().all()
    
    # 计算任务状态统计
    all_tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    in_progress_count = sum(1 for t in all_tasks if t.status == 'in_progress')
    completed_count = sum(1 for t in all_tasks if t.status == 'completed')
    overdue_count = sum(1 for t in all_tasks if t.status == 'overdue')
    
    return render_template('tasks/my_tasks.html', title='我的任务', tasks=tasks, statuses=statuses,
                         in_progress_count=in_progress_count, completed_count=completed_count,
                         overdue_count=overdue_count)

@bp.route('/complete/<int:task_id>', methods=['POST'])
@login_required
def complete(task_id):
    """完成任务"""
    task = Task.query.get_or_404(task_id)
    
    # 检查任务是否分配给当前用户
    if task.assignee_id != current_user.id:
        flash('您只能完成分配给您的任务！', 'danger')
        return redirect(url_for('tasks.my_tasks'))
    
    task.status = 'done'
    task.completed_date = datetime.utcnow()
    task.progress = 100
    
    db.session.commit()
    flash('任务已完成！')
    return redirect(url_for('tasks.my_tasks'))

@bp.route('/comment/<int:task_id>', methods=['POST'])
@login_required
def add_comment(task_id):
    """添加任务评论"""
    task = Task.query.get_or_404(task_id)
    content = request.form.get('content')
    
    comment = TaskComment(
        task_id=task_id,
        user_id=current_user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    flash('评论添加成功！')
    return redirect(url_for('tasks.view', task_id=task_id))
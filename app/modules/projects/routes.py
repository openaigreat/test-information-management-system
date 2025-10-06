from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.modules.projects import bp
from app.modules.projects.forms import ProjectForm
from app.models import Project, Task, TaskComment, TaskAttachment, User
from app import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """项目管理首页"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status')
    manager_id = request.args.get('manager_id')
    
    query = Project.query
    
    if keyword:
        query = query.filter(
            Project.name.contains(keyword) | 
            Project.code.contains(keyword) | 
            Project.description.contains(keyword)
        )
    
    if status:
        query = query.filter_by(status=status)
    
    if manager_id:
        query = query.filter_by(manager_id=manager_id)
    
    projects = query.order_by(Project.start_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有状态和项目经理用于筛选
    statuses = db.session.query(Project.status).distinct().all()
    managers = db.session.query(User).join(Project, User.id == Project.manager_id).distinct().all()
    
    # 计算项目状态统计
    all_projects = Project.query.all()
    in_progress_count = sum(1 for p in all_projects if p.status == 'in_progress')
    completed_count = sum(1 for p in all_projects if p.status == 'completed')
    on_hold_count = sum(1 for p in all_projects if p.status == 'on_hold')
    
    return render_template('projects/index.html', title='项目管理', 
                         projects=projects, statuses=statuses, managers=managers,
                         in_progress_count=in_progress_count, completed_count=completed_count,
                         on_hold_count=on_hold_count)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加项目"""
    form = ProjectForm()
    if form.validate_on_submit():
        # 检查项目名称和代码是否已存在
        if Project.query.filter_by(name=form.name.data).first():
            flash('项目名称已存在！', 'danger')
            return redirect(url_for('projects.add'))
        
        if form.code.data and Project.query.filter_by(project_code=form.code.data).first():
            flash('项目代码已存在！', 'danger')
            return redirect(url_for('projects.add'))
        
        project = Project(
            name=form.name.data,
            project_code=form.code.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            manager_id=form.manager_id.data,
            status=form.status.data,
            priority=form.priority.data,
            notes="",  # 表单中没有notes字段
            created_by=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('项目添加成功！')
        return redirect(url_for('projects.index'))
    
    return render_template('projects/add.html', title='添加项目', form=form)

@bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """编辑项目"""
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        # 检查项目名称和代码是否已存在（排除当前项目）
        if Project.query.filter(Project.id != project_id, Project.name == form.name.data).first():
            flash('项目名称已存在！', 'danger')
            return redirect(url_for('projects.edit', project_id=project_id))
        
        if form.code.data and Project.query.filter(Project.id != project_id, Project.code == form.code.data).first():
            flash('项目代码已存在！', 'danger')
            return redirect(url_for('projects.edit', project_id=project_id))
        
        project.name = form.name.data
        project.code = form.code.data
        project.description = form.description.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.budget = form.budget.data
        project.manager_id = form.manager_id.data
        project.status = form.status.data
        project.priority = form.priority.data
        project.progress = 0  # 表单中没有progress字段
        
        db.session.commit()
        flash('项目信息更新成功！')
        return redirect(url_for('projects.index'))
    
    return render_template('projects/edit.html', title='编辑项目', form=form, project=project)

@bp.route('/delete/<int:project_id>', methods=['POST'])
@login_required
def delete(project_id):
    """删除项目"""
    project = Project.query.get_or_404(project_id)
    
    # 删除相关任务
    Task.query.filter_by(project_id=project_id).delete()
    # 删除相关项目成员
    ProjectMember.query.filter_by(project_id=project_id).delete()
    # 删除相关项目文档
    ProjectDocument.query.filter_by(project_id=project_id).delete()
    # 删除相关项目进度
    ProjectSchedule.query.filter_by(project_id=project_id).delete()
    # 删除相关项目核算
    ProjectAccounting.query.filter_by(project_id=project_id).delete()
    
    db.session.delete(project)
    db.session.commit()
    flash('项目删除成功！')
    return redirect(url_for('projects.index'))

@bp.route('/view/<int:project_id>')
@login_required
def view(project_id):
    """查看项目详情"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目任务统计
    total_tasks = Task.query.filter_by(project_id=project_id).count()
    completed_tasks = Task.query.filter_by(
        project_id=project_id, status='completed'
    ).count()
    
    # 由于ProjectMember模型已移除，不再查询项目成员
    members = []
    
    # 由于ProjectSchedule模型已移除，不再查询进度节点
    recent_schedules = []
    
    return render_template('projects/view.html', title='项目详情', project=project,
                         members=members, total_tasks=total_tasks, 
                         completed_tasks=completed_tasks, recent_schedules=recent_schedules)

@bp.route('/tasks/<int:project_id>')
@login_required
def tasks(project_id):
    """项目任务管理"""
    project = Project.query.get_or_404(project_id)
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    assignee_id = request.args.get('assignee_id')
    
    query = Task.query.filter_by(project_id=project_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    
    tasks = query.order_by(Task.due_date.asc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有状态和任务负责人用于筛选
    statuses = db.session.query(Task.status).distinct().all()
    assignees = db.session.query(User).join(Task, User.id == Task.assignee_id).filter(
        Task.project_id == project_id
    ).distinct().all()
    
    # 计算任务状态统计
    all_tasks = Task.query.filter_by(project_id=project_id).all()
    in_progress_count = sum(1 for t in all_tasks if t.status == 'in_progress')
    completed_count = sum(1 for t in all_tasks if t.status == 'completed')
    overdue_count = sum(1 for t in all_tasks if t.status == 'overdue')
    
    return render_template('projects/tasks.html', title='项目任务', project=project,
                         tasks=tasks, statuses=statuses, assignees=assignees,
                         in_progress_count=in_progress_count, completed_count=completed_count,
                         overdue_count=overdue_count)

@bp.route('/tasks/add/<int:project_id>', methods=['GET', 'POST'])
@login_required
def add_task(project_id):
    """添加项目任务"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assignee_id = request.form.get('assignee_id')
        start_date = request.form.get('start_date')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')
        status = request.form.get('status')
        estimated_hours = float(request.form.get('estimated_hours', 0))
        notes = request.form.get('notes')
        
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            priority=priority,
            status=status,
            estimated_hours=estimated_hours,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        flash('任务添加成功！')
        return redirect(url_for('projects.tasks', project_id=project_id))
    
    users = User.query.all()
    return render_template('projects/add_task.html', title='添加任务', project=project, users=users)

@bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """编辑项目任务"""
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.assignee_id = request.form.get('assignee_id')
        task.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date() if request.form.get('start_date') else None
        task.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None
        task.priority = request.form.get('priority')
        task.status = request.form.get('status')
        task.estimated_hours = float(request.form.get('estimated_hours', 0))
        task.actual_hours = float(request.form.get('actual_hours', 0))
        task.progress = int(request.form.get('progress', 0))
        task.notes = request.form.get('notes')
        
        db.session.commit()
        flash('任务信息更新成功！')
        return redirect(url_for('projects.tasks', project_id=task.project_id))
    
    users = User.query.all()
    return render_template('projects/edit_task.html', title='编辑任务', task=task, project=project, users=users)

@bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """删除项目任务"""
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    
    # 删除相关任务评论
    TaskComment.query.filter_by(task_id=task_id).delete()
    # 删除相关任务附件
    TaskAttachment.query.filter_by(task_id=task_id).delete()
    
    db.session.delete(task)
    db.session.commit()
    flash('任务删除成功！')
    return redirect(url_for('projects.tasks', project_id=project_id))

@bp.route('/tasks/view/<int:task_id>')
@login_required
def view_task(task_id):
    """查看任务详情"""
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    
    # 获取任务评论
    comments = db.session.query(TaskComment, User).join(
        User, TaskComment.user_id == User.id
    ).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at.desc()).all()
    
    # 获取任务附件
    attachments = TaskAttachment.query.filter_by(task_id=task_id).all()
    
    return render_template('projects/view_task.html', title='任务详情', task=task,
                         project=project, comments=comments, attachments=attachments)

@bp.route('/tasks/comment/<int:task_id>', methods=['POST'])
@login_required
def add_task_comment(task_id):
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
    return redirect(url_for('projects.view_task', task_id=task_id))

@bp.route('/members/<int:project_id>')
@login_required
def members(project_id):
    """项目成员管理"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目成员
    members = db.session.query(ProjectMember, User).join(
        User, ProjectMember.user_id == User.id
    ).filter(ProjectMember.project_id == project_id).all()
    
    # 获取非项目成员用户
    member_ids = [m[1].id for m in members]
    non_members = User.query.filter(~User.id.in_(member_ids)).all()
    
    # 计算成员角色统计
    total_members = len(members)
    manager_count = sum(1 for m in members if m[0].role == 'manager')
    developer_count = sum(1 for m in members if m[0].role == 'developer')
    tester_count = sum(1 for m in members if m[0].role == 'tester')
    
    return render_template('projects/members.html', title='项目成员', project=project,
                         members=members, non_members=non_members,
                         total_members=total_members, manager_count=manager_count, 
                         developer_count=developer_count, tester_count=tester_count)

@bp.route('/members/add/<int:project_id>', methods=['POST'])
@login_required
def add_member(project_id):
    """添加项目成员"""
    project = Project.query.get_or_404(project_id)
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    
    # 检查用户是否已经是项目成员
    if ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first():
        flash('该用户已经是项目成员！', 'danger')
        return redirect(url_for('projects.members', project_id=project_id))
    
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
        created_by=current_user.id
    )
    
    db.session.add(member)
    db.session.commit()
    flash('成员添加成功！')
    return redirect(url_for('projects.members', project_id=project_id))

@bp.route('/members/remove/<int:project_id>/<int:user_id>', methods=['POST'])
@login_required
def remove_member(project_id, user_id):
    """移除项目成员"""
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    
    if not member:
        flash('该用户不是项目成员！', 'danger')
        return redirect(url_for('projects.members', project_id=project_id))
    
    db.session.delete(member)
    db.session.commit()
    flash('成员移除成功！')
    return redirect(url_for('projects.members', project_id=project_id))

@bp.route('/documents/<int:project_id>')
@login_required
def documents(project_id):
    """项目文档整理"""
    project = Project.query.get_or_404(project_id)
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    
    query = ProjectDocument.query.filter_by(project_id=project_id)
    
    if category:
        query = query.filter_by(category=category)
    
    documents = query.order_by(ProjectDocument.upload_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有文档类别
    categories = db.session.query(ProjectDocument.category).distinct().all()
    
    return render_template('projects/documents.html', title='项目文档', project=project,
                         documents=documents, categories=categories)

@bp.route('/documents/upload/<int:project_id>', methods=['POST'])
@login_required
def upload_document(project_id):
    """上传项目文档"""
    project = Project.query.get_or_404(project_id)
    
    if 'file' not in request.files:
        flash('没有选择文件！', 'danger')
        return redirect(url_for('projects.documents', project_id=project_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件！', 'danger')
        return redirect(url_for('projects.documents', project_id=project_id))
    
    # 这里应该处理文件上传，保存文件并记录到数据库
    # 简化处理，只记录文档信息
    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    
    document = ProjectDocument(
        project_id=project_id,
        title=title,
        file_name=file.filename,
        file_path='',  # 实际应用中应该保存文件路径
        category=category,
        description=description,
        uploaded_by=current_user.id
    )
    
    db.session.add(document)
    db.session.commit()
    flash('文档上传成功！')
    return redirect(url_for('projects.documents', project_id=project_id))

@bp.route('/documents/delete/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    """删除项目文档"""
    document = ProjectDocument.query.get_or_404(document_id)
    project_id = document.project_id
    
    # 这里应该删除实际文件
    db.session.delete(document)
    db.session.commit()
    flash('文档删除成功！')
    return redirect(url_for('projects.documents', project_id=project_id))

@bp.route('/schedule/<int:project_id>')
@login_required
def schedule(project_id):
    """项目进度节点"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目进度节点
    schedules = ProjectSchedule.query.filter_by(
        project_id=project_id
    ).order_by(ProjectSchedule.start_date.asc()).all()
    
    return render_template('projects/schedule.html', title='项目进度', project=project,
                         schedules=schedules)

@bp.route('/schedule/add/<int:project_id>', methods=['POST'])
@login_required
def add_schedule(project_id):
    """添加项目进度节点"""
    project = Project.query.get_or_404(project_id)
    
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    schedule = ProjectSchedule(
        project_id=project_id,
        title=name,
        description=description,
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
        status=status,
        notes=notes,
        created_by=current_user.id
    )
    
    db.session.add(schedule)
    db.session.commit()
    flash('进度节点添加成功！')
    return redirect(url_for('projects.schedule', project_id=project_id))

@bp.route('/schedule/edit/<int:schedule_id>', methods=['POST'])
@login_required
def edit_schedule(schedule_id):
    """编辑项目进度节点"""
    schedule = ProjectSchedule.query.get_or_404(schedule_id)
    
    schedule.title = request.form.get('name')
    schedule.description = request.form.get('description')
    schedule.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    schedule.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    schedule.status = request.form.get('status')
    schedule.actual_start_date = datetime.strptime(request.form.get('actual_start_date'), '%Y-%m-%d').date() if request.form.get('actual_start_date') else None
    schedule.actual_end_date = datetime.strptime(request.form.get('actual_end_date'), '%Y-%m-%d').date() if request.form.get('actual_end_date') else None
    schedule.notes = request.form.get('notes')
    
    db.session.commit()
    flash('进度节点更新成功！')
    return redirect(url_for('projects.schedule', project_id=schedule.project_id))

@bp.route('/schedule/delete/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    """删除项目进度节点"""
    schedule = ProjectSchedule.query.get_or_404(schedule_id)
    project_id = schedule.project_id
    
    db.session.delete(schedule)
    db.session.commit()
    flash('进度节点删除成功！')
    return redirect(url_for('projects.schedule', project_id=project_id))

@bp.route('/accounting/<int:project_id>')
@login_required
def accounting(project_id):
    """项目核算"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目核算记录
    accountings = ProjectAccounting.query.filter_by(
        project_id=project_id
    ).order_by(ProjectAccounting.record_date.desc()).all()
    
    # 计算项目总支出
    total_expense = db.session.query(db.func.sum(ProjectAccounting.amount)).filter_by(
        project_id=project_id, type='expense'
    ).scalar() or 0
    
    # 计算项目总收入
    total_income = db.session.query(db.func.sum(ProjectAccounting.amount)).filter_by(
        project_id=project_id, type='income'
    ).scalar() or 0
    
    # 计算项目利润
    profit = total_income - total_expense
    
    accounting_summary = {
        'total_expense': total_expense,
        'total_income': total_income,
        'profit': profit,
        'budget': project.budget,
        'budget_remaining': project.budget - total_expense
    }
    
    return render_template('projects/accounting.html', title='项目核算', project=project,
                         accountings=accountings, accounting_summary=accounting_summary)

@bp.route('/accounting/add/<int:project_id>', methods=['POST'])
@login_required
def add_accounting(project_id):
    """添加项目核算记录"""
    project = Project.query.get_or_404(project_id)
    
    title = request.form.get('title')
    type = request.form.get('type')
    amount = float(request.form.get('amount', 0))
    record_date = request.form.get('record_date')
    category = request.form.get('category')
    description = request.form.get('description')
    notes = request.form.get('notes')
    
    accounting = ProjectAccounting(
        project_id=project_id,
        title=title,
        type=type,
        amount=amount,
        record_date=datetime.strptime(record_date, '%Y-%m-%d').date(),
        category=category,
        description=description,
        notes=notes,
        created_by=current_user.id
    )
    
    db.session.add(accounting)
    db.session.commit()
    flash('核算记录添加成功！')
    return redirect(url_for('projects.accounting', project_id=project_id))

@bp.route('/accounting/delete/<int:accounting_id>', methods=['POST'])
@login_required
def delete_accounting(accounting_id):
    """删除项目核算记录"""
    accounting = ProjectAccounting.query.get_or_404(accounting_id)
    project_id = accounting.project_id
    
    db.session.delete(accounting)
    db.session.commit()
    flash('核算记录删除成功！')
    return redirect(url_for('projects.accounting', project_id=project_id))

@bp.route('/records/<int:project_id>')
@login_required
def records(project_id):
    """项目过程记录"""
    project = Project.query.get_or_404(project_id)
    
    # 获取项目任务记录
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.created_at.desc()).limit(10).all()
    
    # 获取项目进度记录
    schedules = ProjectSchedule.query.filter_by(
        project_id=project_id
    ).order_by(ProjectSchedule.created_at.desc()).limit(5).all()
    
    # 获取项目核算记录
    accountings = ProjectAccounting.query.filter_by(
        project_id=project_id
    ).order_by(ProjectAccounting.created_at.desc()).limit(5).all()
    
    return render_template('projects/records.html', title='过程记录', project=project,
                         tasks=tasks, schedules=schedules, accountings=accountings)
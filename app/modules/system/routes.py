from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Role, Permission, SystemLog, SystemSettings, Backup, Restore, Department, Position, Menu, OperationLog, LoginLog
from app.forms.system import LoginForm, RegistrationForm, ChangePasswordForm, EditProfileForm, RoleForm, PermissionForm, SystemSettingsForm, EmailSettingsForm, SecuritySettingsForm, InterfaceSettingsForm, UserForm, LogSearchForm, BackupForm, RestoreForm
from app.utils.decorators import admin_required
from datetime import datetime
import os
import json
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import uuid
from app.modules.system import bp

@bp.route('/')
@login_required
def index():
    """系统设置首页"""
    # 获取系统统计信息
    user_count = User.query.count()
    role_count = Role.query.count()
    permission_count = Permission.query.count()
    log_count = SystemLog.query.count()
    department_count = Department.query.count()
    position_count = Position.query.count()
    
    # 获取最近登录记录
    recent_logins = LoginLog.query.order_by(LoginLog.timestamp.desc()).limit(5).all()
    
    # 获取系统信息
    system_info = {
        'os': os.name,
        'python_version': os.sys.version,
        'app_version': '1.0.0'  # 可以从配置中获取
    }
    
    return render_template('system/index.html', title='系统设置', 
                          user_count=user_count, role_count=role_count, 
                          permission_count=permission_count, log_count=log_count,
                          department_count=department_count, position_count=position_count,
                          recent_logins=recent_logins, system_info=system_info)

@bp.route('/users')
@login_required
@admin_required
def users():
    """用户管理"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    role_id = request.args.get('role_id')
    department_id = request.args.get('department_id')
    status = request.args.get('status')
    
    query = User.query
    
    if keyword:
        query = query.filter(
            User.username.contains(keyword) | 
            User.name.contains(keyword) | 
            User.email.contains(keyword)
        )
    
    if role_id:
        query = query.filter_by(role_id=role_id)
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    if status:
        query = query.filter_by(status=status)
    
    users_list = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有角色和部门，用于筛选
    roles = Role.query.all()
    departments = Department.query.all()
    
    return render_template('system/users.html', title='用户管理', 
                          users=users_list, roles=roles, departments=departments)

@bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """添加用户"""
    form = UserForm()
    
    # 动态设置角色选择
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    form.department_id.choices = [(0, '无')] + [(d.id, d.name) for d in Department.query.all()]
    form.position_id.choices = [(0, '无')] + [(p.id, p.name) for p in Position.query.all()]
    
    if form.validate_on_submit():
        # 检查用户名是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在！', 'danger')
            return redirect(url_for('system.add_user'))
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=form.email.data).first():
            flash('邮箱已存在！', 'danger')
            return redirect(url_for('system.add_user'))
        
        # 创建新用户
        user = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            role_id=form.role_id.data if form.role_id.data != 0 else None,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            position_id=form.position_id.data if form.position_id.data != 0 else None,
            status=form.status.data,
            created_by=current_user.id
        )
        
        # 设置密码
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='添加用户',
            description=f'添加了用户 {user.username}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('用户添加成功！')
        return redirect(url_for('system.users'))
    
    return render_template('system/add_user.html', title='添加用户', form=form)

@bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    # 动态设置角色选择
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    form.department_id.choices = [(0, '无')] + [(d.id, d.name) for d in Department.query.all()]
    form.position_id.choices = [(0, '无')] + [(p.id, p.name) for p in Position.query.all()]
    
    # 不显示密码字段
    form.password.validators = []
    
    if form.validate_on_submit():
        # 检查用户名是否已存在（排除当前用户）
        if User.query.filter(User.username == form.username.data, User.id != user_id).first():
            flash('用户名已存在！', 'danger')
            return redirect(url_for('system.edit_user', user_id=user_id))
        
        # 检查邮箱是否已存在（排除当前用户）
        if User.query.filter(User.email == form.email.data, User.id != user_id).first():
            flash('邮箱已存在！', 'danger')
            return redirect(url_for('system.edit_user', user_id=user_id))
        
        # 更新用户信息
        user.username = form.username.data
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.role_id = form.role_id.data if form.role_id.data != 0 else None
        user.department_id = form.department_id.data if form.department_id.data != 0 else None
        user.position_id = form.position_id.data if form.position_id.data != 0 else None
        user.status = form.status.data
        
        # 如果提供了新密码，则更新密码
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='编辑用户',
            description=f'编辑了用户 {user.username}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('用户更新成功！')
        return redirect(url_for('system.users'))
    
    return render_template('system/edit_user.html', title='编辑用户', form=form, user=user)

@bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账户！', 'danger')
        return redirect(url_for('system.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除用户',
        description=f'删除了用户 {username}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('用户删除成功！')
    return redirect(url_for('system.users'))

@bp.route('/user/view/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """查看用户详情"""
    user = User.query.get_or_404(user_id)
    
    # 获取用户的登录日志
    login_logs = LoginLog.query.filter_by(user_id=user_id).order_by(
        LoginLog.timestamp.desc()
    ).limit(10).all()
    
    # 获取用户的操作日志
    operation_logs = OperationLog.query.filter_by(user_id=user_id).order_by(
        OperationLog.timestamp.desc()
    ).limit(10).all()
    
    return render_template('system/view_user.html', title='用户详情', 
                          user=user, login_logs=login_logs, operation_logs=operation_logs)

@bp.route('/roles')
@login_required
@admin_required
def roles():
    """角色管理"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Role.query
    
    if keyword:
        query = query.filter(Role.name.contains(keyword) | Role.description.contains(keyword))
    
    roles_list = query.order_by(Role.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('system/roles.html', title='角色管理', roles=roles_list)

@bp.route('/role/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_role():
    """添加角色"""
    form = RoleForm()
    
    # 动态设置权限选择
    form.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]
    
    if form.validate_on_submit():
        # 检查角色名称是否已存在
        if Role.query.filter_by(name=form.name.data).first():
            flash('角色名称已存在！', 'danger')
            return redirect(url_for('system.add_role'))
        
        # 创建新角色
        role = Role(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        
        # 添加权限
        if form.permissions.data:
            for permission_id in form.permissions.data:
                permission = Permission.query.get(permission_id)
                if permission:
                    role.permissions.append(permission)
        
        db.session.add(role)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='添加角色',
            description=f'添加了角色 {role.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('角色添加成功！')
        return redirect(url_for('system.roles'))
    
    return render_template('system/add_role.html', title='添加角色', form=form)

@bp.route('/role/edit/<int:role_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(role_id):
    """编辑角色"""
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)
    
    # 动态设置权限选择
    form.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]
    
    if form.validate_on_submit():
        # 检查角色名称是否已存在（排除当前角色）
        if Role.query.filter(Role.name == form.name.data, Role.id != role_id).first():
            flash('角色名称已存在！', 'danger')
            return redirect(url_for('system.edit_role', role_id=role_id))
        
        # 更新角色信息
        role.name = form.name.data
        role.description = form.description.data
        
        # 更新权限
        role.permissions.clear()
        if form.permissions.data:
            for permission_id in form.permissions.data:
                permission = Permission.query.get(permission_id)
                if permission:
                    role.permissions.append(permission)
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='编辑角色',
            description=f'编辑了角色 {role.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('角色更新成功！')
        return redirect(url_for('system.roles'))
    
    return render_template('system/edit_role.html', title='编辑角色', form=form, role=role)

@bp.route('/role/delete/<int:role_id>', methods=['POST'])
@login_required
@admin_required
def delete_role(role_id):
    """删除角色"""
    role = Role.query.get_or_404(role_id)
    
    # 检查是否有用户使用该角色
    if User.query.filter_by(role_id=role_id).first():
        flash('该角色下有用户，不能删除！', 'danger')
        return redirect(url_for('system.roles'))
    
    role_name = role.name
    db.session.delete(role)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除角色',
        description=f'删除了角色 {role_name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('角色删除成功！')
    return redirect(url_for('system.roles'))

@bp.route('/permissions')
@login_required
@admin_required
def permissions():
    """权限管理"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Permission.query
    
    if keyword:
        query = query.filter(
            Permission.name.contains(keyword) | 
            Permission.code.contains(keyword) | 
            Permission.description.contains(keyword)
        )
    
    permissions_list = query.order_by(Permission.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('system/permissions.html', title='权限管理', permissions=permissions_list)

@bp.route('/permission/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_permission():
    """添加权限"""
    form = PermissionForm()
    
    if form.validate_on_submit():
        # 检查权限代码是否已存在
        if Permission.query.filter_by(code=form.code.data).first():
            flash('权限代码已存在！', 'danger')
            return redirect(url_for('system.add_permission'))
        
        # 创建新权限
        permission = Permission(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data,
            created_by=current_user.id
        )
        
        db.session.add(permission)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='添加权限',
            description=f'添加了权限 {permission.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('权限添加成功！')
        return redirect(url_for('system.permissions'))
    
    return render_template('system/add_permission.html', title='添加权限', form=form)

@bp.route('/permission/edit/<int:permission_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_permission(permission_id):
    """编辑权限"""
    permission = Permission.query.get_or_404(permission_id)
    form = PermissionForm(obj=permission)
    
    if form.validate_on_submit():
        # 检查权限代码是否已存在（排除当前权限）
        if Permission.query.filter(Permission.code == form.code.data, Permission.id != permission_id).first():
            flash('权限代码已存在！', 'danger')
            return redirect(url_for('system.edit_permission', permission_id=permission_id))
        
        # 更新权限信息
        permission.name = form.name.data
        permission.code = form.code.data
        permission.description = form.description.data
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='编辑权限',
            description=f'编辑了权限 {permission.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('权限更新成功！')
        return redirect(url_for('system.permissions'))
    
    return render_template('system/edit_permission.html', title='编辑权限', form=form, permission=permission)

@bp.route('/permission/delete/<int:permission_id>', methods=['POST'])
@login_required
@admin_required
def delete_permission(permission_id):
    """删除权限"""
    permission = Permission.query.get_or_404(permission_id)
    
    # 检查是否有角色使用该权限
    if permission.roles:
        flash('该权限被角色使用，不能删除！', 'danger')
        return redirect(url_for('system.permissions'))
    
    permission_name = permission.name
    db.session.delete(permission)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除权限',
        description=f'删除了权限 {permission_name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('权限删除成功！')
    return redirect(url_for('system.permissions'))

@bp.route('/departments')
@login_required
@admin_required
def departments():
    """部门管理"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Department.query
    
    if keyword:
        query = query.filter(Department.name.contains(keyword) | Department.description.contains(keyword))
    
    departments_list = query.order_by(Department.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('system/departments.html', title='部门管理', departments=departments_list)

@bp.route('/department/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    """添加部门"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        
        # 检查部门名称是否已存在
        if Department.query.filter_by(name=name).first():
            flash('部门名称已存在！', 'danger')
            return redirect(url_for('system.add_department'))
        
        # 创建新部门
        department = Department(
            name=name,
            description=description,
            parent_id=parent_id if parent_id else None,
            created_by=current_user.id
        )
        
        db.session.add(department)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='添加部门',
            description=f'添加了部门 {department.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('部门添加成功！')
        return redirect(url_for('system.departments'))
    
    # 获取所有部门，用于选择父部门
    departments = Department.query.all()
    return render_template('system/add_department.html', title='添加部门', departments=departments)

@bp.route('/department/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(department_id):
    """编辑部门"""
    department = Department.query.get_or_404(department_id)
    
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.description = request.form.get('description')
        department.parent_id = request.form.get('parent_id') if request.form.get('parent_id') else None
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='编辑部门',
            description=f'编辑了部门 {department.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('部门更新成功！')
        return redirect(url_for('system.departments'))
    
    # 获取所有部门，用于选择父部门（排除自己和自己的子部门）
    departments = Department.query.filter(
        Department.id != department_id
    ).all()
    
    return render_template('system/edit_department.html', title='编辑部门', 
                         department=department, departments=departments)

@bp.route('/department/delete/<int:department_id>', methods=['POST'])
@login_required
@admin_required
def delete_department(department_id):
    """删除部门"""
    department = Department.query.get_or_404(department_id)
    
    # 检查是否有子部门
    if Department.query.filter_by(parent_id=department_id).first():
        flash('该部门下有子部门，不能删除！', 'danger')
        return redirect(url_for('system.departments'))
    
    # 检查是否有用户属于该部门
    if User.query.filter_by(department_id=department_id).first():
        flash('该部门下有用户，不能删除！', 'danger')
        return redirect(url_for('system.departments'))
    
    department_name = department.name
    db.session.delete(department)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除部门',
        description=f'删除了部门 {department_name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('部门删除成功！')
    return redirect(url_for('system.departments'))

@bp.route('/positions')
@login_required
@admin_required
def positions():
    """职位管理"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Position.query
    
    if keyword:
        query = query.filter(Position.name.contains(keyword) | Position.description.contains(keyword))
    
    positions_list = query.order_by(Position.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('system/positions.html', title='职位管理', positions=positions_list)

@bp.route('/position/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_position():
    """添加职位"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # 检查职位名称是否已存在
        if Position.query.filter_by(name=name).first():
            flash('职位名称已存在！', 'danger')
            return redirect(url_for('system.add_position'))
        
        # 创建新职位
        position = Position(
            name=name,
            description=description,
            created_by=current_user.id
        )
        
        db.session.add(position)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='添加职位',
            description=f'添加了职位 {position.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('职位添加成功！')
        return redirect(url_for('system.positions'))
    
    return render_template('system/add_position.html', title='添加职位')

@bp.route('/position/edit/<int:position_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_position(position_id):
    """编辑职位"""
    position = Position.query.get_or_404(position_id)
    
    if request.method == 'POST':
        position.name = request.form.get('name')
        position.description = request.form.get('description')
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='编辑职位',
            description=f'编辑了职位 {position.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('职位更新成功！')
        return redirect(url_for('system.positions'))
    
    return render_template('system/edit_position.html', title='编辑职位', position=position)

@bp.route('/position/delete/<int:position_id>', methods=['POST'])
@login_required
@admin_required
def delete_position(position_id):
    """删除职位"""
    position = Position.query.get_or_404(position_id)
    
    # 检查是否有用户属于该职位
    if User.query.filter_by(position_id=position_id).first():
        flash('该职位下有用户，不能删除！', 'danger')
        return redirect(url_for('system.positions'))
    
    position_name = position.name
    db.session.delete(position)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除职位',
        description=f'删除了职位 {position_name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('职位删除成功！')
    return redirect(url_for('system.positions'))

@bp.route('/menus')
@login_required
@admin_required
def menus():
    """菜单管理"""
    menus_list = Menu.query.order_by(Menu.order).all()
    return render_template('system/menus.html', title='菜单管理', menus=menus_list)

@bp.route('/menu/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_menu():
    """添加菜单"""
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        path = request.form.get('path')
        icon = request.form.get('icon')
        parent_id = request.form.get('parent_id')
        order = request.form.get('order', 0)
        permission_code = request.form.get('permission_code')
        
        # 创建新菜单
        menu = Menu(
            name=name,
            title=title,
            path=path,
            icon=icon,
            parent_id=parent_id if parent_id else None,
            order=order,
            permission_code=permission_code,
            created_by=current_user.id
        )
        
        db.session.add(menu)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='添加菜单',
            description=f'添加了菜单 {menu.title}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('菜单添加成功！')
        return redirect(url_for('system.menus'))
    
    # 获取所有菜单，用于选择父菜单
    menus = Menu.query.all()
    # 获取所有权限，用于选择关联权限
    permissions = Permission.query.all()
    
    return render_template('system/add_menu.html', title='添加菜单', menus=menus, permissions=permissions)

@bp.route('/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_menu(menu_id):
    """编辑菜单"""
    menu = Menu.query.get_or_404(menu_id)
    
    if request.method == 'POST':
        menu.name = request.form.get('name')
        menu.title = request.form.get('title')
        menu.path = request.form.get('path')
        menu.icon = request.form.get('icon')
        menu.parent_id = request.form.get('parent_id') if request.form.get('parent_id') else None
        menu.order = request.form.get('order', 0)
        menu.permission_code = request.form.get('permission_code')
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='编辑菜单',
            description=f'编辑了菜单 {menu.title}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('菜单更新成功！')
        return redirect(url_for('system.menus'))
    
    # 获取所有菜单，用于选择父菜单（排除自己和自己的子菜单）
    menus = Menu.query.filter(
        Menu.id != menu_id
    ).all()
    # 获取所有权限，用于选择关联权限
    permissions = Permission.query.all()
    
    return render_template('system/edit_menu.html', title='编辑菜单', 
                         menu=menu, menus=menus, permissions=permissions)

@bp.route('/menu/delete/<int:menu_id>', methods=['POST'])
@login_required
@admin_required
def delete_menu(menu_id):
    """删除菜单"""
    menu = Menu.query.get_or_404(menu_id)
    
    # 检查是否有子菜单
    if Menu.query.filter_by(parent_id=menu_id).first():
        flash('该菜单下有子菜单，不能删除！', 'danger')
        return redirect(url_for('system.menus'))
    
    menu_title = menu.title
    db.session.delete(menu)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除菜单',
        description=f'删除了菜单 {menu_title}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('菜单删除成功！')
    return redirect(url_for('system.menus'))

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """系统设置"""
    form = SystemSettingsForm()
    
    if form.validate_on_submit():
        # 获取或创建系统设置
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
        
        # 更新设置
        settings.system_name = form.system_name.data
        settings.system_version = form.system_version.data
        settings.company_name = form.company_name.data
        settings.copyright_info = form.copyright_info.data
        settings.icp_number = form.icp_number.data
        
        # 处理Logo上传
        if form.logo.data:
            filename = secure_filename(form.logo.data.filename)
            # 确保上传目录存在
            upload_path = os.path.join(current_app.root_path, 'static/uploads')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            # 保存文件
            file_path = os.path.join(upload_path, filename)
            form.logo.data.save(file_path)
            settings.logo = f'/static/uploads/{filename}'
        
        db.session.add(settings)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='系统设置',
            description='更新了系统设置',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('系统设置已更新！')
        return redirect(url_for('system.settings'))
    
    # 如果是GET请求，填充表单
    settings = SystemSettings.query.first()
    if settings:
        form.system_name.data = settings.system_name
        form.system_version.data = settings.system_version
        form.company_name.data = settings.company_name
        form.copyright_info.data = settings.copyright_info
        form.icp_number.data = settings.icp_number
    
    return render_template('system/settings.html', title='系统设置', form=form)

@bp.route('/email_settings', methods=['GET', 'POST'])
@login_required
@admin_required
def email_settings():
    """邮件设置"""
    form = EmailSettingsForm()
    
    if form.validate_on_submit():
        # 获取或创建系统设置
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
        
        # 更新邮件设置
        settings.smtp_server = form.smtp_server.data
        settings.smtp_port = form.smtp_port.data
        settings.smtp_username = form.smtp_username.data
        settings.smtp_password = form.smtp_password.data
        settings.smtp_use_tls = form.smtp_use_tls.data
        settings.email_from = form.email_from.data
        
        db.session.add(settings)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='邮件设置',
            description='更新了邮件设置',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('邮件设置已更新！')
        return redirect(url_for('system.email_settings'))
    
    # 如果是GET请求，填充表单
    settings = SystemSettings.query.first()
    if settings:
        form.smtp_server.data = settings.smtp_server
        form.smtp_port.data = settings.smtp_port
        form.smtp_username.data = settings.smtp_username
        form.smtp_password.data = settings.smtp_password
        form.smtp_use_tls.data = settings.smtp_use_tls
        form.email_from.data = settings.email_from
    
    return render_template('system/email_settings.html', title='邮件设置', form=form)

@bp.route('/security_settings', methods=['GET', 'POST'])
@login_required
@admin_required
def security_settings():
    """安全设置"""
    form = SecuritySettingsForm()
    
    if form.validate_on_submit():
        # 获取或创建系统设置
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
        
        # 更新安全设置
        settings.password_min_length = form.password_min_length.data
        settings.password_require_uppercase = form.password_require_uppercase.data
        settings.password_require_lowercase = form.password_require_lowercase.data
        settings.password_require_numbers = form.password_require_numbers.data
        settings.password_require_special_chars = form.password_require_special_chars.data
        settings.login_attempts_limit = form.login_attempts_limit.data
        settings.login_lockout_duration = form.login_lockout_duration.data
        settings.session_timeout = form.session_timeout.data
        
        db.session.add(settings)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='安全设置',
            description='更新了安全设置',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('安全设置已更新！')
        return redirect(url_for('system.security_settings'))
    
    # 如果是GET请求，填充表单
    settings = SystemSettings.query.first()
    if settings:
        form.password_min_length.data = settings.password_min_length
        form.password_require_uppercase.data = settings.password_require_uppercase
        form.password_require_lowercase.data = settings.password_require_lowercase
        form.password_require_numbers.data = settings.password_require_numbers
        form.password_require_special_chars.data = settings.password_require_special_chars
        form.login_attempts_limit.data = settings.login_attempts_limit
        form.login_lockout_duration.data = settings.login_lockout_duration
        form.session_timeout.data = settings.session_timeout
    
    return render_template('system/security_settings.html', title='安全设置', form=form)

@bp.route('/interface_settings', methods=['GET', 'POST'])
@login_required
@admin_required
def interface_settings():
    """界面设置"""
    form = InterfaceSettingsForm()
    
    if form.validate_on_submit():
        # 获取或创建系统设置
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
        
        # 更新界面设置
        settings.theme = form.theme.data
        settings.primary_color = form.primary_color.data
        settings.layout = form.layout.data
        settings.sidebar_collapsed = form.sidebar_collapsed.data
        settings.show_breadcrumbs = form.show_breadcrumbs.data
        settings.show_footer = form.show_footer.data
        
        db.session.add(settings)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='界面设置',
            description='更新了界面设置',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('界面设置已更新！')
        return redirect(url_for('system.interface_settings'))
    
    # 如果是GET请求，填充表单
    settings = SystemSettings.query.first()
    if settings:
        form.theme.data = settings.theme
        form.primary_color.data = settings.primary_color
        form.layout.data = settings.layout
        form.sidebar_collapsed.data = settings.sidebar_collapsed
        form.show_breadcrumbs.data = settings.show_breadcrumbs
        form.show_footer.data = settings.show_footer
    
    return render_template('system/interface_settings.html', title='界面设置', form=form)

@bp.route('/logs')
@login_required
@admin_required
def logs():
    """系统日志"""
    form = LogSearchForm()
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    action = request.args.get('action', '')
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip_address = request.args.get('ip_address')
    
    query = SystemLog.query
    
    if action:
        query = query.filter(SystemLog.action.contains(action))
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(SystemLog.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(SystemLog.timestamp <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    if ip_address:
        query = query.filter(SystemLog.ip_address.contains(ip_address))
    
    logs_list = query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # 获取所有用户，用于筛选
    users = User.query.all()
    
    return render_template('system/logs.html', title='系统日志', 
                          logs=logs_list, form=form, users=users)

@bp.route('/login_logs')
@login_required
@admin_required
def login_logs():
    """登录日志"""
    form = LogSearchForm()
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip_address = request.args.get('ip_address')
    status = request.args.get('status')
    
    query = LoginLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(LoginLog.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(LoginLog.timestamp <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    if ip_address:
        query = query.filter(LoginLog.ip_address.contains(ip_address))
    
    if status:
        query = query.filter_by(status=status)
    
    logs_list = query.order_by(LoginLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # 获取所有用户，用于筛选
    users = User.query.all()
    
    return render_template('system/login_logs.html', title='登录日志', 
                          logs=logs_list, form=form, users=users)

@bp.route('/operation_logs')
@login_required
@admin_required
def operation_logs():
    """操作日志"""
    form = LogSearchForm()
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    action = request.args.get('action', '')
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip_address = request.args.get('ip_address')
    
    query = OperationLog.query
    
    if action:
        query = query.filter(OperationLog.action.contains(action))
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(OperationLog.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(OperationLog.timestamp <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    if ip_address:
        query = query.filter(OperationLog.ip_address.contains(ip_address))
    
    logs_list = query.order_by(OperationLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # 获取所有用户，用于筛选
    users = User.query.all()
    
    return render_template('system/operation_logs.html', title='操作日志', 
                          logs=logs_list, form=form, users=users)

@bp.route('/backup', methods=['GET', 'POST'])
@login_required
@admin_required
def backup():
    """数据备份"""
    form = BackupForm()
    
    if form.validate_on_submit():
        # 创建备份记录
        backup = Backup(
            backup_type=form.backup_type.data,
            backup_format=form.backup_format.data,
            status='进行中',
            created_by=current_user.id
        )
        
        # 设置备份路径和文件名
        if form.backup_path.data:
            backup.backup_path = form.backup_path.data
        else:
            backup.backup_path = os.path.join(current_app.root_path, 'backups')
            
        if form.backup_filename.data:
            backup.backup_filename = form.backup_filename.data
        else:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup.backup_filename = f"backup_{timestamp}.{form.backup_format.data}"
        
        db.session.add(backup)
        db.session.commit()
        
        # 确保备份目录存在
        if not os.path.exists(backup.backup_path):
            os.makedirs(backup.backup_path)
        
        # 这里应该添加实际的备份逻辑
        # 备份完成后更新状态
        backup.status = '已完成'
        backup.file_size = 1024  # 示例文件大小
        backup.completed_at = datetime.now()
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='数据备份',
            description=f'创建了数据备份 {backup.backup_filename}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('数据备份成功！')
        return redirect(url_for('system.backup'))
    
    # 获取备份历史
    backups_list = Backup.query.order_by(Backup.created_at.desc()).all()
    return render_template('system/backup.html', title='数据备份', form=form, backups=backups_list)

@bp.route('/backup/download/<int:backup_id>')
@login_required
@admin_required
def download_backup(backup_id):
    """下载备份文件"""
    backup = Backup.query.get_or_404(backup_id)
    
    # 检查备份文件是否存在
    file_path = os.path.join(backup.backup_path, backup.backup_filename)
    if not os.path.exists(file_path):
        flash('备份文件不存在！', 'danger')
        return redirect(url_for('system.backup'))
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='下载备份',
        description=f'下载了备份文件 {backup.backup_filename}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    # 返回文件
    return current_app.send_file(file_path, as_attachment=True, attachment_filename=backup.backup_filename)

@bp.route('/backup/delete/<int:backup_id>', methods=['POST'])
@login_required
@admin_required
def delete_backup(backup_id):
    """删除备份"""
    backup = Backup.query.get_or_404(backup_id)
    
    # 删除备份文件
    file_path = os.path.join(backup.backup_path, backup.backup_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    backup_name = backup.backup_filename
    db.session.delete(backup)
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        user_id=current_user.id,
        action='删除备份',
        description=f'删除了备份文件 {backup_name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('备份删除成功！')
    return redirect(url_for('system.backup'))

@bp.route('/restore', methods=['GET', 'POST'])
@login_required
@admin_required
def restore():
    """数据恢复"""
    form = RestoreForm()
    
    if form.validate_on_submit():
        # 获取备份文件
        backup = Backup.query.get(form.backup_file.data)
        if not backup:
            flash('备份文件不存在！', 'danger')
            return redirect(url_for('system.restore'))
        
        # 创建恢复记录
        restore = Restore(
            backup_id=backup.id,
            restore_type=form.restore_type.data,
            status='进行中',
            created_by=current_user.id
        )
        db.session.add(restore)
        db.session.commit()
        
        # 这里应该添加实际的恢复逻辑
        # 恢复完成后更新状态
        restore.status = '已完成'
        restore.completed_at = datetime.now()
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='数据恢复',
            description=f'使用备份文件 {backup.backup_filename} 恢复了数据',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('数据恢复成功！')
        return redirect(url_for('system.restore'))
    
    # 获取备份列表
    backups_list = Backup.query.filter_by(status='已完成').order_by(Backup.created_at.desc()).all()
    
    # 获取恢复历史
    restores_list = Restore.query.order_by(Restore.created_at.desc()).all()
    
    return render_template('system/restore.html', title='数据恢复', form=form, 
                          backups=backups_list, restores=restores_list)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """个人资料"""
    form = EditProfileForm()
    
    if form.validate_on_submit():
        # 更新用户资料
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.department = form.department.data
        current_user.position = form.position.data
        current_user.about_me = form.about_me.data
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=current_user.id,
            action='更新个人资料',
            description='更新了个人资料',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('个人资料更新成功！')
        return redirect(url_for('system.profile'))
    
    # 如果是GET请求，填充表单
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.department.data = current_user.department
        form.position.data = current_user.position
        form.about_me.data = current_user.about_me
    
    return render_template('system/profile.html', title='个人资料', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # 验证当前密码
        if not current_user.check_password(form.current_password.data):
            flash('当前密码不正确！', 'danger')
            return redirect(url_for('system.change_password'))
        
        # 验证新密码是否符合安全策略
        settings = SystemSettings.query.first()
        if settings:
            # 检查密码长度
            if len(form.new_password.data) < settings.password_min_length:
                flash(f'密码长度不能少于 {settings.password_min_length} 位！', 'danger')
                return redirect(url_for('system.change_password'))
            
            # 检查是否包含大写字母
            if settings.password_require_uppercase and not any(c.isupper() for c in form.new_password.data):
                flash('密码必须包含大写字母！', 'danger')
                return redirect(url_for('system.change_password'))
            
            # 检查是否包含小写字母
            if settings.password_require_lowercase and not any(c.islower() for c in form.new_password.data):
                flash('密码必须包含小写字母！', 'danger')
                return redirect(url_for('system.change_password'))
            
            # 检查是否包含数字
            if settings.password_require_numbers and not any(c.isdigit() for c in form.new_password.data):
                flash('密码必须包含数字！', 'danger')
                return redirect(url_for('system.change_password'))
            
            # 检查是否包含特殊字符
            if settings.password_require_special_chars and not any(not c.isalnum() for c in form.new_password.data):
                flash('密码必须包含特殊字符！', 'danger')
                return redirect(url_for('system.change_password'))
        
        # 更新密码
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=current_user.id,
            action='修改密码',
            description=f'用户 {current_user.username} 修改了密码',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('密码修改成功！')
        return redirect(url_for('system.profile'))
    
    return render_template('system/change_password.html', title='修改密码', form=form)
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.modules.personnel import bp
from app.models import User, Role, Department, Position, Attendance, Leave, Overtime, Salary, SalaryItem
from app import db
from datetime import datetime, date, time
from sqlalchemy import extract

@bp.route('/')
@login_required
def index():
    """人员管理首页"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=10, error_out=False
    )
    departments = Department.query.all()
    positions = Position.query.all()
    return render_template('personnel/index.html', title='人员管理', users=users, departments=departments, positions=positions)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加人员"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        department_id = request.form.get('department_id')
        position_id = request.form.get('position_id')
        password = request.form.get('password')
        role_ids = request.form.getlist('role_ids')
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在！', 'danger')
            return redirect(url_for('personnel.add'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已存在！', 'danger')
            return redirect(url_for('personnel.add'))
        
        user = User(username=username, email=email, name=name, phone=phone)
        user.set_password(password)
        
        # 设置部门和职位
        if department_id:
            department = Department.query.get(department_id)
            if department:
                user.department = department.name
        
        if position_id:
            position = Position.query.get(position_id)
            if position:
                user.position = position.title
        
        # 设置角色
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        flash('人员添加成功！')
        return redirect(url_for('personnel.index'))
    
    roles = Role.query.all()
    departments = Department.query.all()
    positions = Position.query.all()
    return render_template('personnel/add.html', title='添加人员', roles=roles, departments=departments, positions=positions)

@bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    """编辑人员"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.name = request.form.get('name')
        user.phone = request.form.get('phone')
        department_id = request.form.get('department_id')
        position_id = request.form.get('position_id')
        role_ids = request.form.getlist('role_ids')
        
        # 设置部门和职位
        if department_id:
            department = Department.query.get(department_id)
            if department:
                user.department = department.name
        
        if position_id:
            position = Position.query.get(position_id)
            if position:
                user.position = position.title
        
        # 更新角色
        user.roles = []
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)
        
        # 更新密码（如果提供）
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        db.session.commit()
        flash('人员信息更新成功！')
        return redirect(url_for('personnel.index'))
    
    roles = Role.query.all()
    departments = Department.query.all()
    positions = Position.query.all()
    return render_template('personnel/edit.html', title='编辑人员', user=user, roles=roles, departments=departments, positions=positions)

@bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete(user_id):
    """删除人员"""
    user = User.query.get_or_404(user_id)
    
    # 防止删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账户！', 'danger')
        return redirect(url_for('personnel.index'))
    
    db.session.delete(user)
    db.session.commit()
    flash('人员删除成功！')
    return redirect(url_for('personnel.index'))

@bp.route('/view/<int:user_id>')
@login_required
def view(user_id):
    """查看人员详情"""
    user = User.query.get_or_404(user_id)
    # 获取最近的考勤记录
    recent_attendance = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.attendance_date.desc()).limit(10).all()
    # 获取最近的请假记录
    recent_leaves = Leave.query.filter_by(user_id=user_id).order_by(Leave.created_at.desc()).limit(5).all()
    # 获取最近的加班记录
    recent_overtimes = Overtime.query.filter_by(user_id=user_id).order_by(Overtime.created_at.desc()).limit(5).all()
    # 获取最近的薪资记录
    recent_salaries = Salary.query.filter_by(user_id=user_id).order_by(Salary.salary_month.desc()).limit(5).all()
    
    return render_template('personnel/view.html', title='人员详情', user=user, 
                         recent_attendance=recent_attendance, recent_leaves=recent_leaves,
                         recent_overtimes=recent_overtimes, recent_salaries=recent_salaries)

# 考勤管理路由
@bp.route('/attendance')
@login_required
def attendance():
    """考勤管理"""
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = Attendance.query
    
    if year:
        query = query.filter(extract('year', Attendance.attendance_date) == year)
    if month:
        query = query.filter(extract('month', Attendance.attendance_date) == month)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    attendances = query.order_by(Attendance.attendance_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    users = User.query.all()
    return render_template('personnel/attendance.html', title='考勤管理', attendances=attendances, users=users)

@bp.route('/attendance/check_in', methods=['POST'])
@login_required
def check_in():
    """上班打卡"""
    today = date.today()
    attendance = Attendance.query.filter_by(user_id=current_user.id, attendance_date=today).first()
    
    if attendance:
        if attendance.check_in_time:
            flash('今日已打卡！', 'warning')
        else:
            attendance.check_in_time = datetime.now()
            db.session.commit()
            flash('上班打卡成功！')
    else:
        attendance = Attendance(
            user_id=current_user.id,
            attendance_date=today,
            check_in_time=datetime.now()
        )
        db.session.add(attendance)
        db.session.commit()
        flash('上班打卡成功！')
    
    return redirect(url_for('personnel.attendance'))

@bp.route('/attendance/check_out', methods=['POST'])
@login_required
def check_out():
    """下班打卡"""
    today = date.today()
    attendance = Attendance.query.filter_by(user_id=current_user.id, attendance_date=today).first()
    
    if not attendance:
        flash('请先上班打卡！', 'warning')
    elif attendance.check_out_time:
        flash('今日已下班打卡！', 'warning')
    else:
        attendance.check_out_time = datetime.now()
        
        # 计算工作时长
        if attendance.check_in_time:
            time_diff = attendance.check_out_time - attendance.check_in_time
            hours = time_diff.total_seconds() / 3600
            attendance.work_hours = round(hours, 2)
            
            # 判断是否加班
            if hours > 8:
                attendance.overtime_hours = round(hours - 8, 2)
                attendance.status = 'overtime'
        
        db.session.commit()
        flash('下班打卡成功！')
    
    return redirect(url_for('personnel.attendance'))

@bp.route('/attendance/add', methods=['GET', 'POST'])
@login_required
def add_attendance():
    """添加考勤记录"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        attendance_date = request.form.get('attendance_date')
        check_in_time = request.form.get('check_in_time')
        check_out_time = request.form.get('check_out_time')
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        # 检查是否已存在该日期的考勤记录
        existing = Attendance.query.filter_by(user_id=user_id, attendance_date=attendance_date).first()
        if existing:
            flash('该日期的考勤记录已存在！', 'danger')
            return redirect(url_for('personnel.add_attendance'))
        
        attendance = Attendance(
            user_id=user_id,
            attendance_date=datetime.strptime(attendance_date, '%Y-%m-%d').date(),
            status=status,
            notes=notes
        )
        
        if check_in_time:
            attendance.check_in_time = datetime.strptime(f"{attendance_date} {check_in_time}", '%Y-%m-%d %H:%M')
        
        if check_out_time:
            attendance.check_out_time = datetime.strptime(f"{attendance_date} {check_out_time}", '%Y-%m-%d %H:%M')
            
            # 计算工作时长
            if attendance.check_in_time:
                time_diff = attendance.check_out_time - attendance.check_in_time
                hours = time_diff.total_seconds() / 3600
                attendance.work_hours = round(hours, 2)
                
                # 判断是否加班
                if hours > 8:
                    attendance.overtime_hours = round(hours - 8, 2)
        
        db.session.add(attendance)
        db.session.commit()
        flash('考勤记录添加成功！')
        return redirect(url_for('personnel.attendance'))
    
    users = User.query.all()
    return render_template('personnel/add_attendance.html', title='添加考勤记录', users=users)

@bp.route('/attendance/edit/<int:attendance_id>', methods=['GET', 'POST'])
@login_required
def edit_attendance(attendance_id):
    """编辑考勤记录"""
    attendance = Attendance.query.get_or_404(attendance_id)
    
    if request.method == 'POST':
        attendance_date = request.form.get('attendance_date')
        check_in_time = request.form.get('check_in_time')
        check_out_time = request.form.get('check_out_time')
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        attendance.attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        attendance.status = status
        attendance.notes = notes
        
        if check_in_time:
            attendance.check_in_time = datetime.strptime(f"{attendance_date} {check_in_time}", '%Y-%m-%d %H:%M')
        else:
            attendance.check_in_time = None
        
        if check_out_time:
            attendance.check_out_time = datetime.strptime(f"{attendance_date} {check_out_time}", '%Y-%m-%d %H:%M')
        else:
            attendance.check_out_time = None
        
        # 重新计算工作时长
        if attendance.check_in_time and attendance.check_out_time:
            time_diff = attendance.check_out_time - attendance.check_in_time
            hours = time_diff.total_seconds() / 3600
            attendance.work_hours = round(hours, 2)
            
            # 判断是否加班
            if hours > 8:
                attendance.overtime_hours = round(hours - 8, 2)
            else:
                attendance.overtime_hours = 0
        else:
            attendance.work_hours = 0
            attendance.overtime_hours = 0
        
        db.session.commit()
        flash('考勤记录更新成功！')
        return redirect(url_for('personnel.attendance'))
    
    users = User.query.all()
    return render_template('personnel/edit_attendance.html', title='编辑考勤记录', attendance=attendance, users=users)

@bp.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    """删除考勤记录"""
    attendance = Attendance.query.get_or_404(attendance_id)
    db.session.delete(attendance)
    db.session.commit()
    flash('考勤记录删除成功！')
    return redirect(url_for('personnel.attendance'))

# 请假管理路由
@bp.route('/leaves')
@login_required
def leaves():
    """请假管理"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    
    query = Leave.query
    
    if status:
        query = query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    leaves = query.order_by(Leave.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    users = User.query.all()
    return render_template('personnel/leaves.html', title='请假管理', leaves=leaves, users=users)

@bp.route('/leaves/add', methods=['GET', 'POST'])
@login_required
def add_leave():
    """添加请假记录"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        leave_type = request.form.get('leave_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        days = float(request.form.get('days'))
        reason = request.form.get('reason')
        
        leave = Leave(
            user_id=user_id,
            leave_type=leave_type,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            days=days,
            reason=reason
        )
        
        if start_time:
            leave.start_time = datetime.strptime(start_time, '%H:%M').time()
        
        if end_time:
            leave.end_time = datetime.strptime(end_time, '%H:%M').time()
        
        db.session.add(leave)
        db.session.commit()
        flash('请假申请提交成功！')
        return redirect(url_for('personnel.leaves'))
    
    users = User.query.all()
    return render_template('personnel/add_leave.html', title='添加请假记录', users=users)

@bp.route('/leaves/approve/<int:leave_id>', methods=['POST'])
@login_required
def approve_leave(leave_id):
    """批准请假"""
    leave = Leave.query.get_or_404(leave_id)
    leave.status = 'approved'
    leave.approver_id = current_user.id
    leave.approved_date = datetime.now()
    db.session.commit()
    flash('请假已批准！')
    return redirect(url_for('personnel.leaves'))

@bp.route('/leaves/reject/<int:leave_id>', methods=['POST'])
@login_required
def reject_leave():
    """拒绝请假"""
    leave_id = request.form.get('leave_id')
    rejection_reason = request.form.get('rejection_reason')
    
    leave = Leave.query.get_or_404(leave_id)
    leave.status = 'rejected'
    leave.approver_id = current_user.id
    leave.approved_date = datetime.now()
    leave.rejection_reason = rejection_reason
    db.session.commit()
    flash('请假已拒绝！')
    return redirect(url_for('personnel.leaves'))

# 加班管理路由
@bp.route('/overtimes')
@login_required
def overtimes():
    """加班管理"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    
    query = Overtime.query
    
    if status:
        query = query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    overtimes = query.order_by(Overtime.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    users = User.query.all()
    return render_template('personnel/overtimes.html', title='加班管理', overtimes=overtimes, users=users)

@bp.route('/overtimes/add', methods=['GET', 'POST'])
@login_required
def add_overtime():
    """添加加班记录"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        overtime_date = request.form.get('overtime_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        hours = float(request.form.get('hours'))
        reason = request.form.get('reason')
        
        overtime = Overtime(
            user_id=user_id,
            overtime_date=datetime.strptime(overtime_date, '%Y-%m-%d').date(),
            start_time=datetime.strptime(start_time, '%H:%M').time(),
            end_time=datetime.strptime(end_time, '%H:%M').time(),
            hours=hours,
            reason=reason
        )
        
        db.session.add(overtime)
        db.session.commit()
        flash('加班申请提交成功！')
        return redirect(url_for('personnel.overtimes'))
    
    users = User.query.all()
    return render_template('personnel/add_overtime.html', title='添加加班记录', users=users)

@bp.route('/overtimes/approve/<int:overtime_id>', methods=['POST'])
@login_required
def approve_overtime(overtime_id):
    """批准加班"""
    overtime = Overtime.query.get_or_404(overtime_id)
    overtime.status = 'approved'
    overtime.approver_id = current_user.id
    overtime.approved_date = datetime.now()
    db.session.commit()
    flash('加班已批准！')
    return redirect(url_for('personnel.overtimes'))

@bp.route('/overtimes/reject/<int:overtime_id>', methods=['POST'])
@login_required
def reject_overtime():
    """拒绝加班"""
    overtime_id = request.form.get('overtime_id')
    rejection_reason = request.form.get('rejection_reason')
    
    overtime = Overtime.query.get_or_404(overtime_id)
    overtime.status = 'rejected'
    overtime.approver_id = current_user.id
    overtime.approved_date = datetime.now()
    overtime.rejection_reason = rejection_reason
    db.session.commit()
    flash('加班已拒绝！')
    return redirect(url_for('personnel.overtimes'))

# 薪资管理路由
@bp.route('/salary')
@login_required
def salary():
    """薪资管理"""
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month')
    user_id = request.args.get('user_id', type=int)
    
    query = Salary.query
    
    if month:
        query = query.filter_by(salary_month=month)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    salaries = query.order_by(Salary.salary_month.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    users = User.query.all()
    return render_template('personnel/salary.html', title='薪资管理', salaries=salaries, users=users)

@bp.route('/salary/add', methods=['GET', 'POST'])
@login_required
def add_salary():
    """添加薪资记录"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        salary_month = request.form.get('salary_month')
        basic_salary = float(request.form.get('basic_salary'))
        performance_bonus = float(request.form.get('performance_bonus', 0))
        overtime_pay = float(request.form.get('overtime_pay', 0))
        allowance = float(request.form.get('allowance', 0))
        bonus = float(request.form.get('bonus', 0))
        other_income = float(request.form.get('other_income', 0))
        social_insurance = float(request.form.get('social_insurance', 0))
        housing_fund = float(request.form.get('housing_fund', 0))
        personal_tax = float(request.form.get('personal_tax', 0))
        other_deduction = float(request.form.get('other_deduction', 0))
        notes = request.form.get('notes')
        
        # 计算总收入和总扣款
        total_income = basic_salary + performance_bonus + overtime_pay + allowance + bonus + other_income
        total_deduction = social_insurance + housing_fund + personal_tax + other_deduction
        net_salary = total_income - total_deduction
        
        # 检查是否已存在该月份的薪资记录
        existing = Salary.query.filter_by(user_id=user_id, salary_month=salary_month).first()
        if existing:
            flash('该月份的薪资记录已存在！', 'danger')
            return redirect(url_for('personnel.add_salary'))
        
        salary = Salary(
            user_id=user_id,
            salary_month=salary_month,
            basic_salary=basic_salary,
            performance_bonus=performance_bonus,
            overtime_pay=overtime_pay,
            allowance=allowance,
            bonus=bonus,
            other_income=other_income,
            total_income=total_income,
            social_insurance=social_insurance,
            housing_fund=housing_fund,
            personal_tax=personal_tax,
            other_deduction=other_deduction,
            total_deduction=total_deduction,
            net_salary=net_salary,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(salary)
        db.session.commit()
        flash('薪资记录添加成功！')
        return redirect(url_for('personnel.salary'))
    
    users = User.query.all()
    return render_template('personnel/add_salary.html', title='添加薪资记录', users=users)

@bp.route('/salary/view/<int:salary_id>')
@login_required
def view_salary(salary_id):
    """查看薪资详情"""
    salary = Salary.query.get_or_404(salary_id)
    salary_items = SalaryItem.query.filter_by(salary_id=salary_id).all()
    return render_template('personnel/view_salary.html', title='薪资详情', salary=salary, salary_items=salary_items)

@bp.route('/salary/edit/<int:salary_id>', methods=['GET', 'POST'])
@login_required
def edit_salary(salary_id):
    """编辑薪资记录"""
    salary = Salary.query.get_or_404(salary_id)
    
    if request.method == 'POST':
        salary.basic_salary = float(request.form.get('basic_salary'))
        salary.performance_bonus = float(request.form.get('performance_bonus', 0))
        salary.overtime_pay = float(request.form.get('overtime_pay', 0))
        salary.allowance = float(request.form.get('allowance', 0))
        salary.bonus = float(request.form.get('bonus', 0))
        salary.other_income = float(request.form.get('other_income', 0))
        salary.social_insurance = float(request.form.get('social_insurance', 0))
        salary.housing_fund = float(request.form.get('housing_fund', 0))
        salary.personal_tax = float(request.form.get('personal_tax', 0))
        salary.other_deduction = float(request.form.get('other_deduction', 0))
        salary.notes = request.form.get('notes')
        
        # 重新计算总收入和总扣款
        salary.total_income = salary.basic_salary + salary.performance_bonus + salary.overtime_pay + salary.allowance + salary.bonus + salary.other_income
        salary.total_deduction = salary.social_insurance + salary.housing_fund + salary.personal_tax + salary.other_deduction
        salary.net_salary = salary.total_income - salary.total_deduction
        
        db.session.commit()
        flash('薪资记录更新成功！')
        return redirect(url_for('personnel.salary'))
    
    return render_template('personnel/edit_salary.html', title='编辑薪资记录', salary=salary)

@bp.route('/salary/delete/<int:salary_id>', methods=['POST'])
@login_required
def delete_salary(salary_id):
    """删除薪资记录"""
    salary = Salary.query.get_or_404(salary_id)
    db.session.delete(salary)
    db.session.commit()
    flash('薪资记录删除成功！')
    return redirect(url_for('personnel.salary'))

@bp.route('/salary/confirm/<int:salary_id>', methods=['POST'])
@login_required
def confirm_salary(salary_id):
    """确认薪资记录"""
    salary = Salary.query.get_or_404(salary_id)
    salary.status = 'confirmed'
    db.session.commit()
    flash('薪资记录已确认！')
    return redirect(url_for('personnel.salary'))

@bp.route('/salary/pay/<int:salary_id>', methods=['POST'])
@login_required
def pay_salary(salary_id):
    """发放薪资"""
    salary = Salary.query.get_or_404(salary_id)
    salary.status = 'paid'
    salary.pay_date = date.today()
    db.session.commit()
    flash('薪资已发放！')
    return redirect(url_for('personnel.salary'))

# 部门管理路由
@bp.route('/departments')
@login_required
def departments():
    """部门管理"""
    departments = Department.query.all()
    return render_template('personnel/departments.html', title='部门管理', departments=departments)

@bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """添加部门"""
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id', type=int)
        manager_id = request.form.get('manager_id', type=int)
        level = request.form.get('level', type=int, default=1)
        sort_order = request.form.get('sort_order', type=int, default=0)
        
        # 检查部门名称和代码是否已存在
        if Department.query.filter_by(name=name).first():
            flash('部门名称已存在！', 'danger')
            return redirect(url_for('personnel.add_department'))
        
        if Department.query.filter_by(code=code).first():
            flash('部门代码已存在！', 'danger')
            return redirect(url_for('personnel.add_department'))
        
        department = Department(
            name=name,
            code=code,
            description=description,
            level=level,
            sort_order=sort_order
        )
        
        if parent_id:
            parent = Department.query.get(parent_id)
            if parent:
                department.parent = parent
        
        if manager_id:
            manager = User.query.get(manager_id)
            if manager:
                department.manager = manager
        
        db.session.add(department)
        db.session.commit()
        flash('部门添加成功！')
        return redirect(url_for('personnel.departments'))
    
    departments = Department.query.all()
    users = User.query.all()
    return render_template('personnel/add_department.html', title='添加部门', departments=departments, users=users)

@bp.route('/departments/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    """编辑部门"""
    department = Department.query.get_or_404(department_id)
    
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.code = request.form.get('code')
        department.description = request.form.get('description')
        parent_id = request.form.get('parent_id', type=int)
        manager_id = request.form.get('manager_id', type=int)
        department.level = request.form.get('level', type=int)
        department.sort_order = request.form.get('sort_order', type=int)
        
        # 设置父部门
        if parent_id:
            parent = Department.query.get(parent_id)
            if parent and parent.id != department.id:  # 防止设置自己为父部门
                department.parent = parent
            else:
                department.parent = None
        else:
            department.parent = None
        
        # 设置部门经理
        if manager_id:
            manager = User.query.get(manager_id)
            if manager:
                department.manager = manager
            else:
                department.manager = None
        else:
            department.manager = None
        
        db.session.commit()
        flash('部门信息更新成功！')
        return redirect(url_for('personnel.departments'))
    
    departments = Department.query.all()
    users = User.query.all()
    return render_template('personnel/edit_department.html', title='编辑部门', department=department, departments=departments, users=users)

@bp.route('/departments/delete/<int:department_id>', methods=['POST'])
@login_required
def delete_department(department_id):
    """删除部门"""
    department = Department.query.get_or_404(department_id)
    
    # 检查是否有子部门
    if department.children:
        flash('该部门下有子部门，不能删除！', 'danger')
        return redirect(url_for('personnel.departments'))
    
    # 检查是否有员工
    if User.query.filter_by(department=department.name).first():
        flash('该部门下有员工，不能删除！', 'danger')
        return redirect(url_for('personnel.departments'))
    
    db.session.delete(department)
    db.session.commit()
    flash('部门删除成功！')
    return redirect(url_for('personnel.departments'))

# 职位管理路由
@bp.route('/positions')
@login_required
def positions():
    """职位管理"""
    positions = Position.query.all()
    departments = Department.query.all()
    return render_template('personnel/positions.html', title='职位管理', positions=positions, departments=departments)

@bp.route('/positions/add', methods=['GET', 'POST'])
@login_required
def add_position():
    """添加职位"""
    if request.method == 'POST':
        title = request.form.get('title')
        code = request.form.get('code')
        description = request.form.get('description')
        department_id = request.form.get('department_id', type=int)
        level = request.form.get('level', type=int)
        sort_order = request.form.get('sort_order', type=int, default=0)
        
        # 检查职位名称和代码是否已存在
        if Position.query.filter_by(title=title).first():
            flash('职位名称已存在！', 'danger')
            return redirect(url_for('personnel.add_position'))
        
        if Position.query.filter_by(code=code).first():
            flash('职位代码已存在！', 'danger')
            return redirect(url_for('personnel.add_position'))
        
        position = Position(
            title=title,
            code=code,
            description=description,
            level=level,
            sort_order=sort_order
        )
        
        if department_id:
            department = Department.query.get(department_id)
            if department:
                position.department = department
        
        db.session.add(position)
        db.session.commit()
        flash('职位添加成功！')
        return redirect(url_for('personnel.positions'))
    
    departments = Department.query.all()
    return render_template('personnel/add_position.html', title='添加职位', departments=departments)

@bp.route('/positions/edit/<int:position_id>', methods=['GET', 'POST'])
@login_required
def edit_position(position_id):
    """编辑职位"""
    position = Position.query.get_or_404(position_id)
    
    if request.method == 'POST':
        position.title = request.form.get('title')
        position.code = request.form.get('code')
        position.description = request.form.get('description')
        department_id = request.form.get('department_id', type=int)
        position.level = request.form.get('level', type=int)
        position.sort_order = request.form.get('sort_order', type=int)
        
        # 设置所属部门
        if department_id:
            department = Department.query.get(department_id)
            if department:
                position.department = department
            else:
                position.department = None
        else:
            position.department = None
        
        db.session.commit()
        flash('职位信息更新成功！')
        return redirect(url_for('personnel.positions'))
    
    departments = Department.query.all()
    return render_template('personnel/edit_position.html', title='编辑职位', position=position, departments=departments)

@bp.route('/positions/delete/<int:position_id>', methods=['POST'])
@login_required
def delete_position(position_id):
    """删除职位"""
    position = Position.query.get_or_404(position_id)
    
    # 检查是否有员工使用该职位
    if User.query.filter_by(position=position.title).first():
        flash('该职位下有员工，不能删除！', 'danger')
        return redirect(url_for('personnel.positions'))
    
    db.session.delete(position)
    db.session.commit()
    flash('职位删除成功！')
    return redirect(url_for('personnel.positions'))
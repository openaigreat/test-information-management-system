from datetime import datetime
from app import db

class Attendance(db.Model):
    """考勤记录模型"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime)  # 上班打卡时间
    check_out_time = db.Column(db.DateTime)  # 下班打卡时间
    status = db.Column(db.String(20), default='normal')  # normal, late, early_leave, absent, leave, overtime
    work_hours = db.Column(db.Float, default=0.0)  # 工作小时数
    overtime_hours = db.Column(db.Float, default=0.0)  # 加班小时数
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='attendance_records')
    
    def __repr__(self):
        return f'<Attendance {self.id}>'

class Leave(db.Model):
    """请假记录模型"""
    __tablename__ = 'leave'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(32), nullable=False)  # 请假类型：事假、病假、年假、婚假等
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)  # 开始时间
    end_time = db.Column(db.Time)  # 结束时间
    days = db.Column(db.Float, nullable=False)  # 请假天数
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='leave_records')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_leaves')
    
    def __repr__(self):
        return f'<Leave {self.id}>'

class Overtime(db.Model):
    """加班记录模型"""
    __tablename__ = 'overtime'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    overtime_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    hours = db.Column(db.Float, nullable=False)  # 加班小时数
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='overtime_records')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_overtimes')
    
    def __repr__(self):
        return f'<Overtime {self.id}>'

class Salary(db.Model):
    """薪资记录模型"""
    __tablename__ = 'salary'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    salary_month = db.Column(db.String(7), nullable=False)  # 薪资月份，格式：YYYY-MM
    basic_salary = db.Column(db.Float, nullable=False)  # 基本工资
    performance_bonus = db.Column(db.Float, default=0.0)  # 绩效奖金
    overtime_pay = db.Column(db.Float, default=0.0)  # 加班费
    allowance = db.Column(db.Float, default=0.0)  # 津贴
    bonus = db.Column(db.Float, default=0.0)  # 奖金
    other_income = db.Column(db.Float, default=0.0)  # 其他收入
    total_income = db.Column(db.Float, nullable=False)  # 总收入
    social_insurance = db.Column(db.Float, default=0.0)  # 社保
    housing_fund = db.Column(db.Float, default=0.0)  # 公积金
    personal_tax = db.Column(db.Float, default=0.0)  # 个人所得税
    other_deduction = db.Column(db.Float, default=0.0)  # 其他扣款
    total_deduction = db.Column(db.Float, nullable=False)  # 总扣款
    net_salary = db.Column(db.Float, nullable=False)  # 实发工资
    pay_date = db.Column(db.Date)  # 发放日期
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, paid
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='salary_records')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_salaries')
    
    def __repr__(self):
        return f'<Salary {self.id}>'

class SalaryItem(db.Model):
    """薪资明细模型"""
    __tablename__ = 'salary_item'
    
    id = db.Column(db.Integer, primary_key=True)
    salary_id = db.Column(db.Integer, db.ForeignKey('salary.id'), nullable=False)
    item_type = db.Column(db.String(32), nullable=False)  # 明细类型：基本工资、绩效奖金、加班费等
    item_name = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_income = db.Column(db.Boolean, default=True)  # 是否为收入项
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    salary = db.relationship('Salary', backref='items')
    
    def __repr__(self):
        return f'<SalaryItem {self.id}>'

class Department(db.Model):
    """部门模型"""
    __tablename__ = 'department'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    level = db.Column(db.Integer, default=1)  # 部门层级
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    parent = db.relationship('Department', remote_side=[id], backref='children')
    manager = db.relationship('User', backref='managed_department')
    users = db.relationship('User', backref='department')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Position(db.Model):
    """职位模型"""
    __tablename__ = 'position'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    level = db.Column(db.Integer)  # 职位级别
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    department = db.relationship('Department', backref='positions')
    users = db.relationship('User', backref='position')
    
    def __repr__(self):
        return f'<Position {self.title}>'
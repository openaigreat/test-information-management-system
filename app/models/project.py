from datetime import datetime
from app import db

class Project(db.Model):
    """项目模型"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(32), nullable=False)  # 项目类型
    status = db.Column(db.String(20), default='planning')  # planning, active, on_hold, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    progress = db.Column(db.Integer, default=0)  # 进度百分比
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 关系
    tasks = db.relationship('Task', backref='project', lazy='dynamic')
    members = db.relationship('ProjectMember', backref='project', lazy='dynamic')
    documents = db.relationship('ProjectDocument', backref='project', lazy='dynamic')
    schedules = db.relationship('ProjectSchedule', backref='project', lazy='dynamic')
    accounting_records = db.relationship('ProjectAccounting', backref='project', lazy='dynamic')
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_projects')
    client = db.relationship('Customer', backref='projects')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_projects')
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Task(db.Model):
    """任务模型"""
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'))  # 父任务ID，用于任务层级
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, review, done, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    task_type = db.Column(db.String(32), default='task')  # task, bug, feature, improvement
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    progress = db.Column(db.Integer, default=0)  # 进度百分比
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    subtasks = db.relationship('Task', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_tasks')
    comments = db.relationship('TaskComment', backref='task', lazy='dynamic')
    attachments = db.relationship('TaskAttachment', backref='task', lazy='dynamic')
    
    def __repr__(self):
        return f'<Task {self.title}>'

class TaskComment(db.Model):
    """任务评论模型"""
    __tablename__ = 'task_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='task_comments')
    
    def __repr__(self):
        return f'<TaskComment {self.id}>'

class TaskAttachment(db.Model):
    """任务附件模型"""
    __tablename__ = 'task_attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='task_attachments')
    
    def __repr__(self):
        return f'<TaskAttachment {self.filename}>'

class ProjectMember(db.Model):
    """项目成员模型"""
    __tablename__ = 'project_member'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # 项目角色：项目经理、开发人员、测试人员等
    join_date = db.Column(db.Date)
    leave_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, inactive
    responsibilities = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='project_memberships')
    
    def __repr__(self):
        return f'<ProjectMember {self.id}>'

class ProjectDocument(db.Model):
    """项目文档模型"""
    __tablename__ = 'project_document'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    document_type = db.Column(db.String(32), nullable=False)  # 文档类型：需求文档、设计文档、测试文档等
    version = db.Column(db.String(20), default='1.0')
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    status = db.Column(db.String(20), default='draft')  # draft, review, approved, published, archived
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    uploader = db.relationship('User', backref='project_documents')
    
    def __repr__(self):
        return f'<ProjectDocument {self.title}>'

class ProjectSchedule(db.Model):
    """项目进度模型"""
    __tablename__ = 'project_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    progress = db.Column(db.Integer, default=0)  # 进度百分比
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed, delayed
    dependencies = db.Column(db.Text)  # 依赖关系，JSON格式存储
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    task = db.relationship('Task', backref='schedule')
    
    def __repr__(self):
        return f'<ProjectSchedule {self.title}>'

class ProjectAccounting(db.Model):
    """项目财务模型"""
    __tablename__ = 'project_accounting'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    record_type = db.Column(db.String(32), nullable=False)  # 记录类型：预算、支出、收入
    category = db.Column(db.String(64), nullable=False)  # 分类
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='CNY')
    record_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(100))  # 参考号
    invoice_number = db.Column(db.String(100))  # 发票号
    status = db.Column(db.String(20), default='planned')  # planned, actual, approved, paid
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='project_accounting_records')
    
    def __repr__(self):
        return f'<ProjectAccounting {self.id}>'
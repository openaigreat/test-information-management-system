from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# 导入模块化模型
from app.models.customer import Customer, Contact, Business, Communication
from app.models.finance import Account, Transaction, FinancialRecord
from app.models.inventory import Item, Stock, StockIn, StockOut, Purchase, PurchaseItem, Receive, ReceiveItem
from app.models.project import Project, Task, TaskComment, TaskAttachment, ProjectMember, ProjectDocument, ProjectSchedule, ProjectAccounting
from app.models.knowledge import KnowledgeCategory, KnowledgeArticle, KnowledgeComment, KnowledgeAttachment, KnowledgeFile, KnowledgeManual, KnowledgeGuide, KnowledgeInstruction
from app.models.personnel import Attendance, Leave, Overtime, Salary, SalaryItem, Department, Position

# 关联表
user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    users = db.relationship('User', secondary=user_role, backref=db.backref('roles', lazy='dynamic'))
    permissions = db.relationship('Permission', secondary=role_permission, backref=db.backref('roles', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    code = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    module = db.Column(db.String(64))
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(64))
    position = db.Column(db.String(64))
    avatar = db.Column(db.String(255))
    about_me = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission_code):
        for role in self.roles:
            if any(permission.code == permission_code for permission in role.permissions):
                return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(64))
    level = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(64))
    operation = db.Column(db.String(255))
    details = db.Column(db.Text)
    
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SystemLog {self.id}>'

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'

class Backup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    path = db.Column(db.String(255))
    size = db.Column(db.Integer)
    type = db.Column(db.String(64))
    format = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', backref=db.backref('backups', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Backup {self.filename}>'

class Restore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    backup_id = db.Column(db.Integer, db.ForeignKey('backup.id'))
    type = db.Column(db.String(64))
    status = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    backup = db.relationship('Backup', backref=db.backref('restores', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('restores', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Restore {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
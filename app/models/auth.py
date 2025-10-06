from app import db
from app.models.associations import role_permission

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    
    # 使用字符串引用Permission模型，避免循环导入
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
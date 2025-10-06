from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager
from app.models.associations import user_role

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
    
    # 使用字符串引用Role模型，避免循环导入
    roles = db.relationship('Role', secondary=user_role, backref=db.backref('users', lazy='dynamic'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        # 使用SQL查询检查用户是否有指定角色
        from app.models.auth import Role
        result = db.session.query(
            db.session.query(user_role).filter(
                user_role.c.user_id == self.id
            ).join(
                Role, user_role.c.role_id == Role.id
            ).filter(
                Role.name == role_name
            ).exists()
        ).scalar()
        return result
    
    def has_permission(self, permission_code):
        # 使用SQL查询检查用户是否有指定权限
        from app.models.auth import Role, Permission
        from app.models.associations import role_permission
        result = db.session.query(
            db.session.query(user_role).filter(
                user_role.c.user_id == self.id
            ).join(
                role_permission, user_role.c.role_id == role_permission.c.role_id
            ).join(
                Permission, role_permission.c.permission_id == Permission.id
            ).filter(
                Permission.code == permission_code
            ).exists()
        ).scalar()
        return result
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
from flask import Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # 基本配置
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    
    # 注册蓝图
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.modules.projects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix='/projects')
    
    from app.modules.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认角色和权限
        from app.models import Role, Permission
        from app.models.associations import role_permission
        
        # 检查是否已有权限数据
        if Permission.query.count() == 0:
            # 创建基本权限
            permissions = [
                Permission(name='查看系统', code='view_system', description='查看系统基本信息', module='system'),
                Permission(name='用户管理', code='manage_users', description='管理系统用户', module='system'),
                Permission(name='角色管理', code='manage_roles', description='管理系统角色', module='system'),
                Permission(name='权限管理', code='manage_permissions', description='管理系统权限', module='system'),
            ]
            
            for permission in permissions:
                db.session.add(permission)
            
            # 创建基本角色
            admin_role = Role(name='管理员', description='系统管理员')
            user_role = Role(name='普通用户', description='普通用户')
            
            db.session.add(admin_role)
            db.session.add(user_role)
            db.session.commit()
            
            # 为管理员角色分配所有权限
            for permission in permissions:
                admin_role.permissions.append(permission)
            
            # 为普通用户角色分配基本权限
            user_role.permissions.append(Permission.query.filter_by(code='view_system').first())
            
            db.session.commit()
    
    return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_admin import Admin
import os

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bootstrap = Bootstrap()
admin = Admin(template_mode='bootstrap3')

def create_app(config_class=None):
    app = Flask(__name__)
    
    # 加载配置
    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    admin.init_app(app)
    
    # 配置登录管理
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.modules.personnel import bp as personnel_bp
    app.register_blueprint(personnel_bp, url_prefix='/personnel')
    
    from app.modules.customers import bp as customers_bp
    app.register_blueprint(customers_bp, url_prefix='/customers')
    
    from app.modules.finance import bp as finance_bp
    app.register_blueprint(finance_bp, url_prefix='/finance')
    
    from app.modules.inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    
    from app.modules.projects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix='/projects')
    
    from app.modules.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    
    from app.modules.knowledge import bp as knowledge_bp
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    
    from app.modules.system import bp as system_bp
    app.register_blueprint(system_bp, url_prefix='/system')
    
    from app.modules.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
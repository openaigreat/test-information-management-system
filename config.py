import os
from dotenv import load_dotenv

# 加载环境变量
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'media')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    # 日志配置
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_FILE = os.path.join(basedir, 'logs', 'app.log')
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
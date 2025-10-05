from datetime import datetime
from app import db

class KnowledgeCategory(db.Model):
    """知识分类模型"""
    __tablename__ = 'knowledge_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id'))
    icon = db.Column(db.String(64))  # 分类图标
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    parent = db.relationship('KnowledgeCategory', remote_side=[id], backref='children')
    articles = db.relationship('KnowledgeArticle', backref='category', lazy='dynamic')
    files = db.relationship('KnowledgeFile', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<KnowledgeCategory {self.name}>'

class KnowledgeArticle(db.Model):
    """知识文章模型"""
    __tablename__ = 'knowledge_article'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)  # 摘要
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    like_count = db.Column(db.Integer, default=0)  # 点赞次数
    is_published = db.Column(db.Boolean, default=False)  # 是否发布
    is_top = db.Column(db.Boolean, default=False)  # 是否置顶
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    author = db.relationship('User', backref='knowledge_articles')
    comments = db.relationship('KnowledgeComment', backref='article', lazy='dynamic')
    attachments = db.relationship('KnowledgeAttachment', backref='article', lazy='dynamic')
    
    def __repr__(self):
        return f'<KnowledgeArticle {self.title}>'

class KnowledgeComment(db.Model):
    """知识评论模型"""
    __tablename__ = 'knowledge_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_article.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_comment.id'))  # 父评论ID，用于回复
    is_approved = db.Column(db.Boolean, default=True)  # 是否审核通过
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='knowledge_comments')
    parent = db.relationship('KnowledgeComment', remote_side=[id], backref='replies')
    
    def __repr__(self):
        return f'<KnowledgeComment {self.id}>'

class KnowledgeAttachment(db.Model):
    """知识附件模型"""
    __tablename__ = 'knowledge_attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_article.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    download_count = db.Column(db.Integer, default=0)  # 下载次数
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='knowledge_attachments')
    
    def __repr__(self):
        return f'<KnowledgeAttachment {self.filename}>'

class KnowledgeFile(db.Model):
    """知识文件模型"""
    __tablename__ = 'knowledge_file'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id'), nullable=False)
    file_type = db.Column(db.String(32), nullable=False)  # 文件类型：手册、指南、说明等
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    version = db.Column(db.String(20), default='1.0')
    download_count = db.Column(db.Integer, default=0)  # 下载次数
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    is_published = db.Column(db.Boolean, default=False)  # 是否发布
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    uploader = db.relationship('User', backref='knowledge_files')
    
    def __repr__(self):
        return f'<KnowledgeFile {self.title}>'

class KnowledgeManual(db.Model):
    """知识手册模型"""
    __tablename__ = 'knowledge_manual'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20), default='1.0')
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    download_count = db.Column(db.Integer, default=0)  # 下载次数
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    is_published = db.Column(db.Boolean, default=False)  # 是否发布
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='knowledge_manuals')
    
    def __repr__(self):
        return f'<KnowledgeManual {self.title}>'

class KnowledgeGuide(db.Model):
    """知识指南模型"""
    __tablename__ = 'knowledge_guide'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text)  # 步骤，JSON格式存储
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    difficulty = db.Column(db.String(20), default='medium')  # 难度：easy, medium, hard
    estimated_time = db.Column(db.String(32))  # 预估时间
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    is_published = db.Column(db.Boolean, default=False)  # 是否发布
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='knowledge_guides')
    
    def __repr__(self):
        return f'<KnowledgeGuide {self.title}>'

class KnowledgeInstruction(db.Model):
    """知识说明模型"""
    __tablename__ = 'knowledge_instruction'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    download_count = db.Column(db.Integer, default=0)  # 下载次数
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    is_published = db.Column(db.Boolean, default=False)  # 是否发布
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='knowledge_instructions')
    
    def __repr__(self):
        return f'<KnowledgeInstruction {self.title}>'
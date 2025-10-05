from datetime import datetime
from app import db

class Customer(db.Model):
    """客户模型"""
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    industry = db.Column(db.String(64))
    company_size = db.Column(db.String(64))
    website = db.Column(db.String(255))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, inactive, potential
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 关系
    contacts = db.relationship('CustomerContact', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    businesses = db.relationship('CustomerBusiness', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    communications = db.relationship('CustomerCommunication', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class CustomerContact(db.Model):
    """客户联系人模型"""
    __tablename__ = 'customer_contact'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(64))
    department = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    wechat = db.Column(db.String(64))
    notes = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomerContact {self.name}>'

class CustomerBusiness(db.Model):
    """客户业务往来模型"""
    __tablename__ = 'customer_business'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    business_type = db.Column(db.String(64), nullable=False)  # 业务类型
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='CNY')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='planning')  # planning, ongoing, completed, cancelled
    responsible_person = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    responsible = db.relationship('User', backref='businesses')
    
    def __repr__(self):
        return f'<CustomerBusiness {self.title}>'

class CustomerCommunication(db.Model):
    """客户沟通过程模型"""
    __tablename__ = 'customer_communication'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('customer_contact.id'))
    communication_type = db.Column(db.String(64), nullable=False)  # 沟通类型：电话、邮件、会议等
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    next_step = db.Column(db.Text)
    communication_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer)  # 沟通时长（分钟）
    location = db.Column(db.String(255))  # 沟通地点
    participants = db.Column(db.Text)  # 参与人员，JSON格式存储
    outcome = db.Column(db.Text)  # 沟通结果
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    contact = db.relationship('CustomerContact')
    creator = db.relationship('User', backref='communications')
    
    def __repr__(self):
        return f'<CustomerCommunication {self.title}>'
from datetime import datetime
from app import db

class Account(db.Model):
    """账户模型"""
    __tablename__ = 'account'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(64), unique=True)
    account_type = db.Column(db.String(32), nullable=False)  # 账户类型：现金、银行账户、支付宝等
    bank_name = db.Column(db.String(100))
    bank_branch = db.Column(db.String(100))
    currency = db.Column(db.String(10), default='CNY')
    initial_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, inactive, closed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 关系
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')
    
    def __repr__(self):
        return f'<Account {self.name}>'

class Transaction(db.Model):
    """交易记录模型"""
    __tablename__ = 'transaction'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    transaction_type = db.Column(db.String(32), nullable=False)  # 交易类型：收入、支出、转账
    category = db.Column(db.String(64), nullable=False)  # 交易类别
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='CNY')
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    notes = db.Column(db.Text)
    reference_number = db.Column(db.String(100))  # 参考号
    related_transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))  # 关联交易（如转账）
    status = db.Column(db.String(20), default='completed')  # pending, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    related_transaction = db.relationship('Transaction', remote_side=[id], backref='related_transactions')
    creator = db.relationship('User', backref='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.id}>'

class FinancialRecord(db.Model):
    """财务记录模型"""
    __tablename__ = 'financial_record'
    
    id = db.Column(db.Integer, primary_key=True)
    record_type = db.Column(db.String(32), nullable=False)  # 记录类型：发票、收据、报销单等
    record_number = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='CNY')
    record_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)  # 到期日
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, paid, cancelled
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    category = db.Column(db.String(64))
    payment_method = db.Column(db.String(32))  # 付款方式
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partially_paid, paid
    paid_amount = db.Column(db.Float, default=0.0)
    paid_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    attachment_path = db.Column(db.String(255))  # 附件路径
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    customer = db.relationship('Customer', backref='financial_records')
    project = db.relationship('Project', backref='financial_records')
    creator = db.relationship('User', backref='financial_records')
    
    def __repr__(self):
        return f'<FinancialRecord {self.record_number}>'
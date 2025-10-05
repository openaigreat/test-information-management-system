from datetime import datetime
from app import db

class Item(db.Model):
    """物品模型"""
    __tablename__ = 'item'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(64), nullable=False)
    specification = db.Column(db.String(255))
    unit = db.Column(db.String(32), nullable=False)  # 单位
    brand = db.Column(db.String(64))
    model = db.Column(db.String(64))
    supplier = db.Column(db.String(100))
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    min_stock = db.Column(db.Integer, default=0)  # 最小库存
    max_stock = db.Column(db.Integer, default=0)  # 最大库存
    current_stock = db.Column(db.Integer, default=0)  # 当前库存
    status = db.Column(db.String(20), default='active')  # active, inactive, discontinued
    location = db.Column(db.String(100))  # 存放位置
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 关系
    stock_records = db.relationship('Stock', backref='item', lazy='dynamic')
    stock_in_records = db.relationship('StockIn', backref='item', lazy='dynamic')
    stock_out_records = db.relationship('StockOut', backref='item', lazy='dynamic')
    purchase_items = db.relationship('PurchaseItem', backref='item', lazy='dynamic')
    receive_items = db.relationship('ReceiveItem', backref='item', lazy='dynamic')
    
    def __repr__(self):
        return f'<Item {self.name}>'

class Stock(db.Model):
    """库存模型"""
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    warehouse = db.Column(db.String(100), nullable=False)  # 仓库
    location = db.Column(db.String(100))  # 库位
    batch_number = db.Column(db.String(64))  # 批次号
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    production_date = db.Column(db.Date)  # 生产日期
    expiry_date = db.Column(db.Date)  # 过期日期
    status = db.Column(db.String(20), default='normal')  # normal, reserved, damaged, expired
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Stock {self.id}>'

class StockIn(db.Model):
    """入库记录模型"""
    __tablename__ = 'stock_in'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    stock_in_date = db.Column(db.DateTime, default=datetime.utcnow)
    stock_in_type = db.Column(db.String(32), nullable=False)  # 入库类型：采购、退货、生产等
    supplier = db.Column(db.String(100))
    reference_number = db.Column(db.String(100))  # 参考号
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='stock_in_records')
    
    def __repr__(self):
        return f'<StockIn {self.id}>'

class StockOut(db.Model):
    """出库记录模型"""
    __tablename__ = 'stock_out'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    stock_out_date = db.Column(db.DateTime, default=datetime.utcnow)
    stock_out_type = db.Column(db.String(32), nullable=False)  # 出库类型：领用、销售、报废等
    recipient = db.Column(db.String(100))  # 领用人
    department = db.Column(db.String(64))  # 领用部门
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    reference_number = db.Column(db.String(100))  # 参考号
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    project = db.relationship('Project', backref='stock_out_records')
    creator = db.relationship('User', backref='stock_out_records')
    
    def __repr__(self):
        return f'<StockOut {self.id}>'

class Purchase(db.Model):
    """采购记录模型"""
    __tablename__ = 'purchase'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_number = db.Column(db.String(64), unique=True)
    purchase_date = db.Column(db.Date, nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(64))
    contact_phone = db.Column(db.String(20))
    total_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='CNY')
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, ordered, received, cancelled
    expected_date = db.Column(db.Date)  # 预计到货日期
    received_date = db.Column(db.Date)  # 实际到货日期
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partially_paid, paid
    payment_method = db.Column(db.String(32))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    items = db.relationship('PurchaseItem', backref='purchase', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='purchases')
    
    def __repr__(self):
        return f'<Purchase {self.purchase_number}>'

class PurchaseItem(db.Model):
    """采购明细模型"""
    __tablename__ = 'purchase_item'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    received_quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, partially_received, fully_received
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<PurchaseItem {self.id}>'

class Receive(db.Model):
    """领用记录模型"""
    __tablename__ = 'receive'
    
    id = db.Column(db.Integer, primary_key=True)
    receive_number = db.Column(db.String(64), unique=True)
    receive_date = db.Column(db.Date, nullable=False)
    receive_type = db.Column(db.String(32), nullable=False)  # 领用类型：部门领用、项目领用、个人领用等
    department = db.Column(db.String(64))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    recipient = db.Column(db.String(64), nullable=False)
    purpose = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    items = db.relationship('ReceiveItem', backref='receive', lazy='dynamic', cascade='all, delete-orphan')
    project = db.relationship('Project', backref='receives')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_receives')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_receives')
    
    def __repr__(self):
        return f'<Receive {self.receive_number}>'

class ReceiveItem(db.Model):
    """领用明细模型"""
    __tablename__ = 'receive_item'
    
    id = db.Column(db.Integer, primary_key=True)
    receive_id = db.Column(db.Integer, db.ForeignKey('receive.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ReceiveItem {self.id}>'
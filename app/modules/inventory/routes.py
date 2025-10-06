from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.modules.inventory import bp
from app.models import Item, Stock, StockIn, StockOut, Purchase, PurchaseItem, Receive, ReceiveItem
from app import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """物品管理首页"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Item.query
    
    if keyword:
        query = query.filter(
            Item.name.contains(keyword) | 
            Item.code.contains(keyword) | 
            Item.specification.contains(keyword)
        )
    
    if category:
        query = query.filter_by(category=category)
    
    if status:
        query = query.filter_by(status=status)
    
    items = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有类别和状态用于筛选
    categories = db.session.query(Item.category).distinct().all()
    statuses = db.session.query(Item.status).distinct().all()
    
    # 计算统计信息
    total_items = Item.query.count()
    total_stock = db.session.query(db.func.sum(Stock.quantity)).scalar() or 0
    total_value = db.session.query(db.func.sum(Item.price * Stock.quantity)).join(Stock, Item.id == Stock.item_id).scalar() or 0
    
    return render_template('inventory/index.html', title='物品管理', 
                         items=items, categories=categories, statuses=statuses,
                         total_items=total_items, total_stock=total_stock, total_value=total_value)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加物品"""
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        category = request.form.get('category')
        specification = request.form.get('specification')
        unit = request.form.get('unit')
        price = float(request.form.get('price', 0))
        min_stock = int(request.form.get('min_stock', 0))
        max_stock = int(request.form.get('max_stock', 0))
        supplier = request.form.get('supplier')
        description = request.form.get('description')
        notes = request.form.get('notes')
        
        # 检查物品名称和代码是否已存在
        if Item.query.filter_by(name=name).first():
            flash('物品名称已存在！', 'danger')
            return redirect(url_for('inventory.add'))
        
        if code and Item.query.filter_by(code=code).first():
            flash('物品代码已存在！', 'danger')
            return redirect(url_for('inventory.add'))
        
        item = Item(
            name=name,
            code=code,
            category=category,
            specification=specification,
            unit=unit,
            price=price,
            min_stock=min_stock,
            max_stock=max_stock,
            supplier=supplier,
            description=description,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        # 创建库存记录
        stock = Stock(
            item_id=item.id,
            quantity=0,
            created_by=current_user.id
        )
        db.session.add(stock)
        db.session.commit()
        
        flash('物品添加成功！')
        return redirect(url_for('inventory.index'))
    
    return render_template('inventory/add.html', title='添加物品')

@bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    """编辑物品"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.code = request.form.get('code')
        item.category = request.form.get('category')
        item.specification = request.form.get('specification')
        item.unit = request.form.get('unit')
        item.price = float(request.form.get('price', 0))
        item.min_stock = int(request.form.get('min_stock', 0))
        item.max_stock = int(request.form.get('max_stock', 0))
        item.supplier = request.form.get('supplier')
        item.description = request.form.get('description')
        item.status = request.form.get('status')
        item.notes = request.form.get('notes')
        
        db.session.commit()
        flash('物品信息更新成功！')
        return redirect(url_for('inventory.index'))
    
    return render_template('inventory/edit.html', title='编辑物品', item=item)

@bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete(item_id):
    """删除物品"""
    item = Item.query.get_or_404(item_id)
    
    # 检查是否有关联的库存记录
    stock = Stock.query.filter_by(item_id=item_id).first()
    if stock and stock.quantity > 0:
        flash('该物品有库存，不能删除！', 'danger')
        return redirect(url_for('inventory.index'))
    
    # 删除相关库存记录
    Stock.query.filter_by(item_id=item_id).delete()
    # 删除相关入库记录
    StockIn.query.filter_by(item_id=item_id).delete()
    # 删除相关出库记录
    StockOut.query.filter_by(item_id=item_id).delete()
    # 删除相关采购明细
    PurchaseItem.query.filter_by(item_id=item_id).delete()
    # 删除相关领用明细
    ReceiveItem.query.filter_by(item_id=item_id).delete()
    
    db.session.delete(item)
    db.session.commit()
    flash('物品删除成功！')
    return redirect(url_for('inventory.index'))

@bp.route('/view/<int:item_id>')
@login_required
def view(item_id):
    """查看物品详情"""
    item = Item.query.get_or_404(item_id)
    stock = Stock.query.filter_by(item_id=item_id).first()
    
    # 获取最近的入库记录
    recent_stock_in = StockIn.query.filter_by(item_id=item_id).order_by(
        StockIn.stock_in_date.desc()).limit(5).all()
    
    # 获取最近的出库记录
    recent_stock_out = StockOut.query.filter_by(item_id=item_id).order_by(
        StockOut.stock_out_date.desc()).limit(5).all()
    
    return render_template('inventory/view.html', title='物品详情', item=item, 
                         stock=stock, recent_stock_in=recent_stock_in, 
                         recent_stock_out=recent_stock_out)

@bp.route('/stock')
@login_required
def stock():
    """库存管理"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category')
    stock_status = request.args.get('stock_status')
    
    query = db.session.query(Item, Stock).join(Stock, Item.id == Stock.item_id)
    
    if keyword:
        query = query.filter(
            Item.name.contains(keyword) | 
            Item.code.contains(keyword) | 
            Item.specification.contains(keyword)
        )
    
    if category:
        query = query.filter(Item.category == category)
    
    if stock_status == 'low':
        query = query.filter(Stock.quantity <= Item.min_stock)
    elif stock_status == 'high':
        query = query.filter(Stock.quantity >= Item.max_stock)
    
    stocks = query.order_by(Item.name).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有类别用于筛选
    categories = db.session.query(Item.category).distinct().all()
    
    # 统计库存状态
    total_items = Item.query.count()
    low_stock_items = db.session.query(db.func.count(Stock.id)).join(Item).filter(
        Stock.quantity <= Item.min_stock
    ).scalar()
    out_of_stock_items = db.session.query(db.func.count(Stock.id)).filter(
        Stock.quantity == 0
    ).scalar()
    
    stock_summary = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items
    }
    
    return render_template('inventory/stock.html', title='库存管理', 
                         stocks=stocks, categories=categories, stock_summary=stock_summary)

@bp.route('/stock/in', methods=['GET', 'POST'])
@login_required
def stock_in():
    """物品入库"""
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity = int(request.form.get('quantity', 0))
        stock_in_date = request.form.get('stock_in_date')
        batch_number = request.form.get('batch_number')
        supplier = request.form.get('supplier')
        notes = request.form.get('notes')
        
        if quantity <= 0:
            flash('入库数量必须大于0！', 'danger')
            return redirect(url_for('inventory.stock_in'))
        
        item = Item.query.get_or_404(item_id)
        stock = Stock.query.filter_by(item_id=item_id).first()
        
        if not stock:
            stock = Stock(
                item_id=item_id,
                quantity=0,
                created_by=current_user.id
            )
            db.session.add(stock)
        
        # 创建入库记录
        stock_in = StockIn(
            item_id=item_id,
            quantity=quantity,
            stock_in_date=datetime.strptime(stock_in_date, '%Y-%m-%d').date(),
            batch_number=batch_number,
            supplier=supplier,
            notes=notes,
            created_by=current_user.id
        )
        
        # 更新库存
        stock.quantity += quantity
        
        db.session.add(stock_in)
        db.session.commit()
        flash('物品入库成功！')
        return redirect(url_for('inventory.stock'))
    
    items = Item.query.filter_by(status='active').all()
    return render_template('inventory/stock_in.html', title='物品入库', items=items)

@bp.route('/stock/out', methods=['GET', 'POST'])
@login_required
def stock_out():
    """物品出库"""
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity = int(request.form.get('quantity', 0))
        stock_out_date = request.form.get('stock_out_date')
        receiver = request.form.get('receiver')
        purpose = request.form.get('purpose')
        notes = request.form.get('notes')
        
        if quantity <= 0:
            flash('出库数量必须大于0！', 'danger')
            return redirect(url_for('inventory.stock_out'))
        
        item = Item.query.get_or_404(item_id)
        stock = Stock.query.filter_by(item_id=item_id).first()
        
        if not stock or stock.quantity < quantity:
            flash('库存不足，无法出库！', 'danger')
            return redirect(url_for('inventory.stock_out'))
        
        # 创建出库记录
        stock_out = StockOut(
            item_id=item_id,
            quantity=quantity,
            stock_out_date=datetime.strptime(stock_out_date, '%Y-%m-%d').date(),
            receiver=receiver,
            purpose=purpose,
            notes=notes,
            created_by=current_user.id
        )
        
        # 更新库存
        stock.quantity -= quantity
        
        db.session.add(stock_out)
        db.session.commit()
        flash('物品出库成功！')
        return redirect(url_for('inventory.stock'))
    
    items = Item.query.filter_by(status='active').all()
    return render_template('inventory/stock_out.html', title='物品出库', items=items)

@bp.route('/stock/in/history')
@login_required
def stock_in_history():
    """入库历史记录"""
    page = request.args.get('page', 1, type=int)
    item_id = request.args.get('item_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = StockIn.query
    
    if item_id:
        query = query.filter_by(item_id=item_id)
    
    if start_date:
        query = query.filter(StockIn.stock_in_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(StockIn.stock_in_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    stock_ins = query.order_by(StockIn.stock_in_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    items = Item.query.all()
    return render_template('inventory/stock_in_history.html', title='入库历史', 
                         stock_ins=stock_ins, items=items)

@bp.route('/stock/out/history')
@login_required
def stock_out_history():
    """出库历史记录"""
    page = request.args.get('page', 1, type=int)
    item_id = request.args.get('item_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = StockOut.query
    
    if item_id:
        query = query.filter_by(item_id=item_id)
    
    if start_date:
        query = query.filter(StockOut.stock_out_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(StockOut.stock_out_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    stock_outs = query.order_by(StockOut.stock_out_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    items = Item.query.all()
    return render_template('inventory/stock_out_history.html', title='出库历史', 
                         stock_outs=stock_outs, items=items)

@bp.route('/purchase')
@login_required
def purchase():
    """采购记录"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    supplier = request.args.get('supplier')
    
    query = Purchase.query
    
    if status:
        query = query.filter_by(status=status)
    
    if supplier:
        query = query.filter(Purchase.supplier.contains(supplier))
    
    purchases = query.order_by(Purchase.purchase_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('inventory/purchase.html', title='采购记录', purchases=purchases)

@bp.route('/purchase/add', methods=['GET', 'POST'])
@login_required
def add_purchase():
    """添加采购记录"""
    if request.method == 'POST':
        purchase_number = request.form.get('purchase_number')
        supplier = request.form.get('supplier')
        purchase_date = request.form.get('purchase_date')
        total_amount = float(request.form.get('total_amount', 0))
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        # 检查采购单号是否已存在
        if Purchase.query.filter_by(purchase_number=purchase_number).first():
            flash('采购单号已存在！', 'danger')
            return redirect(url_for('inventory.add_purchase'))
        
        purchase = Purchase(
            purchase_number=purchase_number,
            supplier=supplier,
            purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d').date(),
            total_amount=total_amount,
            status=status,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(purchase)
        db.session.commit()
        flash('采购记录添加成功！')
        return redirect(url_for('inventory.purchase'))
    
    return render_template('inventory/add_purchase.html', title='添加采购记录')

@bp.route('/purchase/view/<int:purchase_id>')
@login_required
def view_purchase(purchase_id):
    """查看采购记录详情"""
    purchase = Purchase.query.get_or_404(purchase_id)
    purchase_items = PurchaseItem.query.filter_by(purchase_id=purchase_id).all()
    return render_template('inventory/view_purchase.html', title='采购记录详情', 
                         purchase=purchase, purchase_items=purchase_items)

@bp.route('/receive')
@login_required
def receive():
    """领用记录"""
    page = request.args.get('page', 1, type=int)
    receiver = request.args.get('receiver')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Receive.query
    
    if receiver:
        query = query.filter(Receive.receiver.contains(receiver))
    
    if start_date:
        query = query.filter(Receive.receive_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(Receive.receive_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    receives = query.order_by(Receive.receive_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('inventory/receive.html', title='领用记录', receives=receives)

@bp.route('/receive/add', methods=['GET', 'POST'])
@login_required
def add_receive():
    """添加领用记录"""
    if request.method == 'POST':
        receive_number = request.form.get('receive_number')
        receiver = request.form.get('receiver')
        department = request.form.get('department')
        receive_date = request.form.get('receive_date')
        purpose = request.form.get('purpose')
        notes = request.form.get('notes')
        
        # 检查领用单号是否已存在
        if Receive.query.filter_by(receive_number=receive_number).first():
            flash('领用单号已存在！', 'danger')
            return redirect(url_for('inventory.add_receive'))
        
        receive = Receive(
            receive_number=receive_number,
            receiver=receiver,
            department=department,
            receive_date=datetime.strptime(receive_date, '%Y-%m-%d').date(),
            purpose=purpose,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(receive)
        db.session.commit()
        flash('领用记录添加成功！')
        return redirect(url_for('inventory.receive'))
    
    return render_template('inventory/add_receive.html', title='添加领用记录')

@bp.route('/receive/view/<int:receive_id>')
@login_required
def view_receive(receive_id):
    """查看领用记录详情"""
    receive = Receive.query.get_or_404(receive_id)
    receive_items = ReceiveItem.query.filter_by(receive_id=receive_id).all()
    return render_template('inventory/view_receive.html', title='领用记录详情', 
                         receive=receive, receive_items=receive_items)
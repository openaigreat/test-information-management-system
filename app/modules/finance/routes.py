from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.modules.finance import bp
from app.models import Account, Transaction, FinancialRecord
from app import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """资金管理首页"""
    page = request.args.get('page', 1, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    record_type = request.args.get('type')
    
    query = FinancialRecord.query
    
    if start_date:
        query = query.filter(FinancialRecord.record_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(FinancialRecord.record_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    if record_type:
        query = query.filter_by(record_type=record_type)
    
    records = query.order_by(FinancialRecord.record_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取汇总数据
    total_income = db.session.query(db.func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.record_type == 'income'
    ).scalar() or 0
    
    total_expense = db.session.query(db.func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.record_type == 'expense'
    ).scalar() or 0
    
    balance = total_income - total_expense
    
    summary = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    }
    
    return render_template('finance/index.html', title='资金管理', 
                         records=records, summary=summary)

@bp.route('/accounts')
@login_required
def accounts():
    """账户管理"""
    page = request.args.get('page', 1, type=int)
    accounts = Account.query.order_by(Account.name).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 计算所有账户总余额
    total_balance = db.session.query(db.func.sum(Account.balance)).scalar() or 0
    
    return render_template('finance/accounts.html', title='账户管理', 
                         accounts=accounts, total_balance=total_balance)

@bp.route('/accounts/add', methods=['GET', 'POST'])
@login_required
def add_account():
    """添加账户"""
    if request.method == 'POST':
        name = request.form.get('name')
        account_number = request.form.get('account_number')
        account_type = request.form.get('account_type')
        bank_name = request.form.get('bank_name')
        currency = request.form.get('currency')
        initial_balance = float(request.form.get('initial_balance', 0))
        notes = request.form.get('notes')
        
        # 检查账户名称是否已存在
        if Account.query.filter_by(name=name).first():
            flash('账户名称已存在！', 'danger')
            return redirect(url_for('finance.add_account'))
        
        # 检查账号是否已存在
        if account_number and Account.query.filter_by(account_number=account_number).first():
            flash('账号已存在！', 'danger')
            return redirect(url_for('finance.add_account'))
        
        account = Account(
            name=name,
            account_number=account_number,
            account_type=account_type,
            bank_name=bank_name,
            currency=currency,
            balance=initial_balance,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(account)
        db.session.commit()
        flash('账户添加成功！')
        return redirect(url_for('finance.accounts'))
    
    return render_template('finance/add_account.html', title='添加账户')

@bp.route('/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    """编辑账户"""
    account = Account.query.get_or_404(account_id)
    
    if request.method == 'POST':
        account.name = request.form.get('name')
        account.account_number = request.form.get('account_number')
        account.account_type = request.form.get('account_type')
        account.bank_name = request.form.get('bank_name')
        account.currency = request.form.get('currency')
        account.notes = request.form.get('notes')
        account.status = request.form.get('status')
        
        db.session.commit()
        flash('账户信息更新成功！')
        return redirect(url_for('finance.accounts'))
    
    return render_template('finance/edit_account.html', title='编辑账户', account=account)

@bp.route('/accounts/delete/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    """删除账户"""
    account = Account.query.get_or_404(account_id)
    
    # 检查是否有关联的交易记录
    if Transaction.query.filter_by(account_id=account_id).first():
        flash('该账户有关联的交易记录，不能删除！', 'danger')
        return redirect(url_for('finance.accounts'))
    
    db.session.delete(account)
    db.session.commit()
    flash('账户删除成功！')
    return redirect(url_for('finance.accounts'))

@bp.route('/transactions')
@login_required
def transactions():
    """交易记录"""
    page = request.args.get('page', 1, type=int)
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    
    query = Transaction.query
    
    if account_id:
        query = query.filter_by(account_id=account_id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    transactions = query.order_by(Transaction.transaction_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有账户用于筛选
    accounts = Account.query.all()
    
    return render_template('finance/transactions.html', title='交易记录', 
                         transactions=transactions, accounts=accounts)

@bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """添加交易记录"""
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        transaction_type = request.form.get('transaction_type')
        amount = float(request.form.get('amount', 0))
        transaction_date = request.form.get('transaction_date')
        description = request.form.get('description')
        reference_number = request.form.get('reference_number')
        counterparty = request.form.get('counterparty')
        notes = request.form.get('notes')
        
        account = Account.query.get_or_404(account_id)
        
        transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            transaction_date=datetime.strptime(transaction_date, '%Y-%m-%d').date(),
            description=description,
            reference_number=reference_number,
            counterparty=counterparty,
            notes=notes,
            created_by=current_user.id
        )
        
        # 更新账户余额
        if transaction_type == 'deposit':
            account.balance += amount
        elif transaction_type == 'withdrawal':
            account.balance -= amount
        
        db.session.add(transaction)
        db.session.commit()
        flash('交易记录添加成功！')
        return redirect(url_for('finance.transactions'))
    
    accounts = Account.query.filter_by(status='active').all()
    return render_template('finance/add_transaction.html', title='添加交易记录', accounts=accounts)

@bp.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """编辑交易记录"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if request.method == 'POST':
        old_amount = transaction.amount
        old_type = transaction.transaction_type
        
        transaction.account_id = request.form.get('account_id')
        transaction.transaction_type = request.form.get('transaction_type')
        transaction.amount = float(request.form.get('amount', 0))
        transaction.transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date()
        transaction.description = request.form.get('description')
        transaction.reference_number = request.form.get('reference_number')
        transaction.counterparty = request.form.get('counterparty')
        transaction.notes = request.form.get('notes')
        
        account = Account.query.get_or_404(transaction.account_id)
        
        # 更新账户余额
        if old_type == 'deposit':
            account.balance -= old_amount
        elif old_type == 'withdrawal':
            account.balance += old_amount
        
        if transaction.transaction_type == 'deposit':
            account.balance += transaction.amount
        elif transaction.transaction_type == 'withdrawal':
            account.balance -= transaction.amount
        
        db.session.commit()
        flash('交易记录更新成功！')
        return redirect(url_for('finance.transactions'))
    
    accounts = Account.query.filter_by(status='active').all()
    return render_template('finance/edit_transaction.html', title='编辑交易记录', 
                         transaction=transaction, accounts=accounts)

@bp.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """删除交易记录"""
    transaction = Transaction.query.get_or_404(transaction_id)
    account = Account.query.get_or_404(transaction.account_id)
    
    # 更新账户余额
    if transaction.transaction_type == 'deposit':
        account.balance -= transaction.amount
    elif transaction.transaction_type == 'withdrawal':
        account.balance += transaction.amount
    
    db.session.delete(transaction)
    db.session.commit()
    flash('交易记录删除成功！')
    return redirect(url_for('finance.transactions'))

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加资金记录"""
    if request.method == 'POST':
        record_type = request.form.get('record_type')
        amount = float(request.form.get('amount', 0))
        record_date = request.form.get('record_date')
        category = request.form.get('category')
        description = request.form.get('description')
        account_id = request.form.get('account_id')
        reference_number = request.form.get('reference_number')
        notes = request.form.get('notes')
        
        record = FinancialRecord(
            record_type=record_type,
            amount=amount,
            record_date=datetime.strptime(record_date, '%Y-%m-%d').date(),
            category=category,
            description=description,
            account_id=account_id,
            reference_number=reference_number,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(record)
        db.session.commit()
        flash('资金记录添加成功！')
        return redirect(url_for('finance.index'))
    
    accounts = Account.query.filter_by(status='active').all()
    return render_template('finance/add.html', title='添加资金记录', accounts=accounts)

@bp.route('/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    """编辑资金记录"""
    record = FinancialRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        record.record_type = request.form.get('record_type')
        record.amount = float(request.form.get('amount', 0))
        record.record_date = datetime.strptime(request.form.get('record_date'), '%Y-%m-%d').date()
        record.category = request.form.get('category')
        record.description = request.form.get('description')
        record.account_id = request.form.get('account_id')
        record.reference_number = request.form.get('reference_number')
        record.notes = request.form.get('notes')
        
        db.session.commit()
        flash('资金记录更新成功！')
        return redirect(url_for('finance.index'))
    
    accounts = Account.query.filter_by(status='active').all()
    return render_template('finance/edit.html', title='编辑资金记录', 
                         record=record, accounts=accounts)

@bp.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete(record_id):
    """删除资金记录"""
    record = FinancialRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('资金记录删除成功！')
    return redirect(url_for('finance.index'))

@bp.route('/view/<int:record_id>')
@login_required
def view(record_id):
    """查看资金记录详情"""
    record = FinancialRecord.query.get_or_404(record_id)
    return render_template('finance/view.html', title='资金记录详情', record=record)

@bp.route('/summary')
@login_required
def summary():
    """资金汇总"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = FinancialRecord.query
    
    if start_date:
        query = query.filter(FinancialRecord.record_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(FinancialRecord.record_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # 获取汇总数据
    total_income = db.session.query(db.func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.record_type == 'income'
    ).scalar() or 0
    
    total_expense = db.session.query(db.func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.record_type == 'expense'
    ).scalar() or 0
    
    balance = total_income - total_expense
    
    # 按类别统计收入
    income_by_category = db.session.query(
        FinancialRecord.category,
        db.func.sum(FinancialRecord.amount).label('total')
    ).filter(
        FinancialRecord.record_type == 'income'
    ).group_by(FinancialRecord.category).all()
    
    # 按类别统计支出
    expense_by_category = db.session.query(
        FinancialRecord.category,
        db.func.sum(FinancialRecord.amount).label('total')
    ).filter(
        FinancialRecord.record_type == 'expense'
    ).group_by(FinancialRecord.category).all()
    
    # 按月份统计
    monthly_stats = db.session.query(
        db.func.strftime('%Y-%m', FinancialRecord.record_date).label('month'),
        db.func.sum(
            db.case(
                [(FinancialRecord.record_type == 'income', FinancialRecord.amount)],
                else_=0
            )
        ).label('income'),
        db.func.sum(
            db.case(
                [(FinancialRecord.record_type == 'expense', FinancialRecord.amount)],
                else_=0
            )
        ).label('expense')
    ).group_by(
        db.func.strftime('%Y-%m', FinancialRecord.record_date)
    ).order_by(
        db.func.strftime('%Y-%m', FinancialRecord.record_date).desc()
    ).limit(12).all()
    
    summary_data = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'income_by_category': income_by_category,
        'expense_by_category': expense_by_category,
        'monthly_stats': monthly_stats
    }
    
    return render_template('finance/summary.html', title='资金汇总', summary=summary_data)
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.modules.customers import bp
from app.models import Customer, CustomerContact, CustomerBusiness, CustomerCommunication
from app import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """客户管理首页"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Customer.query
    
    if keyword:
        query = query.filter(
            Customer.name.contains(keyword) | 
            Customer.code.contains(keyword) | 
            Customer.contact_person.contains(keyword) |
            Customer.phone.contains(keyword) |
            Customer.email.contains(keyword)
        )
    
    if category:
        query = query.filter_by(category=category)
    
    if status:
        query = query.filter_by(status=status)
    
    customers = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有类别和状态用于筛选
    categories = db.session.query(Customer.category).distinct().all()
    statuses = db.session.query(Customer.status).distinct().all()
    
    return render_template('customers/index.html', title='客户管理', 
                         customers=customers, categories=categories, statuses=statuses)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加客户"""
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        category = request.form.get('category')
        level = request.form.get('level')
        source = request.form.get('source')
        industry = request.form.get('industry')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')
        website = request.form.get('website')
        address = request.form.get('address')
        country = request.form.get('country')
        province = request.form.get('province')
        city = request.form.get('city')
        district = request.form.get('district')
        postal_code = request.form.get('postal_code')
        registration_number = request.form.get('registration_number')
        tax_number = request.form.get('tax_number')
        bank_name = request.form.get('bank_name')
        bank_account = request.form.get('bank_account')
        credit_rating = request.form.get('credit_rating')
        credit_limit = float(request.form.get('credit_limit', 0))
        payment_terms = request.form.get('payment_terms')
        notes = request.form.get('notes')
        
        # 检查客户名称和代码是否已存在
        if Customer.query.filter_by(name=name).first():
            flash('客户名称已存在！', 'danger')
            return redirect(url_for('customers.add'))
        
        if code and Customer.query.filter_by(code=code).first():
            flash('客户代码已存在！', 'danger')
            return redirect(url_for('customers.add'))
        
        customer = Customer(
            name=name,
            code=code,
            category=category,
            level=level,
            source=source,
            industry=industry,
            contact_person=contact_person,
            phone=phone,
            email=email,
            website=website,
            address=address,
            country=country,
            province=province,
            city=city,
            district=district,
            postal_code=postal_code,
            registration_number=registration_number,
            tax_number=tax_number,
            bank_name=bank_name,
            bank_account=bank_account,
            credit_rating=credit_rating,
            credit_limit=credit_limit,
            payment_terms=payment_terms,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(customer)
        db.session.commit()
        flash('客户添加成功！')
        return redirect(url_for('customers.index'))
    
    return render_template('customers/add.html', title='添加客户')

@bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    """编辑客户"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.code = request.form.get('code')
        customer.category = request.form.get('category')
        customer.level = request.form.get('level')
        customer.source = request.form.get('source')
        customer.industry = request.form.get('industry')
        customer.contact_person = request.form.get('contact_person')
        customer.phone = request.form.get('phone')
        customer.email = request.form.get('email')
        customer.website = request.form.get('website')
        customer.address = request.form.get('address')
        customer.country = request.form.get('country')
        customer.province = request.form.get('province')
        customer.city = request.form.get('city')
        customer.district = request.form.get('district')
        customer.postal_code = request.form.get('postal_code')
        customer.registration_number = request.form.get('registration_number')
        customer.tax_number = request.form.get('tax_number')
        customer.bank_name = request.form.get('bank_name')
        customer.bank_account = request.form.get('bank_account')
        customer.credit_rating = request.form.get('credit_rating')
        customer.credit_limit = float(request.form.get('credit_limit', 0))
        customer.payment_terms = request.form.get('payment_terms')
        customer.status = request.form.get('status')
        customer.notes = request.form.get('notes')
        
        db.session.commit()
        flash('客户信息更新成功！')
        return redirect(url_for('customers.index'))
    
    return render_template('customers/edit.html', title='编辑客户', customer=customer)

@bp.route('/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete(customer_id):
    """删除客户"""
    customer = Customer.query.get_or_404(customer_id)
    
    # 检查是否有关联的业务记录
    if CustomerBusiness.query.filter_by(customer_id=customer_id).first():
        flash('该客户有关联的业务记录，不能删除！', 'danger')
        return redirect(url_for('customers.index'))
    
    # 删除相关联系人
    CustomerContact.query.filter_by(customer_id=customer_id).delete()
    # 删除相关沟通记录
    CustomerCommunication.query.filter_by(customer_id=customer_id).delete()
    
    db.session.delete(customer)
    db.session.commit()
    flash('客户删除成功！')
    return redirect(url_for('customers.index'))

@bp.route('/view/<int:customer_id>')
@login_required
def view(customer_id):
    """查看客户详情"""
    customer = Customer.query.get_or_404(customer_id)
    # 获取客户联系人
    contacts = CustomerContact.query.filter_by(customer_id=customer_id).all()
    # 获取最近的业务往来
    recent_business = CustomerBusiness.query.filter_by(customer_id=customer_id).order_by(CustomerBusiness.business_date.desc()).limit(5).all()
    # 获取最近的沟通记录
    recent_communications = CustomerCommunication.query.filter_by(customer_id=customer_id).order_by(CustomerCommunication.communication_date.desc()).limit(5).all()
    
    return render_template('customers/view.html', title='客户详情', customer=customer,
                         contacts=contacts, recent_business=recent_business,
                         recent_communications=recent_communications)

# 客户联系人管理路由
@bp.route('/contacts/<int:customer_id>')
@login_required
def contacts(customer_id):
    """查看客户联系人"""
    customer = Customer.query.get_or_404(customer_id)
    contacts = CustomerContact.query.filter_by(customer_id=customer_id).all()
    return render_template('customers/contacts.html', title='客户联系人', customer=customer, contacts=contacts)

@bp.route('/contacts/add/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def add_contact(customer_id):
    """添加客户联系人"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        department = request.form.get('department')
        phone = request.form.get('phone')
        email = request.form.get('email')
        wechat = request.form.get('wechat')
        qq = request.form.get('qq')
        notes = request.form.get('notes')
        is_primary = 'is_primary' in request.form
        
        contact = CustomerContact(
            customer_id=customer_id,
            name=name,
            position=position,
            department=department,
            phone=phone,
            email=email,
            wechat=wechat,
            qq=qq,
            notes=notes,
            is_primary=is_primary
        )
        
        # 如果设为主要联系人，先将该客户其他联系人设为非主要
        if is_primary:
            CustomerContact.query.filter_by(customer_id=customer_id).update({'is_primary': False})
        
        db.session.add(contact)
        db.session.commit()
        flash('联系人添加成功！')
        return redirect(url_for('customers.contacts', customer_id=customer_id))
    
    return render_template('customers/add_contact.html', title='添加联系人', customer=customer)

@bp.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    """编辑客户联系人"""
    contact = CustomerContact.query.get_or_404(contact_id)
    customer = Customer.query.get_or_404(contact.customer_id)
    
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.position = request.form.get('position')
        contact.department = request.form.get('department')
        contact.phone = request.form.get('phone')
        contact.email = request.form.get('email')
        contact.wechat = request.form.get('wechat')
        contact.qq = request.form.get('qq')
        contact.notes = request.form.get('notes')
        is_primary = 'is_primary' in request.form
        
        # 如果设为主要联系人，先将该客户其他联系人设为非主要
        if is_primary and not contact.is_primary:
            CustomerContact.query.filter_by(customer_id=contact.customer_id).update({'is_primary': False})
        
        contact.is_primary = is_primary
        
        db.session.commit()
        flash('联系人信息更新成功！')
        return redirect(url_for('customers.contacts', customer_id=contact.customer_id))
    
    return render_template('customers/edit_contact.html', title='编辑联系人', contact=contact, customer=customer)

@bp.route('/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    """删除客户联系人"""
    contact = CustomerContact.query.get_or_404(contact_id)
    customer_id = contact.customer_id
    
    db.session.delete(contact)
    db.session.commit()
    flash('联系人删除成功！')
    return redirect(url_for('customers.contacts', customer_id=customer_id))

# 客户业务往来管理路由
@bp.route('/business/<int:customer_id>')
@login_required
def business(customer_id):
    """查看客户业务往来"""
    customer = Customer.query.get_or_404(customer_id)
    page = request.args.get('page', 1, type=int)
    
    business_records = CustomerBusiness.query.filter_by(customer_id=customer_id).order_by(
        CustomerBusiness.business_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('customers/business.html', title='业务往来', 
                         customer=customer, business_records=business_records)

@bp.route('/business/add/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def add_business(customer_id):
    """添加客户业务往来"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        business_type = request.form.get('business_type')
        business_date = request.form.get('business_date')
        amount = float(request.form.get('amount', 0))
        currency = request.form.get('currency')
        description = request.form.get('description')
        notes = request.form.get('notes')
        
        business = CustomerBusiness(
            customer_id=customer_id,
            business_type=business_type,
            business_date=datetime.strptime(business_date, '%Y-%m-%d').date(),
            amount=amount,
            currency=currency,
            description=description,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(business)
        db.session.commit()
        flash('业务记录添加成功！')
        return redirect(url_for('customers.business', customer_id=customer_id))
    
    return render_template('customers/add_business.html', title='添加业务记录', customer=customer)

@bp.route('/business/edit/<int:business_id>', methods=['GET', 'POST'])
@login_required
def edit_business(business_id):
    """编辑客户业务往来"""
    business = CustomerBusiness.query.get_or_404(business_id)
    customer = Customer.query.get_or_404(business.customer_id)
    
    if request.method == 'POST':
        business.business_type = request.form.get('business_type')
        business.business_date = datetime.strptime(request.form.get('business_date'), '%Y-%m-%d').date()
        business.amount = float(request.form.get('amount', 0))
        business.currency = request.form.get('currency')
        business.description = request.form.get('description')
        business.notes = request.form.get('notes')
        
        db.session.commit()
        flash('业务记录更新成功！')
        return redirect(url_for('customers.business', customer_id=business.customer_id))
    
    return render_template('customers/edit_business.html', title='编辑业务记录', business=business, customer=customer)

@bp.route('/business/delete/<int:business_id>', methods=['POST'])
@login_required
def delete_business(business_id):
    """删除客户业务往来"""
    business = CustomerBusiness.query.get_or_404(business_id)
    customer_id = business.customer_id
    
    db.session.delete(business)
    db.session.commit()
    flash('业务记录删除成功！')
    return redirect(url_for('customers.business', customer_id=customer_id))

# 客户沟通过程管理路由
@bp.route('/communication/<int:customer_id>')
@login_required
def communication(customer_id):
    """查看客户沟通过程"""
    customer = Customer.query.get_or_404(customer_id)
    page = request.args.get('page', 1, type=int)
    
    communications = CustomerCommunication.query.filter_by(customer_id=customer_id).order_by(
        CustomerCommunication.communication_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('customers/communication.html', title='沟通过程', 
                         customer=customer, communications=communications)

@bp.route('/communication/add/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def add_communication(customer_id):
    """添加客户沟通过程"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        communication_type = request.form.get('communication_type')
        communication_date = request.form.get('communication_date')
        contact_person = request.form.get('contact_person')
        subject = request.form.get('subject')
        content = request.form.get('content')
        next_follow_up = request.form.get('next_follow_up')
        notes = request.form.get('notes')
        
        communication = CustomerCommunication(
            customer_id=customer_id,
            communication_type=communication_type,
            communication_date=datetime.strptime(communication_date, '%Y-%m-%d').date(),
            contact_person=contact_person,
            subject=subject,
            content=content,
            next_follow_up=datetime.strptime(next_follow_up, '%Y-%m-%d').date() if next_follow_up else None,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(communication)
        db.session.commit()
        flash('沟通记录添加成功！')
        return redirect(url_for('customers.communication', customer_id=customer_id))
    
    contacts = CustomerContact.query.filter_by(customer_id=customer_id).all()
    return render_template('customers/add_communication.html', title='添加沟通记录', 
                         customer=customer, contacts=contacts)

@bp.route('/communication/edit/<int:communication_id>', methods=['GET', 'POST'])
@login_required
def edit_communication(communication_id):
    """编辑客户沟通过程"""
    communication = CustomerCommunication.query.get_or_404(communication_id)
    customer = Customer.query.get_or_404(communication.customer_id)
    
    if request.method == 'POST':
        communication.communication_type = request.form.get('communication_type')
        communication.communication_date = datetime.strptime(request.form.get('communication_date'), '%Y-%m-%d').date()
        communication.contact_person = request.form.get('contact_person')
        communication.subject = request.form.get('subject')
        communication.content = request.form.get('content')
        next_follow_up = request.form.get('next_follow_up')
        communication.next_follow_up = datetime.strptime(next_follow_up, '%Y-%m-%d').date() if next_follow_up else None
        communication.notes = request.form.get('notes')
        
        db.session.commit()
        flash('沟通记录更新成功！')
        return redirect(url_for('customers.communication', customer_id=communication.customer_id))
    
    contacts = CustomerContact.query.filter_by(customer_id=customer_id).all()
    return render_template('customers/edit_communication.html', title='编辑沟通记录', 
                         communication=communication, customer=customer, contacts=contacts)

@bp.route('/communication/delete/<int:communication_id>', methods=['POST'])
@login_required
def delete_communication(communication_id):
    """删除客户沟通过程"""
    communication = CustomerCommunication.query.get_or_404(communication_id)
    customer_id = communication.customer_id
    
    db.session.delete(communication)
    db.session.commit()
    flash('沟通记录删除成功！')
    return redirect(url_for('customers.communication', customer_id=customer_id))
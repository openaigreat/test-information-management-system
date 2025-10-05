from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.modules.knowledge import bp
from app.models import KnowledgeCategory, KnowledgeArticle, KnowledgeComment, KnowledgeAttachment, KnowledgeFile, KnowledgeManual, KnowledgeGuide, KnowledgeInstruction
from app import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """知识库首页"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id')
    keyword = request.args.get('keyword', '')
    
    query = KnowledgeArticle.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            KnowledgeArticle.title.contains(keyword) | 
            KnowledgeArticle.content.contains(keyword)
        )
    
    articles = query.order_by(KnowledgeArticle.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    
    return render_template('knowledge/index.html', title='知识库', 
                         categories=categories, articles=articles)

@bp.route('/files')
@login_required
def files():
    """网盘"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id')
    keyword = request.args.get('keyword', '')
    
    query = KnowledgeFile.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            KnowledgeFile.name.contains(keyword) | 
            KnowledgeFile.description.contains(keyword)
        )
    
    files = query.order_by(KnowledgeFile.upload_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    
    return render_template('knowledge/files.html', title='网盘', 
                         categories=categories, files=files)

@bp.route('/manuals')
@login_required
def manuals():
    """设备手册"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id')
    keyword = request.args.get('keyword', '')
    
    query = KnowledgeManual.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            KnowledgeManual.title.contains(keyword) | 
            KnowledgeManual.content.contains(keyword)
        )
    
    manuals = query.order_by(KnowledgeManual.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    
    return render_template('knowledge/manuals.html', title='设备手册', 
                         categories=categories, manuals=manuals)

@bp.route('/guides')
@login_required
def guides():
    """操作指导"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id')
    keyword = request.args.get('keyword', '')
    
    query = KnowledgeGuide.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            KnowledgeGuide.title.contains(keyword) | 
            KnowledgeGuide.content.contains(keyword)
        )
    
    guides = query.order_by(KnowledgeGuide.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    
    return render_template('knowledge/guides.html', title='操作指导', 
                         categories=categories, guides=guides)

@bp.route('/instructions')
@login_required
def instructions():
    """说明书"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id')
    keyword = request.args.get('keyword', '')
    
    query = KnowledgeInstruction.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            KnowledgeInstruction.title.contains(keyword) | 
            KnowledgeInstruction.content.contains(keyword)
        )
    
    instructions = query.order_by(KnowledgeInstruction.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    
    return render_template('knowledge/instructions.html', title='说明书', 
                         categories=categories, instructions=instructions)

@bp.route('/category/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """添加知识库分类"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        
        # 检查分类名称是否已存在
        if KnowledgeCategory.query.filter_by(name=name).first():
            flash('分类名称已存在！', 'danger')
            return redirect(url_for('knowledge.add_category'))
        
        category = KnowledgeCategory(
            name=name,
            description=description,
            parent_id=parent_id if parent_id else None,
            created_by=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        flash('分类添加成功！')
        return redirect(url_for('knowledge.index'))
    
    # 获取所有分类，用于选择父分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/add_category.html', title='添加分类', categories=categories)

@bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """编辑知识库分类"""
    category = KnowledgeCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.parent_id = request.form.get('parent_id') if request.form.get('parent_id') else None
        
        db.session.commit()
        flash('分类更新成功！')
        return redirect(url_for('knowledge.index'))
    
    # 获取所有分类，用于选择父分类（排除自己和自己的子分类）
    categories = KnowledgeCategory.query.filter(
        KnowledgeCategory.id != category_id
    ).all()
    
    return render_template('knowledge/edit_category.html', title='编辑分类', 
                         category=category, categories=categories)

@bp.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    """删除知识库分类"""
    category = KnowledgeCategory.query.get_or_404(category_id)
    
    # 检查是否有子分类
    if KnowledgeCategory.query.filter_by(parent_id=category_id).first():
        flash('该分类下有子分类，不能删除！', 'danger')
        return redirect(url_for('knowledge.index'))
    
    # 检查是否有相关文章
    if KnowledgeArticle.query.filter_by(category_id=category_id).first():
        flash('该分类下有文章，不能删除！', 'danger')
        return redirect(url_for('knowledge.index'))
    
    db.session.delete(category)
    db.session.commit()
    flash('分类删除成功！')
    return redirect(url_for('knowledge.index'))

@bp.route('/article/add', methods=['GET', 'POST'])
@login_required
def add_article():
    """添加知识库文章"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        tags = request.form.get('tags')
        status = request.form.get('status')
        
        article = KnowledgeArticle(
            title=title,
            content=content,
            category_id=category_id,
            tags=tags,
            status=status,
            created_by=current_user.id
        )
        
        db.session.add(article)
        db.session.commit()
        flash('文章添加成功！')
        return redirect(url_for('knowledge.index'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/add_article.html', title='添加文章', categories=categories)

@bp.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    """编辑知识库文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.category_id = request.form.get('category_id')
        article.tags = request.form.get('tags')
        article.status = request.form.get('status')
        
        db.session.commit()
        flash('文章更新成功！')
        return redirect(url_for('knowledge.view_article', article_id=article_id))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/edit_article.html', title='编辑文章', 
                         article=article, categories=categories)

@bp.route('/article/delete/<int:article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
    """删除知识库文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    
    # 删除相关评论
    KnowledgeComment.query.filter_by(article_id=article_id).delete()
    # 删除相关附件
    KnowledgeAttachment.query.filter_by(article_id=article_id).delete()
    
    db.session.delete(article)
    db.session.commit()
    flash('文章删除成功！')
    return redirect(url_for('knowledge.index'))

@bp.route('/article/view/<int:article_id>')
@login_required
def view_article(article_id):
    """查看知识库文章详情"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    
    # 获取文章评论
    comments = db.session.query(KnowledgeComment, User).join(
        User, KnowledgeComment.user_id == User.id
    ).filter(KnowledgeComment.article_id == article_id).order_by(
        KnowledgeComment.created_at.desc()
    ).all()
    
    # 获取文章附件
    attachments = KnowledgeAttachment.query.filter_by(article_id=article_id).all()
    
    return render_template('knowledge/view_article.html', title='文章详情', 
                         article=article, comments=comments, attachments=attachments)

@bp.route('/article/comment/<int:article_id>', methods=['POST'])
@login_required
def add_article_comment(article_id):
    """添加文章评论"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    content = request.form.get('content')
    
    comment = KnowledgeComment(
        article_id=article_id,
        user_id=current_user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    flash('评论添加成功！')
    return redirect(url_for('knowledge.view_article', article_id=article_id))

@bp.route('/category/<int:category_id>')
@login_required
def view_category(category_id):
    """查看分类下的文章列表"""
    category = KnowledgeCategory.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    query = KnowledgeArticle.query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            KnowledgeArticle.title.contains(keyword) | 
            KnowledgeArticle.content.contains(keyword)
        )
    
    articles = query.order_by(KnowledgeArticle.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('knowledge/view_category.html', title='分类文章', 
                         category=category, articles=articles)

@bp.route('/file/upload', methods=['POST'])
@login_required
def upload_file():
    """上传文件到网盘"""
    if 'file' not in request.files:
        flash('没有选择文件！', 'danger')
        return redirect(url_for('knowledge.files'))
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件！', 'danger')
        return redirect(url_for('knowledge.files'))
    
    # 这里应该处理文件上传，保存文件并记录到数据库
    # 简化处理，只记录文件信息
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    description = request.form.get('description')
    
    knowledge_file = KnowledgeFile(
        name=name,
        file_name=file.filename,
        file_path='',  # 实际应用中应该保存文件路径
        file_size=0,   # 实际应用中应该获取文件大小
        category_id=category_id,
        description=description,
        uploaded_by=current_user.id
    )
    
    db.session.add(knowledge_file)
    db.session.commit()
    flash('文件上传成功！')
    return redirect(url_for('knowledge.files'))

@bp.route('/file/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """删除网盘文件"""
    file = KnowledgeFile.query.get_or_404(file_id)
    
    # 这里应该删除实际文件
    db.session.delete(file)
    db.session.commit()
    flash('文件删除成功！')
    return redirect(url_for('knowledge.files'))

@bp.route('/manual/add', methods=['GET', 'POST'])
@login_required
def add_manual():
    """添加设备手册"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        equipment_model = request.form.get('equipment_model')
        manufacturer = request.form.get('manufacturer')
        version = request.form.get('version')
        
        manual = KnowledgeManual(
            title=title,
            content=content,
            category_id=category_id,
            equipment_model=equipment_model,
            manufacturer=manufacturer,
            version=version,
            created_by=current_user.id
        )
        
        db.session.add(manual)
        db.session.commit()
        flash('设备手册添加成功！')
        return redirect(url_for('knowledge.manuals'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/add_manual.html', title='添加设备手册', categories=categories)

@bp.route('/manual/edit/<int:manual_id>', methods=['GET', 'POST'])
@login_required
def edit_manual(manual_id):
    """编辑设备手册"""
    manual = KnowledgeManual.query.get_or_404(manual_id)
    
    if request.method == 'POST':
        manual.title = request.form.get('title')
        manual.content = request.form.get('content')
        manual.category_id = request.form.get('category_id')
        manual.equipment_model = request.form.get('equipment_model')
        manual.manufacturer = request.form.get('manufacturer')
        manual.version = request.form.get('version')
        
        db.session.commit()
        flash('设备手册更新成功！')
        return redirect(url_for('knowledge.manuals'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/edit_manual.html', title='编辑设备手册', 
                         manual=manual, categories=categories)

@bp.route('/manual/delete/<int:manual_id>', methods=['POST'])
@login_required
def delete_manual(manual_id):
    """删除设备手册"""
    manual = KnowledgeManual.query.get_or_404(manual_id)
    
    db.session.delete(manual)
    db.session.commit()
    flash('设备手册删除成功！')
    return redirect(url_for('knowledge.manuals'))

@bp.route('/manual/view/<int:manual_id>')
@login_required
def view_manual(manual_id):
    """查看设备手册详情"""
    manual = KnowledgeManual.query.get_or_404(manual_id)
    return render_template('knowledge/view_manual.html', title='设备手册详情', manual=manual)

@bp.route('/guide/add', methods=['GET', 'POST'])
@login_required
def add_guide():
    """添加操作指导"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        steps = request.form.get('steps')
        difficulty = request.form.get('difficulty')
        time_required = request.form.get('time_required')
        
        guide = KnowledgeGuide(
            title=title,
            content=content,
            category_id=category_id,
            steps=steps,
            difficulty=difficulty,
            time_required=time_required,
            created_by=current_user.id
        )
        
        db.session.add(guide)
        db.session.commit()
        flash('操作指导添加成功！')
        return redirect(url_for('knowledge.guides'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/add_guide.html', title='添加操作指导', categories=categories)

@bp.route('/guide/edit/<int:guide_id>', methods=['GET', 'POST'])
@login_required
def edit_guide(guide_id):
    """编辑操作指导"""
    guide = KnowledgeGuide.query.get_or_404(guide_id)
    
    if request.method == 'POST':
        guide.title = request.form.get('title')
        guide.content = request.form.get('content')
        guide.category_id = request.form.get('category_id')
        guide.steps = request.form.get('steps')
        guide.difficulty = request.form.get('difficulty')
        guide.time_required = request.form.get('time_required')
        
        db.session.commit()
        flash('操作指导更新成功！')
        return redirect(url_for('knowledge.guides'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/edit_guide.html', title='编辑操作指导', 
                         guide=guide, categories=categories)

@bp.route('/guide/delete/<int:guide_id>', methods=['POST'])
@login_required
def delete_guide(guide_id):
    """删除操作指导"""
    guide = KnowledgeGuide.query.get_or_404(guide_id)
    
    db.session.delete(guide)
    db.session.commit()
    flash('操作指导删除成功！')
    return redirect(url_for('knowledge.guides'))

@bp.route('/guide/view/<int:guide_id>')
@login_required
def view_guide(guide_id):
    """查看操作指导详情"""
    guide = KnowledgeGuide.query.get_or_404(guide_id)
    return render_template('knowledge/view_guide.html', title='操作指导详情', guide=guide)

@bp.route('/instruction/add', methods=['GET', 'POST'])
@login_required
def add_instruction():
    """添加说明书"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        product_name = request.form.get('product_name')
        product_model = request.form.get('product_model')
        manufacturer = request.form.get('manufacturer')
        
        instruction = KnowledgeInstruction(
            title=title,
            content=content,
            category_id=category_id,
            product_name=product_name,
            product_model=product_model,
            manufacturer=manufacturer,
            created_by=current_user.id
        )
        
        db.session.add(instruction)
        db.session.commit()
        flash('说明书添加成功！')
        return redirect(url_for('knowledge.instructions'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/add_instruction.html', title='添加说明书', categories=categories)

@bp.route('/instruction/edit/<int:instruction_id>', methods=['GET', 'POST'])
@login_required
def edit_instruction(instruction_id):
    """编辑说明书"""
    instruction = KnowledgeInstruction.query.get_or_404(instruction_id)
    
    if request.method == 'POST':
        instruction.title = request.form.get('title')
        instruction.content = request.form.get('content')
        instruction.category_id = request.form.get('category_id')
        instruction.product_name = request.form.get('product_name')
        instruction.product_model = request.form.get('product_model')
        instruction.manufacturer = request.form.get('manufacturer')
        
        db.session.commit()
        flash('说明书更新成功！')
        return redirect(url_for('knowledge.instructions'))
    
    # 获取所有分类
    categories = KnowledgeCategory.query.all()
    return render_template('knowledge/edit_instruction.html', title='编辑说明书', 
                         instruction=instruction, categories=categories)

@bp.route('/instruction/delete/<int:instruction_id>', methods=['POST'])
@login_required
def delete_instruction(instruction_id):
    """删除说明书"""
    instruction = KnowledgeInstruction.query.get_or_404(instruction_id)
    
    db.session.delete(instruction)
    db.session.commit()
    flash('说明书删除成功！')
    return redirect(url_for('knowledge.instructions'))

@bp.route('/instruction/view/<int:instruction_id>')
@login_required
def view_instruction(instruction_id):
    """查看说明书详情"""
    instruction = KnowledgeInstruction.query.get_or_404(instruction_id)
    return render_template('knowledge/view_instruction.html', title='说明书详情', instruction=instruction)
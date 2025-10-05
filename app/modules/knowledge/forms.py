from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class CategoryForm(FlaskForm):
    """知识库分类表单"""
    name = StringField('分类名称', validators=[DataRequired()])
    description = TextAreaField('分类描述', validators=[Optional()])
    parent_id = SelectField('父分类', coerce=int, validators=[Optional()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        # 这里应该从数据库获取分类列表作为父分类选项
        self.parent_id.choices = [(0, '无')]  # 临时空选项

class ArticleForm(FlaskForm):
    """知识库文章表单"""
    title = StringField('文章标题', validators=[DataRequired()])
    content = TextAreaField('文章内容', validators=[DataRequired()])
    category_id = SelectField('所属分类', coerce=int, validators=[DataRequired()])
    tags = StringField('标签', validators=[Optional()])
    is_public = SelectField('公开状态', choices=[
        ('public', '公开'),
        ('private', '私有')
    ], validators=[DataRequired()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        # 这里应该从数据库获取分类列表作为分类选项
        self.category_id.choices = [(0, '请选择')]  # 临时空选项
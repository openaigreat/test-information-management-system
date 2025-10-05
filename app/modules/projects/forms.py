from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class ProjectForm(FlaskForm):
    """项目表单"""
    name = StringField('项目名称', validators=[DataRequired()])
    description = TextAreaField('项目描述', validators=[Optional()])
    status = SelectField('项目状态', choices=[
        ('planning', '规划中'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('on_hold', '已暂停'),
        ('cancelled', '已取消')
    ], validators=[DataRequired()])
    priority = SelectField('优先级', choices=[
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急')
    ], validators=[DataRequired()])
    start_date = DateField('开始日期', validators=[DataRequired()])
    end_date = DateField('结束日期', validators=[Optional()])
    budget = DecimalField('预算', validators=[Optional(), NumberRange(min=0)])
    manager_id = SelectField('项目经理', coerce=int, validators=[DataRequired()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        # 这里应该从数据库获取用户列表作为项目经理选项
        self.manager_id.choices = [(0, '请选择')]  # 临时空选项
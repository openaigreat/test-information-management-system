from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models import User, Project

class TaskForm(FlaskForm):
    """任务表单"""
    title = StringField('任务标题', validators=[DataRequired()])
    description = TextAreaField('任务描述', validators=[Optional()])
    status = SelectField('任务状态', choices=[
        ('todo', '待办'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('overdue', '已逾期')
    ], validators=[DataRequired()])
    priority = SelectField('优先级', choices=[
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急')
    ], validators=[DataRequired()])
    assignee_id = SelectField('指派给', coerce=int, validators=[DataRequired()])
    project_id = SelectField('所属项目', coerce=int, validators=[Optional()])
    start_date = DateField('开始日期', validators=[Optional()])
    due_date = DateField('截止日期', validators=[DataRequired()])
    estimated_hours = DecimalField('预计工时', validators=[Optional(), NumberRange(min=0)])
    actual_hours = DecimalField('实际工时', validators=[Optional(), NumberRange(min=0)])
    progress = IntegerField('进度(%)', validators=[Optional(), NumberRange(min=0, max=100)])
    notes = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # 从数据库获取用户列表作为指派对象选项
        users = User.query.all()
        self.assignee_id.choices = [(user.id, user.username) for user in users]
        
        # 从数据库获取项目列表作为所属项目选项
        projects = Project.query.all()
        self.project_id.choices = [(0, '无')] + [(project.id, project.name) for project in projects]
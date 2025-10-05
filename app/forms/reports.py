from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, IntegerField, DateField, DateTimeField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from wtforms.widgets import TextArea

class ReportFilterForm(FlaskForm):
    start_date = DateField('开始日期', validators=[Optional()])
    end_date = DateField('结束日期', validators=[Optional()])
    department = SelectField('部门', choices=[], validators=[Optional()])
    user = SelectField('用户', choices=[], validators=[Optional()])
    project = SelectField('项目', choices=[], validators=[Optional()])
    status = SelectField('状态', choices=[('all', '全部'), ('pending', '待处理'), ('in_progress', '进行中'), ('completed', '已完成'), ('cancelled', '已取消')], validators=[Optional()])
    submit = SubmitField('生成报表')
    export_excel = SubmitField('导出Excel')
    export_pdf = SubmitField('导出PDF')

class PersonnelReportForm(ReportFilterForm):
    position = SelectField('职位', choices=[], validators=[Optional()])
    submit = SubmitField('生成人员报表')

class AttendanceReportForm(ReportFilterForm):
    submit = SubmitField('生成考勤报表')

class SalaryReportForm(ReportFilterForm):
    salary_min = FloatField('最低薪资', validators=[Optional()])
    salary_max = FloatField('最高薪资', validators=[Optional()])
    submit = SubmitField('生成薪资报表')

class TaskReportForm(ReportFilterForm):
    priority = SelectField('优先级', choices=[('all', '全部'), ('low', '低'), ('medium', '中'), ('high', '高'), ('urgent', '紧急')], validators=[Optional()])
    submit = SubmitField('生成任务报表')

class KnowledgeReportForm(ReportFilterForm):
    category = SelectField('分类', choices=[], validators=[Optional()])
    author = SelectField('作者', choices=[], validators=[Optional()])
    is_public = SelectField('公开状态', choices=[('all', '全部'), ('public', '公开'), ('private', '私有')], validators=[Optional()])
    submit = SubmitField('生成知识库报表')
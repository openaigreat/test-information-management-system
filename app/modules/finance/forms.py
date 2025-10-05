from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class FinanceRecordForm(FlaskForm):
    """资金记录表单"""
    title = StringField('标题', validators=[DataRequired()])
    amount = DecimalField('金额', validators=[DataRequired(), NumberRange(min=0.01)])
    record_type = SelectField('类型', choices=[('income', '收入'), ('expense', '支出')], validators=[DataRequired()])
    category = SelectField('分类', validators=[DataRequired()])
    date = DateField('日期', validators=[DataRequired()])
    description = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(FinanceRecordForm, self).__init__(*args, **kwargs)
        # 根据类型动态设置分类选项
        if hasattr(self, 'record_type') and self.record_type.data:
            if self.record_type.data == 'income':
                self.category.choices = [
                    ('sales', '销售收入'),
                    ('investment', '投资收益'),
                    ('subsidy', '补贴收入'),
                    ('other_income', '其他收入')
                ]
            else:
                self.category.choices = [
                    ('salary', '工资支出'),
                    ('rent', '租金支出'),
                    ('supplies', '物资采购'),
                    ('marketing', '营销费用'),
                    ('other_expense', '其他支出')
                ]
        else:
            self.category.choices = []
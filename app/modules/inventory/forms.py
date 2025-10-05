from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class ItemForm(FlaskForm):
    """物品表单"""
    name = StringField('物品名称', validators=[DataRequired()])
    category = SelectField('分类', validators=[DataRequired()])
    description = TextAreaField('描述', validators=[Optional()])
    unit = StringField('单位', validators=[DataRequired()])
    price = DecimalField('单价', validators=[DataRequired(), NumberRange(min=0)])
    supplier = StringField('供应商', validators=[Optional()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            ('office', '办公用品'),
            ('equipment', '设备器材'),
            ('material', '原材料'),
            ('product', '产品'),
            ('other', '其他')
        ]

class StockForm(FlaskForm):
    """库存表单"""
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=1)])
    date = DateField('日期', validators=[DataRequired()])
    operator = StringField('操作人', validators=[DataRequired()])
    remark = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
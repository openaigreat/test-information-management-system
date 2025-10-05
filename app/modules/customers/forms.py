from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class CustomerForm(FlaskForm):
    """客户表单"""
    name = StringField('客户名称', validators=[DataRequired()])
    contact_person = StringField('联系人', validators=[DataRequired()])
    email = EmailField('邮箱', validators=[Optional(), Email()])
    phone = TelField('电话', validators=[DataRequired()])
    address = StringField('地址', validators=[Optional()])
    description = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('提交')
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from app.models import Customer

class CustomerForm(FlaskForm):
    """客户表单"""
    name = StringField('客户名称', validators=[DataRequired(), Length(1, 100)])
    code = StringField('客户代码', validators=[Optional(), Length(1, 50)])
    contact_person = StringField('联系人', validators=[Optional(), Length(1, 50)])
    contact_phone = StringField('联系电话', validators=[Optional(), Length(1, 20)])
    email = StringField('邮箱', validators=[Optional(), Email()])
    address = StringField('地址', validators=[Optional(), Length(1, 200)])
    industry = StringField('行业', validators=[Optional(), Length(1, 50)])
    customer_type = SelectField('客户类型', choices=[
        ('individual', '个人'),
        ('company', '企业'),
        ('government', '政府'),
        ('other', '其他')
    ], default='company')
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('prospect', '潜在客户')
    ], default='prospect')
    description = TextAreaField('描述', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('保存')

    def validate_name(self, field):
        """验证客户名称是否已存在"""
        if hasattr(self, 'customer') and self.customer and field.data == self.customer.name:
            return
        if Customer.query.filter_by(name=field.data).first():
            raise ValidationError('客户名称已存在')

class ContactForm(FlaskForm):
    """联系人表单"""
    customer_id = IntegerField('客户ID', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 50)])
    position = StringField('职位', validators=[Optional(), Length(1, 50)])
    department = StringField('部门', validators=[Optional(), Length(1, 50)])
    phone = StringField('电话', validators=[Optional(), Length(1, 20)])
    mobile = StringField('手机', validators=[Optional(), Length(1, 20)])
    email = StringField('邮箱', validators=[Optional(), Email()])
    wechat = StringField('微信', validators=[Optional(), Length(1, 50)])
    qq = StringField('QQ', validators=[Optional(), Length(1, 20)])
    is_primary = BooleanField('主要联系人', default=False)
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '非活跃')
    ], default='active')
    description = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('保存')

class BusinessForm(FlaskForm):
    """业务往来表单"""
    customer_id = IntegerField('客户ID', validators=[DataRequired()])
    business_type = SelectField('业务类型', choices=[
        ('inquiry', '询价'),
        ('quotation', '报价'),
        ('order', '订单'),
        ('contract', '合同'),
        ('payment', '付款'),
        ('delivery', '交付'),
        ('service', '服务'),
        ('complaint', '投诉'),
        ('other', '其他')
    ], validators=[DataRequired()])
    title = StringField('标题', validators=[DataRequired(), Length(1, 100)])
    content = TextAreaField('内容', validators=[Optional(), Length(0, 1000)])
    amount = IntegerField('金额', validators=[Optional(), NumberRange(0)])
    date = DateField('日期', validators=[DataRequired()])
    status = SelectField('状态', choices=[
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ], default='pending')
    responsible_person = StringField('负责人', validators=[Optional(), Length(1, 50)])
    next_follow_up = DateField('下次跟进', validators=[Optional()])
    description = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('保存')

class CommunicationForm(FlaskForm):
    """沟通记录表单"""
    customer_id = IntegerField('客户ID', validators=[DataRequired()])
    contact_id = IntegerField('联系人ID', validators=[Optional()])
    communication_type = SelectField('沟通类型', choices=[
        ('phone', '电话'),
        ('email', '邮件'),
        ('meeting', '会议'),
        ('visit', '拜访'),
        ('wechat', '微信'),
        ('other', '其他')
    ], validators=[DataRequired()])
    title = StringField('主题', validators=[DataRequired(), Length(1, 100)])
    content = TextAreaField('内容', validators=[Optional(), Length(0, 1000)])
    date = DateField('日期', validators=[DataRequired()])
    next_follow_up = DateField('下次跟进', validators=[Optional()])
    description = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('保存')
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from app.models import User, Role

class PersonnelForm(FlaskForm):
    """人员表单"""
    username = StringField('用户名', validators=[DataRequired()])
    email = EmailField('邮箱', validators=[DataRequired(), Email()])
    name = StringField('姓名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[Optional()])
    password2 = PasswordField('确认密码', validators=[EqualTo('password')])
    role_id = SelectField('角色', coerce=int)
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(PersonnelForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(0, '无')] + [(r.id, r.name) for r in Role.query.order_by('name').all()]
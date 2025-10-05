from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, IntegerField, DateField, FileField, MultipleFileField, HiddenField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
from app.models import User, Role, Permission, Department, Position, Menu, SystemSettings

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(8, 32)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    phone = StringField('手机号', validators=[Optional(), Length(11)])
    submit = SubmitField('注册')

    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        """验证邮箱是否已存在"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(8, 32)])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('修改密码')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('请求密码重置')

class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('重置密码')

class EditProfileForm(FlaskForm):
    """编辑个人资料表单"""
    name = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    phone = StringField('手机号', validators=[Optional(), Length(11)])
    department = StringField('部门', validators=[Optional(), Length(1, 64)])
    position = StringField('职位', validators=[Optional(), Length(1, 64)])
    about_me = TextAreaField('个人简介', validators=[Optional(), Length(0, 256)])
    avatar = FileField('头像', validators=[Optional()])
    submit = SubmitField('保存')

    def validate_email(self, field):
        """验证邮箱是否已存在（排除当前用户）"""
        if field.data != self.email.data and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

class SystemSettingsForm(FlaskForm):
    """系统设置表单"""
    system_name = StringField('系统名称', validators=[DataRequired(), Length(1, 64)])
    system_version = StringField('系统版本', validators=[Optional(), Length(1, 32)])
    company_name = StringField('公司名称', validators=[Optional(), Length(1, 64)])
    copyright_info = StringField('版权信息', validators=[Optional(), Length(1, 128)])
    icp_number = StringField('ICP备案号', validators=[Optional(), Length(1, 32)])
    logo = FileField('系统Logo', validators=[Optional()])
    submit = SubmitField('保存')

class EmailSettingsForm(FlaskForm):
    """邮件设置表单"""
    smtp_server = StringField('SMTP服务器', validators=[DataRequired(), Length(1, 64)])
    smtp_port = IntegerField('SMTP端口', validators=[DataRequired(), NumberRange(1, 65535)])
    smtp_username = StringField('SMTP用户名', validators=[DataRequired(), Length(1, 64)])
    smtp_password = PasswordField('SMTP密码', validators=[DataRequired()])
    smtp_use_tls = BooleanField('使用TLS加密')
    email_from = StringField('发件人邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('保存')

class SecuritySettingsForm(FlaskForm):
    """安全设置表单"""
    password_min_length = IntegerField('密码最小长度', validators=[DataRequired(), NumberRange(6, 32)], default=8)
    password_require_uppercase = BooleanField('要求包含大写字母', default=True)
    password_require_lowercase = BooleanField('要求包含小写字母', default=True)
    password_require_numbers = BooleanField('要求包含数字', default=True)
    password_require_special_chars = BooleanField('要求包含特殊字符', default=True)
    login_attempts_limit = IntegerField('登录尝试限制次数', validators=[DataRequired(), NumberRange(1, 10)], default=5)
    login_lockout_duration = IntegerField('登录锁定时长(分钟)', validators=[DataRequired(), NumberRange(1, 1440)], default=30)
    session_timeout = IntegerField('会话超时时间(分钟)', validators=[DataRequired(), NumberRange(5, 1440)], default=60)
    submit = SubmitField('保存')

class InterfaceSettingsForm(FlaskForm):
    """界面设置表单"""
    theme = SelectField('主题', choices=[('light', '浅色'), ('dark', '深色')], default='light')
    primary_color = StringField('主色调', validators=[Optional(), Length(1, 7)], default='#1890ff')
    layout = SelectField('布局', choices=[('side', '侧边栏'), ('top', '顶部导航')], default='side')
    sidebar_collapsed = BooleanField('侧边栏默认折叠', default=False)
    show_breadcrumbs = BooleanField('显示面包屑导航', default=True)
    show_footer = BooleanField('显示页脚', default=True)
    submit = SubmitField('保存')

class RoleForm(FlaskForm):
    """角色表单"""
    name = StringField('角色名称', validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField('角色描述', validators=[Optional(), Length(0, 256)])
    permissions = SelectMultipleField('权限', coerce=int, validators=[Optional()])
    submit = SubmitField('保存')

    def validate_name(self, field):
        """验证角色名称是否已存在"""
        if Role.query.filter_by(name=field.data).first():
            raise ValidationError('角色名称已存在')

class PermissionForm(FlaskForm):
    """权限表单"""
    name = StringField('权限名称', validators=[DataRequired(), Length(1, 64)])
    code = StringField('权限代码', validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField('权限描述', validators=[Optional(), Length(0, 256)])
    submit = SubmitField('保存')

    def validate_code(self, field):
        """验证权限代码是否已存在"""
        if Permission.query.filter_by(code=field.data).first():
            raise ValidationError('权限代码已存在')

class UserForm(FlaskForm):
    """用户表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    phone = StringField('手机号', validators=[Optional(), Length(11)])
    password = PasswordField('密码', validators=[Optional(), Length(8, 32)])
    role_id = SelectField('角色', coerce=int, validators=[Optional()])
    department_id = SelectField('部门', coerce=int, validators=[Optional()])
    position_id = SelectField('职位', coerce=int, validators=[Optional()])
    status = SelectField('状态', choices=[('active', '激活'), ('inactive', '未激活'), ('locked', '锁定')], default='active')
    submit = SubmitField('保存')

    def validate_username(self, field):
        """验证用户名是否已存在"""
        if hasattr(self, 'user') and self.user and field.data == self.user.username:
            return
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        """验证邮箱是否已存在"""
        if hasattr(self, 'user') and self.user and field.data == self.user.email:
            return
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

class LogSearchForm(FlaskForm):
    """日志搜索表单"""
    action = StringField('操作类型', validators=[Optional()])
    user_id = SelectField('用户', coerce=int, validators=[Optional()])
    start_date = DateField('开始日期', validators=[Optional()])
    end_date = DateField('结束日期', validators=[Optional()])
    ip_address = StringField('IP地址', validators=[Optional()])
    status = SelectField('状态', choices=[('', '全部'), ('success', '成功'), ('failed', '失败')], validators=[Optional()])
    submit = SubmitField('搜索')

class BackupForm(FlaskForm):
    """备份表单"""
    backup_type = SelectField('备份类型', choices=[('full', '完整备份'), ('incremental', '增量备份')], default='full')
    backup_format = SelectField('备份格式', choices=[('sql', 'SQL'), ('zip', 'ZIP')], default='sql')
    backup_path = StringField('备份路径', validators=[Optional()])
    backup_filename = StringField('备份文件名', validators=[Optional()])
    submit = SubmitField('开始备份')

class RestoreForm(FlaskForm):
    """恢复表单"""
    backup_file = SelectField('备份文件', coerce=int, validators=[DataRequired()])
    restore_type = SelectField('恢复类型', choices=[('full', '完整恢复'), ('partial', '部分恢复')], default='full')
    submit = SubmitField('开始恢复')

class DepartmentForm(FlaskForm):
    """部门表单"""
    name = StringField('部门名称', validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField('部门描述', validators=[Optional(), Length(0, 256)])
    parent_id = SelectField('上级部门', coerce=int, validators=[Optional()])
    submit = SubmitField('保存')

    def validate_name(self, field):
        """验证部门名称是否已存在"""
        if hasattr(self, 'department') and self.department and field.data == self.department.name:
            return
        if Department.query.filter_by(name=field.data).first():
            raise ValidationError('部门名称已存在')

class PositionForm(FlaskForm):
    """职位表单"""
    name = StringField('职位名称', validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField('职位描述', validators=[Optional(), Length(0, 256)])
    submit = SubmitField('保存')

    def validate_name(self, field):
        """验证职位名称是否已存在"""
        if hasattr(self, 'position') and self.position and field.data == self.position.name:
            return
        if Position.query.filter_by(name=field.data).first():
            raise ValidationError('职位名称已存在')

class MenuForm(FlaskForm):
    """菜单表单"""
    name = StringField('菜单名称', validators=[DataRequired(), Length(1, 64)])
    title = StringField('菜单标题', validators=[DataRequired(), Length(1, 64)])
    path = StringField('菜单路径', validators=[Optional(), Length(1, 128)])
    icon = StringField('菜单图标', validators=[Optional(), Length(1, 64)])
    parent_id = SelectField('父菜单', coerce=int, validators=[Optional()])
    order = IntegerField('排序', validators=[Optional(), NumberRange(0, 999)], default=0)
    permission_code = StringField('权限代码', validators=[Optional(), Length(1, 64)])
    submit = SubmitField('保存')
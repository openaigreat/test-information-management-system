# 模型包初始化文件
# 此文件用于导出models目录下的所有模型，使app/models可以被正确识别为Python包

# 先导入基本模块，避免循环导入
from app import db, login_manager

# 导入用户模块和项目任务管理相关模型
from app.models.user import User
from app.models.auth import Role, Permission
from app.models.project import Project, Task, TaskComment, TaskAttachment

# 导入关联表
from app.models.associations import user_role, role_permission

__all__ = ['db', 'login_manager', 'User', 'Role', 'Permission', 'Project', 'Task', 'TaskComment', 'TaskAttachment',
           'user_role', 'role_permission']
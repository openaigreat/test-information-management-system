from .system import (
    LoginForm, RegistrationForm, ChangePasswordForm, EditProfileForm,
    RoleForm, PermissionForm, SystemSettingsForm, EmailSettingsForm,
    SecuritySettingsForm, InterfaceSettingsForm, UserForm, LogSearchForm,
    BackupForm, RestoreForm, DepartmentForm, PositionForm, MenuForm
)
from .customers import (
    CustomerForm, ContactForm, BusinessForm, CommunicationForm
)
from .finance import (
    AccountForm, TransactionForm, RecordForm, CategoryForm
)
from .inventory import (
    ItemForm, StockForm, StockInForm, StockOutForm, PurchaseForm, ReceiveForm
)
from .projects import (
    ProjectForm, TaskForm, TaskCommentForm, TaskAttachmentForm, MemberForm,
    DocumentForm, ScheduleForm, AccountingForm, RecordForm as ProjectRecordForm
)
from .knowledge import (
    CategoryForm as KnowledgeCategoryForm, ArticleForm, ArticleCommentForm,
    ArticleAttachmentForm, FileForm, ManualForm, GuideForm, InstructionForm
)

__all__ = [
    # System forms
    'LoginForm', 'RegistrationForm', 'ChangePasswordForm', 'EditProfileForm',
    'RoleForm', 'PermissionForm', 'SystemSettingsForm', 'EmailSettingsForm',
    'SecuritySettingsForm', 'InterfaceSettingsForm', 'UserForm', 'LogSearchForm',
    'BackupForm', 'RestoreForm', 'DepartmentForm', 'PositionForm', 'MenuForm',
    
    # Customer forms
    'CustomerForm', 'ContactForm', 'BusinessForm', 'CommunicationForm',
    
    # Finance forms
    'AccountForm', 'TransactionForm', 'RecordForm', 'CategoryForm',
    
    # Inventory forms
    'ItemForm', 'StockForm', 'StockInForm', 'StockOutForm', 'PurchaseForm', 'ReceiveForm',
    
    # Project forms
    'ProjectForm', 'TaskForm', 'TaskCommentForm', 'TaskAttachmentForm', 'MemberForm',
    'DocumentForm', 'ScheduleForm', 'AccountingForm', 'ProjectRecordForm',
    
    # Knowledge forms
    'KnowledgeCategoryForm', 'ArticleForm', 'ArticleCommentForm', 'ArticleAttachmentForm',
    'FileForm', 'ManualForm', 'GuideForm', 'InstructionForm'
]
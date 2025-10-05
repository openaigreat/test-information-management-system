import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, upload_folder, allowed_extensions=None):
    """保存文件到指定目录"""
    if file and allowed_file(file.filename, allowed_extensions):
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        
        # 添加UUID前缀避免文件名冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return file_path
    
    return None

def delete_file(file_path):
    """删除文件"""
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def get_file_size(file_path):
    """获取文件大小（字节）"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
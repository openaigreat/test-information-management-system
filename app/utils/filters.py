from flask import render_template_string

def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    if value is None:
        return ''
    return value.strftime(format)

def format_date(value, format='%Y-%m-%d'):
    """格式化日期"""
    if value is None:
        return ''
    return value.strftime(format)

def format_currency(value):
    """格式化货币"""
    if value is None:
        return '¥0.00'
    return f'¥{value:,.2f}'

def format_percentage(value):
    """格式化百分比"""
    if value is None:
        return '0%'
    return f'{value:.1f}%'

def truncate_html(html, length=100):
    """截断HTML文本"""
    if not html:
        return ''
    
    # 移除HTML标签
    text = render_template_string('{{ html | striptags }}', html=html)
    
    # 截断文本
    if len(text) <= length:
        return text
    
    return text[:length] + '...'
import requests
import json

# 基本URL
BASE_URL = "http://127.0.0.1:5000"

def test_admin_route():
    """测试管理页面路由"""
    print("===== 测试管理页面路由 ======")
    response = requests.get(f"{BASE_URL}/admin/")
    print(f"管理页面(/admin/)响应状态码: {response.status_code}")
    # 如果响应包含内容，检查是否包含登录表单相关信息
    if response.status_code == 200:
        if "login" in response.text.lower() or "username" in response.text.lower():
            print("检测到登录表单元素")

def test_reports_route():
    """测试报表主页路由"""
    print("\n===== 测试报表主页路由 ======")
    response = requests.get(f"{BASE_URL}/reports/")
    print(f"报表主页(/reports/)响应状态码: {response.status_code}")
    
    # 测试其他报表路由，但不期望它们在未登录状态下工作
    print("\n===== 测试其他报表路由（可能需要登录）======")
    
    # 测试人员报表
    print("\n测试人员报表...")
    response = requests.get(f"{BASE_URL}/reports/personnel")
    print(f"人员报表响应状态码: {response.status_code}")
    
    # 测试考勤报表
    print("\n测试考勤报表...")
    response = requests.get(f"{BASE_URL}/reports/attendance")
    print(f"考勤报表响应状态码: {response.status_code}")
    
    # 测试薪资报表
    print("\n测试薪资报表...")
    response = requests.get(f"{BASE_URL}/reports/salary")
    print(f"薪资报表响应状态码: {response.status_code}")
    
    # 测试任务报表
    print("\n测试任务报表...")
    response = requests.get(f"{BASE_URL}/reports/tasks")
    print(f"任务报表响应状态码: {response.status_code}")
    
    # 测试知识库报表
    print("\n测试知识库报表...")
    response = requests.get(f"{BASE_URL}/reports/knowledge")
    print(f"知识库报表响应状态码: {response.status_code}")

def main():
    # 测试管理页面路由
    test_admin_route()
    
    # 测试报表路由
    test_reports_route()

if __name__ == "__main__":
    main()
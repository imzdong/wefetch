#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Selenium登录功能
"""

from selenium_wechat_login import SeleniumWeChatLogin

def test_status_callback(status, message):
    """测试状态回调"""
    print(f"[{status.upper()}] {message}")

def main():
    print("=== 测试Selenium微信公众号登录 ===")
    
    login = SeleniumWeChatLogin()
    
    # 检查保存的cookies状态
    print("\n1. 检查保存的登录凭据状态...")
    cookie_status = login.check_saved_cookies_status()
    print(f"   {cookie_status['message']}")
    
    if cookie_status.get('has_cookies'):
        # 测试自动登录
        print("\n2. 尝试自动登录...")
        result = login.auto_login_with_cookies(test_status_callback)
        
        if result.get('success'):
            print("✅ 自动登录成功！")
            
            # 保持浏览器打开3秒让用户看到结果
            try:
                input("按Enter键关闭浏览器...")
            except:
                pass
        else:
            print(f"❌ 自动登录失败: {result['message']}")
    else:
        # 测试扫码登录
        print("\n2. 启动扫码登录...")
        result = login.login_with_qr_code(test_status_callback)
        
        if result.get('success'):
            print("✅ 扫码登录流程启动成功！")
            print("请在打开的浏览器中扫描二维码完成登录...")
            print("登录完成后，按Enter键关闭浏览器...")
            
            try:
                input("按Enter键关闭浏览器...")
            except:
                pass
        else:
            print(f"❌ 启动扫码登录失败: {result['message']}")
    
    # 关闭浏览器
    login.close_driver()
    print("\n测试完成！")

if __name__ == "__main__":
    main()
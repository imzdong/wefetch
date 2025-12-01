#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于Selenium的微信公众号扫码登录
支持自动扫码登录和cookie免密登录
"""

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import threading

class SeleniumWeChatLogin:
    """基于Selenium的微信公众号登录"""
    
    def __init__(self):
        self.driver = None
        self.cookie_file = "mp_cookies.json"
        self.login_success_callback = None
        self.status_callback = None
        
    def setup_driver(self):
        """设置Chrome浏览器"""
        try:
            options = webdriver.ChromeOptions()
            
            # 基本设置
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 禁用图片加载以提高速度（可选）
            # prefs = {"profile.managed_default_content_settings.images": 2}
            # options.add_experimental_option("prefs", prefs)
            
            # 创建浏览器实例
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
            
            # 执行脚本隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            return True
            
        except Exception as e:
            print(f"设置浏览器失败: {e}")
            return False
    
    def login_with_qr_code(self, status_callback=None):
        """扫码登录"""
        try:
            self.status_callback = status_callback
            
            if status_callback:
                status_callback("waiting", "正在初始化浏览器...")
            
            # 设置浏览器
            if not self.setup_driver():
                return {
                    'success': False,
                    'message': '浏览器初始化失败'
                }
            
            if status_callback:
                status_callback("waiting", "正在打开登录页面...")
            
            # 打开微信公众号后台登录页
            self.driver.get("https://mp.weixin.qq.com")
            
            # 等待页面加载完成
            time.sleep(3)
            
            if status_callback:
                status_callback("waiting", "请扫描二维码登录...")
            
            # 在新线程中等待登录完成
            threading.Thread(
                target=self.wait_for_login_complete, 
                daemon=True
            ).start()
            
            return {
                'success': True,
                'message': '请扫描二维码登录'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'启动登录失败: {str(e)}'
            }
    
    def wait_for_login_complete(self):
        """等待登录完成"""
        try:
            # 等待用户扫码完成，通过URL变化判断
            max_wait_time = 300  # 最大等待5分钟
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                current_url = self.driver.current_url
                
                # 多种登录成功的判断条件
                login_success_indicators = [
                    "home" in current_url,
                    "cgi-bin/home" in current_url,
                    "cgi-bin/operation" in current_url,
                    "cgi-bin/homepage" in current_url
                ]
                
                if any(login_success_indicators):
                    if self.status_callback:
                        self.status_callback("success", "登录成功，正在获取凭据...")
                    
                    # 获取登录凭据
                    result = self.extract_login_credentials()
                    
                    if self.status_callback:
                        if result['success']:
                            self.status_callback("success", "登录成功！")
                        else:
                            self.status_callback("error", result.get('message', '获取登录凭据失败'))
                    
                    return result
                
                # 检查是否有二维码过期或登录错误的情况
                # 只有在明确是错误页面时才报错，其他正常页面继续等待
                if "error" in current_url.lower() or "verify" in current_url.lower():
                    if self.status_callback:
                        self.status_callback("error", "页面状态异常，请重新尝试")
                    return {'success': False, 'message': '页面状态异常'}
                
                time.sleep(2)  # 每2秒检查一次
            
            # 超时
            if self.status_callback:
                self.status_callback("timeout", "登录超时，请重新扫描二维码")
            
            return {'success': False, 'message': '登录超时'}
            
        except Exception as e:
            if self.status_callback:
                self.status_callback("error", f"登录检查异常: {str(e)}")
            return {'success': False, 'message': f'登录检查异常: {str(e)}'}
    
    def auto_login_with_cookies(self, status_callback=None):
        """使用保存的cookies自动登录"""
        try:
            self.status_callback = status_callback
            
            if status_callback:
                status_callback("waiting", "正在检查保存的登录凭据...")
            
            # 检查cookies文件是否存在
            if not os.path.exists(self.cookie_file):
                return {
                    'success': False,
                    'message': '未找到保存的登录凭据，请先扫码登录'
                }
            
            if status_callback:
                status_callback("waiting", "正在初始化浏览器...")
            
            # 设置浏览器
            if not self.setup_driver():
                return {
                    'success': False,
                    'message': '浏览器初始化失败'
                }
            
            if status_callback:
                status_callback("waiting", "正在加载登录凭据...")
            
            # 先访问微信公众平台首页
            self.driver.get("https://mp.weixin.qq.com")
            time.sleep(3)
            
            # 读取并添加cookies
            with open(self.cookie_file, "r", encoding='utf-8') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"添加cookie失败: {e}")
                    continue
            
            # 刷新页面验证登录状态
            self.driver.get("https://mp.weixin.qq.com")
            time.sleep(3)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            if "home" in current_url or "cgi-bin/home" in current_url:
                if status_callback:
                    status_callback("success", "自动登录成功！")
                
                # 更新cookies（获取最新的会话信息）
                self.save_cookies()
                
                # 获取最新的登录凭据
                result = self.extract_login_credentials()
                
                return {
                    'success': True,
                    'message': '自动登录成功',
                    'credentials': result
                }
            else:
                if status_callback:
                    status_callback("error", "登录凭据已过期，请重新扫码登录")
                return {
                    'success': False,
                    'message': '登录凭据已过期，请重新扫码登录'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'自动登录失败: {str(e)}'
            }
    
    def extract_login_credentials(self):
        """提取登录凭据"""
        try:
            # 保存cookies
            cookies = self.save_cookies()
            
            # 从URL中提取token
            current_url = self.driver.current_url
            token = None
            
            if "token=" in current_url:
                try:
                    token = current_url.split("token=")[1].split("&")[0]
                except:
                    token = None
            
            # 获取页面源码尝试提取token
            if not token:
                try:
                    page_source = self.driver.page_source
                    if "token=" in page_source:
                        # 使用多种正则表达式模式提取token
                        import re
                        patterns = [
                            r'token["\']?\s*[:=]\s*["\']?(\d+)',
                            r'token=(\d+)',
                            r'"token":"?(\d+)"?',
                            r'token["\']?:["\']?(\d+)'
                        ]
                        
                        for pattern in patterns:
                            token_match = re.search(pattern, page_source)
                            if token_match:
                                token = token_match.group(1)
                                break
                                
                        # 如果还是找不到，尝试从localStorage获取
                        if not token:
                            try:
                                token = self.driver.execute_script("return localStorage.getItem('token') || '';")
                            except:
                                pass
                except:
                    pass
            
            if token and cookies:
                return {
                    'success': True,
                    'token': token,
                    'cookie': cookies,
                    'message': '登录凭据获取成功'
                }
            else:
                return {
                    'success': False,
                    'message': '无法获取完整的登录凭据'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'提取登录凭据失败: {str(e)}'
            }
    
    def save_cookies(self):
        """保存cookies到文件"""
        try:
            cookies = self.driver.get_cookies()
            
            with open(self.cookie_file, "w", encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            # 转换为请求头格式
            cookie_list = []
            for cookie in cookies:
                cookie_list.append(f"{cookie['name']}={cookie['value']}")
            
            return '; '.join(cookie_list)
            
        except Exception as e:
            print(f"保存cookies失败: {e}")
            return ""
    
    def check_saved_cookies_status(self):
        """检查保存的cookies状态"""
        try:
            if not os.path.exists(self.cookie_file):
                return {
                    'has_cookies': False,
                    'message': '未找到保存的登录凭据'
                }
            
            # 检查文件修改时间，判断是否可能过期
            file_time = os.path.getmtime(self.cookie_file)
            current_time = time.time()
            age_hours = (current_time - file_time) / 3600
            
            return {
                'has_cookies': True,
                'age_hours': age_hours,
                'message': f'找到保存的登录凭据（{age_hours:.1f}小时前）'
            }
            
        except Exception as e:
            return {
                'has_cookies': False,
                'message': f'检查登录凭据状态失败: {str(e)}'
            }
    
    def close_driver(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            print(f"关闭浏览器失败: {e}")

# 测试代码
if __name__ == "__main__":
    def test_status_callback(status, message):
        print(f"[{status.upper()}] {message}")
    
    login = SeleniumWeChatLogin()
    
    # 测试扫码登录
    print("=== 测试扫码登录 ===")
    result = login.login_with_qr_code(test_status_callback)
    
    if result.get('success'):
        print("✅ 扫码登录流程启动成功")
        print("请在浏览器中扫描二维码完成登录...")
        
        # 等待登录完成
        try:
            while True:
                time.sleep(5)
                current_url = login.driver.current_url
                if "home" in current_url:
                    print("🎉 登录成功！")
                    break
        except KeyboardInterrupt:
            print("用户中断登录流程")
        finally:
            login.close_driver()
    else:
        print(f"❌ 启动失败: {result['message']}")
    
    # 测试自动登录
    print("\n=== 测试自动登录 ===")
    cookie_status = login.check_saved_cookies_status()
    print(f"Cookie状态: {cookie_status['message']}")
    
    if cookie_status['has_cookies']:
        result = login.auto_login_with_cookies(test_status_callback)
        
        if result.get('success'):
            print("✅ 自动登录成功")
            time.sleep(3)  # 显示3秒让用户看到结果
        else:
            print(f"❌ 自动登录失败: {result['message']}")
        
        login.close_driver()
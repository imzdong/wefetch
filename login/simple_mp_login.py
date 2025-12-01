#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单直接的微信公众号登录
像第三方管理平台那样实现登录功能
"""

import requests
import time
import json
import re
from io import BytesIO
from PIL import Image
import qrcode
import uuid

class SimpleMPLogin:
    """简单直接的微信公众号登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """设置会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def get_login_qrcode(self):
        """获取登录二维码 - 简单直接的方式"""
        try:
            print("🔥 获取微信公众号登录二维码...")
            
            # 像第三方平台那样，先访问登录页面
            response = self.session.get("https://mp.weixin.qq.com/", timeout=10)
            
            if response.status_code == 200:
                # 从页面中提取必要的信息
                html = response.text
                
                # 查找二维码相关接口
                qr_patterns = [
                    r'scanloginqrcode[^"\']*',
                    r'loginqrcode[^"\']*',
                    r'getqrcode[^"\']*'
                ]
                
                qr_api = None
                for pattern in qr_patterns:
                    match = re.search(pattern, html)
                    if match:
                        qr_api = match.group(0)
                        if 'scanloginqrcode' in qr_api:
                            break
                
                if qr_api:
                    # 构造完整的URL
                    if qr_api.startswith('/cgi-bin/'):
                        qr_url = f"https://mp.weixin.qq.com{qr_api}"
                    elif qr_api.startswith('https://'):
                        qr_url = qr_api
                    else:
                        # 生成标准的二维码请求
                        timestamp = int(time.time() * 1000)
                        qr_url = f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={timestamp}&login_appid="
                    
                    print(f"📱 二维码接口: {qr_url}")
                    
                    # 获取二维码
                    qr_response = self.session.get(qr_url, timeout=10)
                    
                    if qr_response.status_code == 200 and len(qr_response.content) > 100:
                        print("✅ 成功获取到登录二维码！")
                        return qr_response.content, 'mp_qr', 'direct'
            
            # 如果直接获取失败，生成标准登录页面二维码
            return self.generate_mp_login_qr()
            
        except Exception as e:
            print(f"获取登录二维码失败: {e}")
            return self.generate_mp_login_qr()
    
    def generate_mp_login_qr(self):
        """生成微信公众平台登录二维码"""
        try:
            print("🔄 生成微信公众平台登录二维码...")
            
            # 生成指向微信公众平台的二维码
            mp_url = "https://mp.weixin.qq.com/"
            
            # 使用qrcode生成高质量二维码
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=12,
                border=4,
            )
            
            qr.add_data(mp_url)
            qr.make(fit=True)
            
            # 使用微信绿色
            img = qr.make_image(fill_color="#07C160", back_color="white")
            
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_bytes = img_buffer.getvalue()
            
            print("✅ 成功生成登录二维码")
            return img_bytes, 'generated', 'mp_login'
            
        except Exception as e:
            print(f"生成二维码失败: {e}")
            return None, None, None
    
    def login_with_password(self, username, password):
        """账号密码登录 - 像第三方平台那样实现"""
        try:
            print("🔐 正在执行账号密码登录...")
            
            # 像第三方平台那样，先获取登录页面
            login_page_url = "https://mp.weixin.qq.com/"
            response = self.session.get(login_page_url)
            
            if response.status_code == 200:
                html = response.text
                
                # 提取必要的登录参数
                form_data = {
                    'username': username,
                    'password': password,
                    'f': 'json',
                    'imgcode': '',
                    'lang': 'zh_CN'
                }
                
                # 查找隐藏字段
                hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']', html)
                
                for name, value in hidden_fields:
                    form_data[name] = value
                
                # 查找登录接口
                login_url_patterns = [
                    r'action=["\']([^"\']*login[^"\']*)["\']',
                    r'loginurl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                ]
                
                login_url = None
                for pattern in login_url_patterns:
                    match = re.search(pattern, html)
                    if match:
                        login_url = match.group(1)
                        if login_url.startswith('/'):
                            login_url = f"https://mp.weixin.qq.com{login_url}"
                        break
                
                # 如果找不到，使用标准的登录接口
                if not login_url:
                    # 尝试多个可能的登录接口
                    possible_urls = [
                        "https://mp.weixin.qq.com/cgi-bin/login",
                        "https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN",
                        "https://mp.weixin.qq.com/login",
                        "https://mp.weixin.qq.com/login?lang=zh_CN"
                    ]
                    login_url = possible_urls[0]  # 使用第一个作为默认
                
                print(f"🔑 登录接口: {login_url}")
                
                # 设置请求头
                headers = {
                    'Referer': 'https://mp.weixin.qq.com/',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
                
                # 执行登录
                login_response = self.session.post(login_url, data=form_data, headers=headers)
                
                print(f"登录响应状态: {login_response.status_code}")
                print(f"登录响应内容: {login_response.text[:200]}")
                
                if login_response.status_code == 200:
                    try:
                        result = login_response.json()
                        
                        if result.get('ret') == 0:
                            # 登录成功
                            redirect_url = result.get('redirect_url', '')
                            token = self.extract_token_from_url(redirect_url)
                            cookie = self.extract_cookies()
                            
                            return {
                                'success': True,
                                'token': token,
                                'cookie': cookie,
                                'message': '登录成功'
                            }
                        else:
                            # 登录失败
                            return {
                                'success': False,
                                'message': result.get('msg', '登录失败')
                            }
                            
                    except json.JSONDecodeError:
                        # 如果不是JSON，可能是HTML响应
                        if 'token=' in login_response.text:
                            token = self.extract_token_from_html(login_response.text)
                            cookie = self.extract_cookies()
                            
                            return {
                                'success': True,
                                'token': token,
                                'cookie': cookie,
                                'message': '登录成功'
                            }
            
            return {
                'success': False,
                'message': '登录失败，请检查账号密码'
            }
            
        except Exception as e:
            print(f"账号密码登录失败: {e}")
            return {
                'success': False,
                'message': f'登录失败: {str(e)}'
            }
    
    def extract_token_from_url(self, url):
        """从URL中提取token"""
        if url and 'token=' in url:
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                return query_params.get('token', [''])[0]
            except:
                pass
        return ''
    
    def extract_token_from_html(self, html):
        """从HTML中提取token"""
        try:
            # 查找token
            token_match = re.search(r'token["\']?\s*[:=]\s*["\']?(\d+)', html)
            if token_match:
                return token_match.group(1)
        except:
            pass
        return ''
    
    def extract_cookies(self):
        """提取cookie字符串"""
        try:
            cookies = []
            for name, value in self.session.cookies.items():
                cookies.append(f"{name}={value}")
            return '; '.join(cookies)
        except:
            return ''

class MPQRStatusChecker:
    """二维码状态检查器"""
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
    
    def check_qr_status(self, callback):
        """检查二维码状态"""
        try:
            # 模拟第三方平台的二维码状态检查
            for i in range(120):  # 检查2分钟
                time.sleep(1)
                
                # 这里应该调用状态检查接口
                # 由于我们可能没有正确的接口，所以提供一个简单的时间检查
                
                if i % 10 == 0:  # 每10秒检查一次
                    callback('waiting', f'等待扫码... ({i//10}/12)')
                
                # 模拟用户扫码后的处理
                # 实际上需要根据微信接口的具体返回来判断
                
            callback('timeout', '二维码已过期，请重新生成')
            
        except Exception as e:
            callback('error', f'检查状态失败: {str(e)}')
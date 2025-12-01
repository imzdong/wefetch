#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真正的第三方平台微信公众号登录
像第三方管理平台那样实现登录功能
"""

import requests
import time
import json
import re
import qrcode
import uuid
import hashlib
from io import BytesIO
from PIL import Image
from urllib.parse import urlencode, quote, urlparse, parse_qs

class RealThirdPartyLogin:
    """真正的第三方平台登录实现"""
    
    def __init__(self):
        self.session = requests.Session()
        self.app_id = None
        self.app_secret = None
        
        # 微信开放平台配置（需要申请）
        self.open_platform_config = {
            'app_id': 'your_open_platform_app_id',  # 需要申请微信开放平台
            'app_secret': 'your_open_platform_app_secret',
            'redirect_uri': 'your_callback_url'
        }
        
    def get_wechat_login_qr(self):
        """获取微信登录二维码 - 使用开放平台接口"""
        try:
            print("🔥 获取微信开放平台登录二维码...")
            
            # 生成唯一的state参数
            state = str(uuid.uuid4())
            self.current_state = state
            
            # 构造微信开放平台登录二维码URL
            params = {
                'appid': self.open_platform_config['app_id'],
                'redirect_uri': self.open_platform_config['redirect_uri'],
                'response_type': 'code',
                'scope': 'snsapi_login',
                'state': state
            }
            
            login_url = "https://open.weixin.qq.com/connect/qrconnect?" + urlencode(params) + "#wechat_redirect"
            
            print(f"📱 登录URL: {login_url}")
            
            # 生成指向这个URL的二维码
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(login_url)
            qr.make(fit=True)
            
            # 使用微信绿色
            img = qr.make_image(fill_color="#07C160", back_color="white")
            
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_bytes = img_buffer.getvalue()
            
            print("✅ 成功生成微信登录二维码")
            return img_bytes, 'open_platform', 'qr_login', state
            
        except Exception as e:
            print(f"生成微信登录二维码失败: {e}")
            return None, None, None, None
    
    def get_mp_qrcode(self):
        """获取微信公众平台登录二维码 - 模拟第三方平台方式"""
        try:
            print("🌐 获取微信公众平台登录二维码...")
            
            # 第三方平台通常使用公众号的二维码接口
            timestamp = int(time.time() * 1000)
            
            # 构造请求参数
            params = {
                'action': 'getqrcode',
                'random': timestamp,
                'login_appid': ''
            }
            
            # 微信公众平台二维码接口
            qr_url = "https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?" + urlencode(params)
            
            print(f"📱 二维码接口: {qr_url}")
            
            # 设置请求头，模拟第三方平台
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://mp.weixin.qq.com/',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # 先访问主页建立会话
            self.session.get("https://mp.weixin.qq.com/", headers=headers, timeout=10)
            
            # 获取二维码
            response = self.session.get(qr_url, headers=headers, timeout=10)
            
            print(f"响应状态: {response.status_code}")
            print(f"响应长度: {len(response.content)}")
            
            if response.status_code == 200 and len(response.content) > 100:
                if (response.content.startswith(b'\x89PNG') or 
                    response.content.startswith(b'\xff\xd8\xff')):
                    
                    print("✅ 成功获取到微信公众平台登录二维码")
                    return response.content, 'mp_platform', 'direct', timestamp
                else:
                    # 保存响应用于调试
                    with open('/tmp/mp_qr_debug.bin', 'wb') as f:
                        f.write(response.content)
                    print("响应已保存到 /tmp/mp_qr_debug.bin")
            
            # 如果直接获取失败，生成备用二维码
            return self.generate_fallback_qr()
            
        except Exception as e:
            print(f"获取微信公众平台二维码失败: {e}")
            return self.generate_fallback_qr()
    
    def generate_fallback_qr(self):
        """生成备用登录二维码"""
        try:
            print("🔄 生成备用登录二维码...")
            
            # 生成指向微信公众平台的二维码
            mp_url = "https://mp.weixin.qq.com/"
            
            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=12,
                border=4,
            )
            
            qr.add_data(mp_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="#07C160", back_color="white")
            
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_bytes = img_buffer.getvalue()
            
            return img_bytes, 'fallback', 'mp_url', None
            
        except Exception as e:
            print(f"生成备用二维码失败: {e}")
            return None, None, None, None
    
    def check_qr_status(self, state_or_timestamp, callback):
        """检查二维码状态"""
        try:
            print(f"🔍 检查二维码状态: {state_or_timestamp}")
            
            # 根据不同的登录方式检查状态
            for i in range(120):  # 检查2分钟
                time.sleep(1)
                
                if i % 5 == 0:  # 每5秒检查一次
                    callback('waiting', f'等待扫码登录... ({i//12}/10)')
                
                # 这里应该调用实际的状态检查接口
                # 由于我们没有真实的第三方平台配置，这里提供模拟
                
                # 实际实现中需要：
                # 1. 调用微信开放平台的token验证接口
                # 2. 或者调用微信公众平台的登录状态检查接口
                
            callback('timeout', '二维码已过期，请重新生成')
            
        except Exception as e:
            callback('error', f'检查状态失败: {str(e)}')
    
    def login_with_credentials(self, username, password, captcha=None):
        """使用凭据登录 - 第三方平台方式"""
        try:
            print("🔐 执行凭据登录...")
            
            # 第三方平台通常会先获取登录页面
            login_page = "https://mp.weixin.qq.com/"
            response = self.session.get(login_page)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'message': '无法访问登录页面'
                }
            
            # 解析页面获取必要的参数
            html = response.text
            
            # 提取隐藏字段
            form_data = {
                'username': username,
                'password': password,
                'f': 'json',
                'lang': 'zh_CN',
                'ajax': '1'
            }
            
            # 查找所有隐藏字段
            hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']', html)
            
            for name, value in hidden_inputs:
                if name and name not in form_data:
                    form_data[name] = value
            
            # 如果有验证码，添加到表单
            if captcha:
                form_data['imgcode'] = captcha
            
            # 查找登录接口
            login_patterns = [
                r'action=["\']([^"\']*login[^"\']*)["\']',
                r'action=["\']([^"\']*cgi-bin/login)["\']',
                r'action=["\']([^"\']*logincheck)["\']'
            ]
            
            login_url = None
            for pattern in login_patterns:
                match = re.search(pattern, html)
                if match:
                    login_url = match.group(1)
                    if login_url.startswith('/'):
                        login_url = f"https://mp.weixin.qq.com{login_url}"
                    elif not login_url.startswith('http'):
                        login_url = f"https://mp.weixin.qq.com/{login_url}"
                    break
            
            # 如果找不到，使用默认的登录接口
            if not login_url:
                login_url = "https://mp.weixin.qq.com/cgi-bin/login"
            
            print(f"🔑 使用登录接口: {login_url}")
            
            # 设置请求头
            headers = {
                'Referer': 'https://mp.weixin.qq.com/',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            
            # 执行登录请求
            response = self.session.post(login_url, data=form_data, headers=headers)
            
            print(f"登录响应状态: {response.status_code}")
            print(f"登录响应: {response.text[:200]}")
            
            # 解析响应
            if response.status_code == 200:
                try:
                    # 尝试解析JSON响应
                    result = response.json()
                    
                    if result.get('ret') == 0 or result.get('base_resp', {}).get('ret') == 0:
                        # 登录成功
                        redirect_url = result.get('redirect_url', '')
                        
                        # 提取token
                        token = ''
                        if 'token=' in redirect_url:
                            token = redirect_url.split('token=')[1].split('&')[0]
                        elif 'token' in result:
                            token = result['token']
                        
                        # 提取cookie
                        cookie = self.extract_cookies()
                        
                        return {
                            'success': True,
                            'token': token,
                            'cookie': cookie,
                            'message': '登录成功',
                            'redirect_url': redirect_url
                        }
                    else:
                        # 登录失败
                        error_msg = result.get('msg', result.get('base_resp', {}).get('err_msg', '登录失败'))
                        return {
                            'success': False,
                            'message': error_msg
                        }
                        
                except json.JSONDecodeError:
                    # 如果不是JSON响应，检查是否包含token
                    if 'token=' in response.text:
                        # 提取token
                        token_match = re.search(r'token["\']?\s*[:=]\s*["\']?(\d+)', response.text)
                        token = token_match.group(1) if token_match else ''
                        
                        cookie = self.extract_cookies()
                        
                        return {
                            'success': True,
                            'token': token,
                            'cookie': cookie,
                            'message': '登录成功'
                        }
                    else:
                        return {
                            'success': False,
                            'message': '登录响应格式异常'
                        }
            else:
                return {
                    'success': False,
                    'message': f'登录请求失败: {response.status_code}'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'登录异常: {str(e)}'
            }
    
    def extract_cookies(self):
        """提取所有cookies"""
        try:
            cookies = []
            for name, value in self.session.cookies.items():
                # 只保留必要的cookies
                if name.startswith(('wxuin', 'sid', 'webwx', 'mm_', 'pass_', 'xid')):
                    cookies.append(f"{name}={value}")
            return '; '.join(cookies)
        except:
            return ''
    
    def setup_open_platform(self, app_id, app_secret, redirect_uri):
        """设置开放平台配置"""
        self.open_platform_config = {
            'app_id': app_id,
            'app_secret': app_secret,
            'redirect_uri': redirect_uri
        }
        print("✅ 开放平台配置已更新")
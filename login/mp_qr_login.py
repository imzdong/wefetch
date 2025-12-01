#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号平台直接扫码登录
真正的微信公众号管理后台登录功能
"""

import requests
import time
import json
import re
from io import BytesIO
from PIL import Image
import qrcode
from urllib.parse import urlparse, parse_qs
import random
import string

class MPDirectQRLogin:
    """微信公众号平台直接扫码登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.login_uuid = None
        self.qr_data = None
        self.login_status = 'waiting'
        
    def get_mp_login_qrcode(self):
        """获取微信公众号登录二维码"""
        try:
            # 方法1: 直接获取公众号登录页面二维码
            print("正在获取微信公众号登录二维码...")
            
            # 首先访问公众号登录页面获取必要的参数
            login_url = "https://mp.weixin.qq.com/"
            response = self.session.get(login_url)
            
            if response.status_code == 200:
                # 解析页面，查找二维码相关的信息
                content = response.text
                
                # 查找二维码相关的API接口
                qr_patterns = [
                    r'qr\.cgi[^"\']*',
                    r'qrcode[^"\']*',
                    r'login[^"\']*qr[^"\']*',
                    r'getqrcode[^"\']*'
                ]
                
                qr_url = None
                for pattern in qr_patterns:
                    match = re.search(pattern, content)
                    if match:
                        qr_candidate = match.group(0)
                        if 'http' in qr_candidate:
                            qr_url = qr_candidate
                            break
                
                # 如果没找到，尝试构造二维码URL
                if not qr_url:
                    # 生成UUID用于二维码
                    self.login_uuid = self.generate_uuid()
                    
                    # 微信公众号登录二维码API
                    import time
                    timestamp = int(time.time() * 1000)  # 毫秒时间戳
                    
                    qr_urls = [
                        f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={timestamp}&login_appid=",
                        f"https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode&param=4300&uuid={self.login_uuid}",
                        f"https://mp.weixin.qq.com/cgi-bin/loginloginqrcode?action=getqrcode&uuid={self.login_uuid}"
                    ]
                    
                    for url in qr_urls:
                        try:
                            print(f"尝试获取二维码: {url}")
                            qr_response = self.session.get(url, timeout=10)
                            
                            if qr_response.status_code == 200 and len(qr_response.content) > 1000:
                                # 检查是否是图片数据
                                if qr_response.content.startswith(b'\x89PNG') or qr_response.content.startswith(b'\xff\xd8\xff'):
                                    print("成功获取到二维码图片")
                                    self.qr_data = qr_response.content
                                    return qr_response.content, 'direct', 'mp_qr'
                                    
                        except Exception as e:
                            print(f"尝试URL失败: {url}, 错误: {e}")
                            continue
                
                # 方法2: 如果直接获取失败，生成登录页面的二维码
                if not self.qr_data:
                    print("使用备用方案：生成登录页面二维码")
                    return self.generate_login_page_qr()
                    
            else:
                print(f"访问登录页面失败: {response.status_code}")
                return self.generate_login_page_qr()
                
        except Exception as e:
            print(f"获取二维码失败: {e}")
            return self.generate_login_page_qr()
    
    def generate_login_page_qr(self):
        """生成登录页面的二维码作为备用方案"""
        try:
            # 生成指向微信公众平台登录页面的二维码
            login_url = "https://mp.weixin.qq.com/"
            
            # 使用qrcode库生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(login_url)
            qr.make(fit=True)
            
            # 创建图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            self.qr_data = img_bytes
            return img_bytes, 'redirect', 'login_page'
            
        except Exception as e:
            print(f"生成备用二维码失败: {e}")
            return None, None, None
    
    def check_mp_login_status(self, callback):
        """检查微信公众号登录状态"""
        try:
            if not self.login_uuid and not self.qr_data:
                callback('error', '没有有效的登录会话')
                return
            
            # 如果是重定向类型的二维码，直接提示用户手动操作
            if hasattr(self, 'qr_method') and self.qr_method == 'redirect':
                callback('waiting', '请扫描二维码访问登录页面，然后在页面中完成登录')
                time.sleep(3)
                callback('manual_required', '请在浏览器中完成登录后获取Cookie和Token')
                return
                
            # 如果有UUID，检查登录状态
            if self.login_uuid:
                max_attempts = 120  # 2分钟检查时间
                attempt = 0
                
                while attempt < max_attempts and self.login_status == 'waiting':
                    try:
                        # 微信公众号登录状态检查接口
                        timestamp = int(time.time() * 1000)
                        status_urls = [
                            f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&random={timestamp}&login_appid=",
                            f"https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=ask&uuid={self.login_uuid}&lang=zh_CN&f=json",
                            f"https://mp.weixin.qq.com/cgi-bin/checklogin?uuid={self.login_uuid}&lang=zh_CN&f=json",
                        ]
                        
                        for status_url in status_urls:
                            try:
                                response = self.session.get(status_url, timeout=5)
                                
                                if response.status_code == 200:
                                    try:
                                        data = response.json()
                                        
                                        if data.get('code') == 200:
                                            # 登录成功
                                            callback('success', '登录成功', self.extract_login_data(response))
                                            return
                                        elif data.get('code') == 201:
                                            # 已扫描，等待确认
                                            callback('scanned', '二维码已扫描，请在手机上确认登录')
                                        elif data.get('code') == 408:
                                            # 等待扫描
                                            callback('waiting', '等待扫描二维码...')
                                        else:
                                            # 其他状态
                                            print(f"登录状态: {data}")
                                            callback('waiting', f'检查登录状态... (尝试 {attempt + 1}/{max_attempts})')
                                            
                                    except json.JSONDecodeError:
                                        # 如果不是JSON，检查是否包含成功标识
                                        if 'window.wx' in response.text or 'token=' in response.text:
                                            callback('success', '登录成功', self.extract_login_data_from_html(response.text))
                                            return
                                            
                            except Exception as e:
                                print(f"检查状态URL失败: {status_url}, 错误: {e}")
                                continue
                                
                    except Exception as e:
                        print(f"检查登录状态失败: {e}")
                    
                    time.sleep(1)  # 每秒检查一次
                    attempt += 1
                
                # 超时
                if attempt >= max_attempts:
                    callback('timeout', '登录超时，请重新生成二维码')
                    
        except Exception as e:
            callback('error', f'检查登录状态时出错: {str(e)}')
    
    def extract_login_data(self, response):
        """从登录成功的响应中提取数据"""
        try:
            data = {}
            
            # 尝试从JSON响应中提取
            try:
                json_data = response.json()
                if 'redirect_url' in json_data:
                    redirect_url = json_data['redirect_url']
                    data.update(self.parse_redirect_url(redirect_url))
            except:
                pass
                
            # 从响应头中提取Cookie
            if 'set-cookie' in response.headers:
                cookies = response.headers.get('set-cookie', '')
                data['cookie'] = self.extract_cookies_from_header(cookies)
                
            # 从URL中提取token
            if 'token' in response.url:
                parsed_url = urlparse(response.url)
                query_params = parse_qs(parsed_url.query)
                if 'token' in query_params:
                    data['token'] = query_params['token'][0]
                    
            return data
            
        except Exception as e:
            print(f"提取登录数据失败: {e}")
            return {}
    
    def extract_login_data_from_html(self, html_content):
        """从HTML内容中提取登录数据"""
        try:
            data = {}
            
            # 查找token
            token_match = re.search(r'token["\']?\s*[:=]\s*["\']?(\d+)', html_content)
            if token_match:
                data['token'] = token_match.group(1)
                
            # 查找其他相关信息
            # 这里可以添加更多的正则表达式来提取需要的数据
            
            return data
            
        except Exception as e:
            print(f"从HTML提取数据失败: {e}")
            return {}
    
    def parse_redirect_url(self, redirect_url):
        """解析重定向URL获取登录信息"""
        try:
            parsed = urlparse(redirect_url)
            query_params = parse_qs(parsed.query)
            
            data = {}
            if 'token' in query_params:
                data['token'] = query_params['token'][0]
                
            return data
            
        except Exception as e:
            print(f"解析重定向URL失败: {e}")
            return {}
    
    def extract_cookies_from_header(self, cookie_header):
        """从Set-Cookie头中提取cookie"""
        try:
            cookies = []
            
            # 分割多个cookie
            for cookie_str in cookie_header.split(','):
                cookie_str = cookie_str.strip()
                
                # 提取cookie名和值
                parts = cookie_str.split(';')[0]
                if '=' in parts:
                    cookies.append(parts.strip())
                    
            return '; '.join(cookies)
            
        except Exception as e:
            print(f"提取Cookie失败: {e}")
            return ''
    
    def generate_uuid(self):
        """生成UUID"""
        def random_string(length):
            chars = string.ascii_letters + string.digits
            return ''.join(random.choice(chars) for _ in range(length))
        
        # 生成类似微信UUID的格式
        return random_string(8) + random_string(4) + random_string(4) + random_string(4) + random_string(12)

class SimpleMPQRLogin:
    """简化的微信公众号登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """设置会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def get_simple_login_qr(self):
        """获取简单的登录二维码"""
        try:
            # 直接生成指向微信公众平台的二维码
            mp_url = "https://mp.weixin.qq.com/"
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=12,
                border=4,
            )
            
            qr.add_data(mp_url)
            qr.make(fit=True)
            
            # 创建图片
            img = qr.make_image(fill_color="#00C800", back_color="white")
            
            # 在中心添加微信logo（可选）
            try:
                # 这里可以添加微信logo
                pass
            except:
                pass
                
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_bytes = img_buffer.getvalue()
            
            return img_bytes, 'simple', 'mp_redirect'
            
        except Exception as e:
            print(f"生成简单登录二维码失败: {e}")
            return None, None, None
    
    def check_simple_login_status(self, callback):
        """检查简单登录状态 - 这个主要依赖手动操作"""
        callback('waiting', '请扫描二维码访问微信公众平台并完成登录')
        time.sleep(2)
        callback('manual', '请在浏览器中完成登录后，使用Cookie获取助手获取登录信息')
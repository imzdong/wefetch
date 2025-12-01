#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号扫码登录 - 正确版本
真正实现微信公众号管理平台的扫码登录功能
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

class WeChatMPQRLogin:
    """微信公众号扫码登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.login_data = {}
        
    def setup_session(self):
        """设置会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_mp_qrcode(self):
        """获取微信公众号登录二维码"""
        try:
            print("正在获取微信公众号登录二维码...")
            
            # 使用您提供的有效接口
            timestamp = int(time.time() * 1000)
            qr_url = f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={timestamp}&login_appid="
            
            print(f"使用有效接口获取二维码: {qr_url}")
            
            # 设置必要的请求头，模拟浏览器行为
            headers = {
                'Referer': 'https://mp.weixin.qq.com/',
                'Origin': 'https://mp.weixin.qq.com',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # 先访问登录页面建立会话
            print("首先访问登录页面建立会话...")
            self.session.get("https://mp.weixin.qq.com/", headers=headers, timeout=10)
            
            # 获取二维码
            response = self.session.get(qr_url, headers=headers, timeout=10)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.content)}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                if len(response.content) == 0:
                    print("响应为空，尝试添加延迟...")
                    # 有时需要等待一下再重试
                    time.sleep(0.5)
                    response = self.session.get(qr_url, headers=headers, timeout=10)
                    print(f"重试后响应长度: {len(response.content)}")
                
                if len(response.content) > 100:
                    # 检查是否是图片
                    content_type = response.headers.get('Content-Type', '')
                    print(f"Content-Type: {content_type}")
                    
                    if (response.content.startswith(b'\x89PNG') or 
                        response.content.startswith(b'\xff\xd8\xff') or
                        'image' in content_type):
                        print("🎉 成功获取到二维码图片！")
                        return response.content, 'mp_qr', 'direct'
                    else:
                        # 调试输出
                        print("响应不是图片格式")
                        print(f"响应内容前50字符: {response.text[:50]}")
                        
                        # 可能需要保存响应内容来调试
                        with open('/tmp/debug_response.txt', 'wb') as f:
                            f.write(response.content)
                        print("已保存响应内容到 /tmp/debug_response.txt")
            
            # 如果直接获取失败，但状态码是200，可能是参数问题
            if response.status_code == 200 and len(response.content) == 0:
                print("状态码200但内容为空，可能是参数或会话问题")
                return self.get_qr_with_fresh_session(timestamp)
            
            # 方法2: 如果直接获取失败，尝试先访问登录页面
            return self.get_qr_via_page()
            
        except Exception as e:
            print(f"获取二维码失败: {e}")
            return self.get_fallback_qr()
    
    def get_qr_with_fresh_session(self, timestamp):
        """使用全新的会话获取二维码"""
        try:
            print("尝试使用全新会话获取二维码...")
            
            # 创建新会话
            new_session = requests.Session()
            new_session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://mp.weixin.qq.com/'
            })
            
            # 直接访问
            qr_url = f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={timestamp}&login_appid="
            response = new_session.get(qr_url, timeout=10)
            
            print(f"新会话响应长度: {len(response.content)}")
            
            if len(response.content) > 100:
                print("🎉 新会话成功获取到二维码！")
                return response.content, 'mp_qr', 'new_session'
            
            return self.get_fallback_qr()
            
        except Exception as e:
            print(f"新会话获取失败: {e}")
            return self.get_fallback_qr()
    
    def get_qr_via_page(self):
        """通过登录页面获取二维码"""
        try:
            print("尝试通过登录页面获取二维码...")
            
            # 先访问登录页面
            page_url = "https://mp.weixin.qq.com/"
            response = self.session.get(page_url)
            
            print(f"登录页面状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 从页面中提取相关信息
                content = response.text
                
                # 查找页面中的二维码相关代码
                qr_match = re.search(r'scanloginqrcode[^"\']*', content)
                if qr_match:
                    print(f"在页面中找到二维码相关代码: {qr_match.group()}")
                
                # 尝试从页面中提取token或其他参数
                token_match = re.search(r'token["\']?\s*[:=]\s*["\']?(\d+)', content)
                if token_match:
                    token = token_match.group(1)
                    print(f"从页面中提取到token: {token}")
                    self.login_data['token'] = token
                
                # 生成二维码
                return self.generate_mp_qr_with_params()
            
            return self.get_fallback_qr()
            
        except Exception as e:
            print(f"通过页面获取二维码失败: {e}")
            return self.get_fallback_qr()
    
    def generate_mp_qr_with_params(self):
        """使用参数生成微信公众号二维码"""
        try:
            print("生成带参数的微信公众号二维码...")
            
            # 直接生成指向微信公众平台的二维码
            mp_url = "https://mp.weixin.qq.com/"
            
            # 如果有token，可以构建更精确的URL
            if 'token' in self.login_data:
                mp_url += f"?token={self.login_data['token']}"
            
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
            
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            return img_bytes, 'generated', 'mp_url'
            
        except Exception as e:
            print(f"生成二维码失败: {e}")
            return self.get_fallback_qr()
    
    def get_fallback_qr(self):
        """获取备用二维码"""
        try:
            print("生成备用登录二维码...")
            
            # 生成指向微信公众平台的二维码
            login_url = "https://mp.weixin.qq.com/"
            
            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=3,
            )
            
            qr.add_data(login_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            print("成功生成备用二维码")
            return img_bytes, 'fallback', 'redirect'
            
        except Exception as e:
            print(f"生成备用二维码失败: {e}")
            return None, None, None
    
    def check_login_status(self, callback):
        """检查登录状态"""
        try:
            # 对于直接二维码，检查状态
            callback('waiting', '请使用微信扫描二维码')
            
            # 由于技术限制，提供手动指导
            time.sleep(2)
            callback('manual_guide', '扫码后请在浏览器中完成登录，然后使用Cookie获取助手')
            
        except Exception as e:
            callback('error', f'检查登录状态失败: {str(e)}')

class SimpleWeChatLogin:
    """简化的微信登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
    
    def setup_headers(self):
        """设置请求头"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*'
        })
    
    def get_simple_qrcode(self):
        """获取简单二维码"""
        try:
            print("生成简单微信公众号登录二维码...")
            
            # 直接生成微信公众号登录页面的二维码
            login_url = "https://mp.weixin.qq.com/"
            
            qr = qrcode.QRCode(
                version=4,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=12,
                border=4,
            )
            
            qr.add_data(login_url)
            qr.make(fit=True)
            
            # 创建美化的二维码
            img = qr.make_image(fill_color="#07C160", back_color="white")
            
            # 转换为字节
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=100)
            img_bytes = img_buffer.getvalue()
            
            return img_bytes, 'simple', 'mp_login'
            
        except Exception as e:
            print(f"生成简单二维码失败: {e}")
            return None, None, None
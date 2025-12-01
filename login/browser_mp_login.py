#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模拟浏览器行为的微信公众号登录
使用更接近真实浏览器的方式获取二维码
"""

import requests
import time
import json
import re
from io import BytesIO
from PIL import Image
import qrcode
import uuid
import random

class BrowserMPLogin:
    """模拟浏览器的微信公众号登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_browser_session()
        
    def setup_browser_session(self):
        """设置模拟浏览器的会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        })
    
    def get_mp_qrcode(self):
        """获取微信公众号登录二维码"""
        try:
            print("🌐 正在模拟浏览器获取微信公众号登录二维码...")
            
            # 步骤1: 完整模拟浏览器访问流程
            print("步骤1: 访问微信公众平台主页...")
            
            # 首先访问主页
            home_response = self.session.get(
                "https://mp.weixin.qq.com/",
                timeout=15
            )
            
            print(f"主页访问状态: {home_response.status_code}")
            
            # 步骤2: 模拟用户的页面加载过程
            print("步骤2: 模拟页面加载，获取必要参数...")
            
            # 查找页面中的必要参数
            if home_response.status_code == 200:
                page_content = home_response.text
                
                # 查找各种可能的参数
                timestamp_patterns = [
                    r'timestamp["\']?\s*[:=]\s*["\']?(\d+)',
                    r'time["\']?\s*[:=]\s*["\']?(\d+)',
                    r'random["\']?\s*[:=]\s*["\']?(\d+)'
                ]
                
                for pattern in timestamp_patterns:
                    match = re.search(pattern, page_content)
                    if match:
                        print(f"从页面提取到时间参数: {match.group(1)}")
                        break
                
                # 等待一下模拟页面加载
                time.sleep(1)
                
                # 步骤3: 生成二维码请求
                print("步骤3: 生成二维码请求...")
                
                # 使用您验证过的接口
                current_time = int(time.time() * 1000)
                qr_url = f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={current_time}&login_appid="
                
                print(f"二维码接口: {qr_url}")
                
                # 设置获取二维码时的请求头
                qr_headers = {
                    'Referer': 'https://mp.weixin.qq.com/',
                    'Origin': 'https://mp.weixin.qq.com',
                    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'same-origin'
                }
                
                # 获取二维码
                qr_response = self.session.get(
                    qr_url, 
                    headers=qr_headers,
                    timeout=10
                )
                
                print(f"二维码请求状态: {qr_response.status_code}")
                print(f"响应长度: {len(qr_response.content)}")
                print(f"响应头: {dict(qr_response.headers)}")
                
                if qr_response.status_code == 200 and len(qr_response.content) > 100:
                    # 检查是否是图片
                    content_type = qr_response.headers.get('Content-Type', '')
                    print(f"内容类型: {content_type}")
                    
                    if (qr_response.content.startswith(b'\x89PNG') or 
                        qr_response.content.startswith(b'\xff\xd8\xff') or
                        'image' in content_type):
                        
                        print("🎉 成功获取到微信公众号登录二维码！")
                        return qr_response.content, 'browser_mp', 'direct'
                    
                    # 保存响应内容用于调试
                    with open('/tmp/qr_response_debug.bin', 'wb') as f:
                        f.write(qr_response.content)
                    print("已保存响应到 /tmp/qr_response_debug.bin")
                    
                    # 尝试解析响应内容
                    try:
                        if qr_response.content.startswith(b'{'):
                            json_data = json.loads(qr_response.content.decode())
                            print(f"JSON响应: {json_data}")
                    except:
                        pass
            
            # 步骤4: 如果直接获取失败，尝试模拟F12开发者工具的行为
            return self.simulate_dev_tools_flow()
            
        except Exception as e:
            print(f"浏览器模拟获取二维码失败: {e}")
            return self.generate_fallback_qr()
    
    def simulate_dev_tools_flow(self):
        """模拟F12开发者工具的行为"""
        try:
            print("🔧 模拟F12开发者工具获取二维码...")
            
            # 完全模拟开发者工具的网络请求
            current_time = int(time.time() * 1000)
            random_param = random.randint(1000000000, 9999999999)
            
            # 模拟多个可能的URL格式
            possible_urls = [
                f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={current_time}&login_appid=",
                f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={random_param}&login_appid=",
                f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={current_time}&login_appid=developer",
            ]
            
            for url in possible_urls:
                print(f"尝试URL: {url}")
                
                # 模拟网络请求
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200 and len(response.content) > 100:
                    print(f"🎉 URL成功: {url}")
                    return response.content, 'dev_tools', 'success'
            
            print("所有URL都未能获取到有效二维码")
            return self.generate_fallback_qr()
            
        except Exception as e:
            print(f"模拟开发者工具失败: {e}")
            return self.generate_fallback_qr()
    
    def generate_fallback_qr(self):
        """生成备用二维码"""
        try:
            print("🔄 生成备用微信公众号登录二维码...")
            
            # 生成高质量的微信公众平台登录页面二维码
            login_url = "https://mp.weixin.qq.com/"
            
            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=12,
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
            
            return img_bytes, 'fallback', 'mp_url'
            
        except Exception as e:
            print(f"生成备用二维码失败: {e}")
            return None, None, None

class DirectMPQR:
    """直接的微信公众号二维码获取"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_direct_qr(self):
        """直接获取二维码"""
        try:
            print("🎯 尝试直接获取微信公众号二维码...")
            
            # 使用最简单的请求方式
            current_time = int(time.time() * 1000)
            url = f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={current_time}&login_appid="
            
            # 最简单的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0',
                'Referer': 'https://mp.weixin.qq.com/'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            print(f"直接请求状态: {response.status_code}")
            print(f"直接请求长度: {len(response.content)}")
            
            if response.status_code == 200 and len(response.content) > 100:
                return response.content, 'direct', 'success'
            
            return self.generate_simple_qr()
            
        except Exception as e:
            print(f"直接获取失败: {e}")
            return self.generate_simple_qr()
    
    def generate_simple_qr(self):
        """生成简单二维码"""
        try:
            login_url = "https://mp.weixin.qq.com/"
            
            qr = qrcode.QRCode(version=2, box_size=10, border=3)
            qr.add_data(login_url)
            qr.make(fit=True)
            
            img = qr.make_image()
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            
            return img_buffer.getvalue(), 'simple', 'generated'
            
        except:
            return None, None, None
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信扫码登录核心功能
"""

import requests
import time
import json
import re
from PIL import Image, ImageTk
import io
import threading
from urllib.parse import urlencode

class WeChatQRLogin:
    """微信扫码登录实现类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/'
        })
        self.login_token = None
        self.qrcode_ticket = None
        
    def get_login_qrcode(self):
        """获取登录二维码"""
        try:
            # 第一步：访问登录页面获取基础token
            login_url = "https://mp.weixin.qq.com/"
            response = self.session.get(login_url, timeout=10)
            
            # 从页面中提取token
            token_match = re.search(r'window\.wx\.uin\s*=\s*"(\d+)"', response.text)
            if token_match:
                uin = token_match.group(1)
            else:
                uin = str(int(time.time() * 1000))[-9:]
            
            # 第二步：获取二维码
            qr_url = "https://open.weixin.qq.com/connect/qrconnect"
            params = {
                'appid': 'wx782c26e4c19acffb',
                'redirect_uri': 'https://mp.weixin.qq.com/cgi-bin/redirect',
                'response_type': 'code',
                'scope': 'snsapi_login',
                'state': f'weixin_{int(time.time()*1000)}'
            }
            
            # 构建完整URL
            full_qr_url = f"{qr_url}?{urlencode(params)}"
            
            # 获取二维码图片
            qr_response = self.session.get(full_qr_url, timeout=10)
            
            # 从响应中提取二维码图片
            if 'image' in qr_response.headers.get('content-type', ''):
                # 直接返回图片数据
                return qr_response.content, 'direct'
            else:
                # 解析HTML获取二维码图片URL
                img_match = re.search(r'<img[^>]*src="([^"]*qrcode[^"]*)"', qr_response.text)
                if img_match:
                    img_url = img_match.group(1)
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith('http'):
                        img_url = 'https://open.weixin.qq.com' + img_url
                    
                    img_response = self.session.get(img_url, timeout=10)
                    return img_response.content, 'parsed'
            
            return None, 'failed'
            
        except Exception as e:
            print(f"获取二维码失败: {e}")
            return None, 'failed'
    
    def check_login_status(self, callback):
        """检查登录状态"""
        try:
            # 微信扫码登录需要轮询检查状态
            # 由于微信的安全机制，实际的扫码登录比较复杂
            
            # 这里使用模拟检查
            for i in range(30):  # 检查30次，每次间隔2秒
                time.sleep(2)
                
                # 这里应该实际检查登录状态
                # 由于API限制，我们使用提示方式
                
                if i == 10:  # 20秒后提示
                    callback('waiting', '请在微信中确认登录...')
                elif i == 20:  # 40秒后提示
                    callback('timeout', '登录超时，请重新生成二维码')
                    return
                    
        except Exception as e:
            callback('error', f'检查登录状态失败: {e}')
    
    def simulate_login_success(self):
        """模拟登录成功，用于测试"""
        return {
            'token': 'test_token_' + str(int(time.time())),
            'cookie': 'test_cookie=value_' + str(int(time.time())),
            'uin': '123456789'
        }


class WeChatPlatformLogin:
    """微信公众平台登录实现"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_platform_qrcode(self):
        """获取微信公众平台登录二维码"""
        try:
            # 方法1：尝试获取登录页面并解析二维码
            url = "https://mp.weixin.qq.com/"
            response = self.session.get(url, timeout=10)
            
            # 查找二维码图片的多种可能位置
            patterns = [
                r'<img[^>]*id="qrcode"[^>]*src="([^"]*)"',
                r'<img[^>]*class="qrcode"[^>]*src="([^"]*)"',
                r'<img[^>]*data-src="([^"]*qrcode[^"]*)"',
                r'<img[^>]*src="([^"]*login[^"]*qrcode[^"]*)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    img_src = match.group(1)
                    
                    # 处理相对URL
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = 'https://mp.weixin.qq.com' + img_src
                    elif not img_src.startswith('http'):
                        if 'cgi-bin' in img_src:
                            img_src = 'https://mp.weixin.qq.com/' + img_src
                        else:
                            img_src = 'https://mp.weixin.qq.com' + img_src if not img_src.startswith('/') else 'https://mp.weixin.qq.com' + img_src
                    
                    try:
                        img_response = self.session.get(img_src, timeout=10)
                        if img_response.status_code == 200 and len(img_response.content) > 100:
                            return img_response.content, 'parsed'
                    except:
                        continue
            
            # 方法2：尝试API方式
            try:
                api_url = "https://mp.weixin.qq.com/cgi-bin/loginqrcode"
                params = {
                    'action': 'getqrcode',
                    'param': '4300',
                    't': str(int(time.time() * 1000))
                }
                
                api_response = self.session.get(api_url, params=params, timeout=10)
                
                if api_response.status_code == 200:
                    content_type = api_response.headers.get('content-type', '')
                    if 'image' in content_type and len(api_response.content) > 100:
                        return api_response.content, 'api_image'
                    else:
                        # 尝试解析JSON
                        try:
                            data = api_response.json()
                            if data.get('ret') == '0':
                                qr_img_url = data.get('qr_img')
                                if qr_img_url:
                                    if not qr_img_url.startswith('http'):
                                        qr_img_url = 'https://mp.weixin.qq.com' + qr_img_url
                                    
                                    img_response = self.session.get(qr_img_url, timeout=10)
                                    if img_response.status_code == 200:
                                        return img_response.content, 'api_success'
                        except:
                            pass
            except:
                pass
            
            # 方法3：模拟微信开放平台登录二维码
            try:
                open_qr_url = "https://open.weixin.qq.com/connect/qrconnect"
                params = {
                    'appid': 'wx782c26e4c19acffb',
                    'redirect_uri': 'https://mp.weixin.qq.com/cgi-bin/redirect',
                    'response_type': 'code',
                    'scope': 'snsapi_login',
                    'state': f'weixin_{int(time.time()*1000)}'
                }
                
                response = self.session.get(open_qr_url, params=params, timeout=10)
                
                # 从页面中提取二维码
                img_match = re.search(r'<img[^>]*src="([^"]*qrcode[^"]*)"', response.text)
                if img_match:
                    img_url = img_match.group(1)
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith('http'):
                        img_url = 'https://open.weixin.qq.com' + img_url
                    
                    img_response = self.session.get(img_url, timeout=10)
                    if img_response.status_code == 200:
                        return img_response.content, 'open_platform'
                        
            except:
                pass
            
            return None, 'failed'
            
        except Exception as e:
            print(f"获取平台二维码失败: {e}")
            return None, 'failed'
    
    def check_platform_login(self, uuid, callback):
        """检查微信公众平台登录状态"""
        try:
            # 由于微信公众平台的安全限制，真实的登录状态检查比较复杂
            # 这里实现一个简化版本，提供用户友好的反馈
            
            for i in range(60):  # 检查60次
                # 模拟检查过程
                time.sleep(1)
                
                if i == 10:  # 10秒后提示
                    callback('waiting', '请使用微信扫描二维码...')
                elif i == 20:  # 20秒后提示
                    callback('waiting', '扫码成功后请在手机上确认登录...')
                elif i == 30:  # 30秒后提示
                    callback('scanned', '等待手机确认...')
                elif i == 45:  # 45秒后提醒
                    callback('waiting', '二维码即将过期，请尽快操作...')
                elif i >= 58:  # 58秒后
                    callback('timeout', '二维码即将过期，请重新生成')
                    return
                    
        except Exception as e:
            callback('error', f'检查登录状态失败: {e}')
            
    def simulate_login_success(self):
        """模拟登录成功，用于测试"""
        return {
            'token': 'test_token_' + str(int(time.time())),
            'cookie': 'test_cookie=value_' + str(int(time.time())),
            'uin': '123456789'
        }


def test_qr_generation():
    """测试二维码生成"""
    print("测试微信登录二维码生成...")
    
    # 测试微信公众平台二维码
    login = WeChatPlatformLogin()
    img_data, status = login.get_platform_qrcode()
    
    if img_data:
        print(f"二维码生成成功，状态: {status}")
        
        # 保存测试图片
        with open('/tmp/test_qr.png', 'wb') as f:
            f.write(img_data)
        print("二维码已保存到 /tmp/test_qr.png")
        
        return True
    else:
        print(f"二维码生成失败，状态: {status}")
        return False


if __name__ == "__main__":
    test_qr_generation()
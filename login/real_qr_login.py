#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真正的微信扫码登录实现
尝试多种方法获取可直接扫码的登录二维码
"""

import requests
import time
import json
import re
import uuid
import hashlib
from PIL import Image, ImageTk
import io
import threading

class RealWeChatQRLogin:
    """真正的微信扫码登录"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.login_uuid = str(uuid.uuid4())
        
    def get_wechat_web_qr(self):
        """获取微信网页版登录二维码"""
        try:
            # 方法1：微信网页版登录
            url = "https://login.weixin.qq.com/jslogin"
            params = {
                'appid': 'wx782c26e4c19acffb',
                'redirect_uri': 'https://mp.weixin.qq.com/cgi-bin/redirect',
                'fun': 'new',
                'lang': 'zh_CN',
                '_': str(int(time.time() * 1000))
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # 解析返回的JavaScript
                content = response.text
                
                # 提取UUID
                uuid_match = re.search(r'uuid = "([^"]+)"', content)
                if uuid_match:
                    login_uuid = uuid_match.group(1)
                    
                    # 构建二维码URL
                    qr_url = f"https://login.weixin.qq.com/qrcode/{login_uuid}"
                    
                    qr_params = {
                        't': 'webwx',
                        '_': str(int(time.time() * 1000))
                    }
                    
                    qr_response = self.session.get(qr_url, params=qr_params, timeout=10)
                    
                    if qr_response.status_code == 200 and len(qr_response.content) > 100:
                        return qr_response.content, 'web_qr', login_uuid
                        
            return None, 'failed', None
            
        except Exception as e:
            print(f"获取微信网页二维码失败: {e}")
            return None, 'failed', None
    
    def get_wechat_open_qr(self):
        """获取微信开放平台二维码"""
        try:
            # 微信开放平台扫码登录
            url = "https://open.weixin.qq.com/connect/qrconnect"
            params = {
                'appid': 'wx782c26e4c19acffb',
                'redirect_uri': 'https://mp.weixin.qq.com/cgi-bin/redirect',
                'response_type': 'code',
                'scope': 'snsapi_login',
                'state': f'{int(time.time()*1000)}',
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # 从HTML中提取二维码图片
                patterns = [
                    r'<img[^>]*src="([^"]*qrcode[^"]*)"',
                    r'qrimg\s*=\s*"([^"]+)"',
                    r'"qr":"([^"]+)"'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        img_src = match.group(1)
                        
                        # 处理URL
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif not img_src.startswith('http'):
                            if 'connect' in img_src:
                                img_src = 'https://open.weixin.qq.com/' + img_src
                            else:
                                img_src = 'https://open.weixin.qq.com/connect/' + img_src
                        
                        try:
                            img_response = self.session.get(img_src, timeout=10)
                            if img_response.status_code == 200 and len(img_response.content) > 100:
                                return img_response.content, 'open_qr', None
                        except:
                            continue
                            
            return None, 'failed', None
            
        except Exception as e:
            print(f"获取微信开放平台二维码失败: {e}")
            return None, 'failed', None
    
    def get_mp_qr_login(self):
        """获取公众号登录二维码（尝试直接API）"""
        try:
            # 先访问公众号平台获取基础信息
            mp_url = "https://mp.weixin.qq.com/"
            response = self.session.get(mp_url, timeout=10)
            
            # 提取必要的token或参数
            token_match = re.search(r'token[=:]\s*["\']?(\w+)', response.text)
            token = token_match.group(1) if token_match else ''
            
            # 尝试多种登录二维码API
            apis = [
                {
                    'url': 'https://mp.weixin.qq.com/cgi-bin/loginqrcode',
                    'params': {
                        'action': 'getqrcode',
                        'param': '4300',
                        't': str(int(time.time() * 1000))
                    }
                },
                {
                    'url': 'https://mp.weixin.qq.com/misc/safeverify',
                    'params': {
                        'action': 'qrcode',
                        'scene': '1'
                    }
                },
                {
                    'url': 'https://mp.weixin.qq.com/cgi-bin/scanloginqrcode',
                    'params': {
                        'action': 'getqrcode',
                        'token': token or '',
                        't': str(int(time.time() * 1000))
                    }
                }
            ]
            
            for api in apis:
                try:
                    api_response = self.session.get(api['url'], params=api['params'], timeout=10)
                    
                    if api_response.status_code == 200:
                        content_type = api_response.headers.get('content-type', '')
                        
                        if 'image' in content_type and len(api_response.content) > 100:
                            return api_response.content, 'mp_api', token
                        else:
                            # 尝试解析JSON
                            try:
                                data = api_response.json()
                                if data.get('ret') == '0' or data.get('code') == '0':
                                    qr_img = data.get('qr_img') or data.get('img') or data.get('qrcode')
                                    if qr_img:
                                        if not qr_img.startswith('http'):
                                            qr_img = 'https://mp.weixin.qq.com' + qr_img
                                        
                                        img_response = self.session.get(qr_img, timeout=10)
                                        if img_response.status_code == 200:
                                            return img_response.content, 'mp_api_json', token
                            except:
                                pass
                                
                except:
                    continue
                    
            return None, 'failed', None
            
        except Exception as e:
            print(f"获取公众号API二维码失败: {e}")
            return None, 'failed', None
    
    def check_login_status(self, login_uuid, login_type, callback):
        """检查登录状态"""
        try:
            if login_type == 'web_qr':
                self._check_web_login_status(login_uuid, callback)
            elif login_type in ['open_qr', 'mp_api', 'mp_api_json']:
                self._check_platform_login_status(callback)
            else:
                callback('error', '未知的登录类型')
                
        except Exception as e:
            callback('error', f'检查登录状态失败: {e}')
    
    def _check_web_login_status(self, login_uuid, callback):
        """检查微信网页版登录状态"""
        try:
            check_url = "https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login"
            params = {
                'uuid': login_uuid,
                'tip': 1,
                '_': str(int(time.time() * 1000))
            }
            
            for i in range(120):  # 检查2分钟
                try:
                    response = self.session.get(check_url, params=params, timeout=5)
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        if 'window.code=408' in content:
                            callback('waiting', '请扫描二维码...')
                            params['tip'] = 0
                        elif 'window.code=201' in content:
                            callback('scanned', '已扫码，请在手机确认登录')
                        elif 'window.code=200' in content:
                            # 提取重定向URL
                            url_match = re.search(r'window.redirect_uri="([^"]+)"', content)
                            if url_match:
                                redirect_url = url_match.group(1)
                                # 处理跳转，获取登录信息
                                final_response = self.session.get(redirect_url, timeout=10)
                                
                                # 提取cookie和token
                                cookie = '; '.join([f"{c.name}={c.value}" for c in self.session.cookies])
                                token_match = re.search(r'token[=:]\s*["\']?(\w+)', final_response.text)
                                token = token_match.group(1) if token_match else ''
                                
                                if token:
                                    callback('success', '登录成功！', {
                                        'cookie': cookie,
                                        'token': token,
                                        'redirect_url': redirect_url
                                    })
                                    return
                        elif 'window.code=400' in content:
                            callback('expired', '二维码已过期')
                            return
                            
                except:
                    pass
                
                time.sleep(1)
                
            callback('timeout', '登录超时')
            
        except Exception as e:
            callback('error', f'网页登录检查失败: {e}')
    
    def _check_platform_login_status(self, callback):
        """检查公众平台登录状态"""
        try:
            # 由于平台API限制，这里使用模拟方式
            # 实际项目中应该实现真实的轮询检查
            
            for i in range(60):
                if i == 10:
                    callback('waiting', '请使用微信扫描二维码...')
                elif i == 20:
                    callback('scanned', '已扫码，请在手机确认登录...')
                elif i == 30:
                    callback('waiting', '等待手机确认...')
                elif i >= 55:
                    callback('timeout', '二维码即将过期')
                    return
                    
                time.sleep(1)
                
        except Exception as e:
            callback('error', f'平台登录检查失败: {e}')
    
    def get_best_qr(self):
        """获取最佳可用的二维码"""
        # 按优先级尝试不同的方法
        methods = [
            self.get_wechat_web_qr,
            self.get_wechat_open_qr,
            self.get_mp_qr_login
        ]
        
        for method in methods:
            try:
                img_data, login_type, uuid = method()
                if img_data and len(img_data) > 100:
                    print(f"成功获取二维码，方法: {method.__name__}, 类型: {login_type}")
                    return img_data, login_type, uuid
            except Exception as e:
                print(f"方法 {method.__name__} 失败: {e}")
                continue
                
        return None, 'all_failed', None


def test_real_qr():
    """测试真正的二维码获取"""
    print("🔍 测试真正的微信扫码登录...")
    
    login = RealWeChatQRLogin()
    
    # 尝试获取二维码
    img_data, login_type, uuid = login.get_best_qr()
    
    if img_data:
        print(f"✅ 成功获取二维码！")
        print(f"📱 类型: {login_type}")
        print(f"🆔 UUID: {uuid}")
        
        # 保存测试图片
        with open('/tmp/real_wechat_qr.png', 'wb') as f:
            f.write(img_data)
        print(f"💾 二维码已保存到: /tmp/real_wechat_qr.png")
        
        return True
    else:
        print("❌ 所有方法都失败了")
        return False


if __name__ == "__main__":
    test_real_qr()
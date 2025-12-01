#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试简单登录功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from simple_mp_login import SimpleMPLogin
from PIL import Image, ImageTk
from io import BytesIO

class SimpleLoginTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("微信公众号登录测试")
        self.root.geometry("400x600")
        
        self.simple_mp_login = None
        
        self.create_ui()
        
    def create_ui(self):
        # 标题
        title = ttk.Label(self.root, text="微信公众号登录测试", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # 二维码显示区域
        self.qr_label = ttk.Label(self.root, text="点击生成二维码", width=30, background="lightgray")
        self.qr_label.pack(pady=20)
        
        # 按钮
        self.generate_btn = ttk.Button(self.root, text="生成二维码", command=self.generate_qr)
        self.generate_btn.pack(pady=10)
        
        # 账号密码登录区域
        login_frame = ttk.LabelFrame(self.root, text="账号密码登录", padding=20)
        login_frame.pack(pady=20, padx=20, fill='x')
        
        ttk.Label(login_frame, text="账号:").grid(row=0, column=0, sticky='e', pady=5)
        self.username_entry = ttk.Entry(login_frame, width=20)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, sticky='e', pady=5)
        self.password_entry = ttk.Entry(login_frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        self.password_btn = ttk.Button(login_frame, text="登录", command=self.test_password_login)
        self.password_btn.grid(row=2, column=1, pady=10, sticky='e')
        
        # 状态显示
        self.status_label = ttk.Label(self.root, text="就绪", background="lightyellow")
        self.status_label.pack(pady=10, fill='x')
        
    def generate_qr(self):
        """生成二维码"""
        try:
            if not self.simple_mp_login:
                self.simple_mp_login = SimpleMPLogin()
            
            self.status_label.config(text="正在生成二维码...")
            
            img_data, method, login_type = self.simple_mp_login.get_login_qrcode()
            
            if img_data and len(img_data) > 100:
                # 显示二维码
                img = Image.open(BytesIO(img_data))
                img = img.resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                
                self.qr_label.config(image=photo, text="")
                self.qr_label.image = photo  # 保持引用
                
                self.status_label.config(text=f"二维码生成成功 - 方法: {method}, 类型: {login_type}")
            else:
                self.status_label.config(text="生成二维码失败")
                
        except Exception as e:
            self.status_label.config(text=f"错误: {str(e)}")
            
    def test_password_login(self):
        """测试密码登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入账号和密码")
            return
        
        try:
            if not self.simple_mp_login:
                self.simple_mp_login = SimpleMPLogin()
            
            self.status_label.config(text="正在登录...")
            self.password_btn.config(state='disabled')
            
            result = self.simple_mp_login.login_with_password(username, password)
            
            if result.get('success'):
                self.status_label.config(text="登录成功！")
                messagebox.showinfo("成功", f"登录成功！\nToken: {result.get('token', '')[:20]}...")
            else:
                self.status_label.config(text=f"登录失败: {result.get('message', '')}")
                messagebox.showerror("失败", result.get('message', '登录失败'))
                
        except Exception as e:
            self.status_label.config(text=f"登录错误: {str(e)}")
            messagebox.showerror("错误", str(e))
            
        finally:
            self.password_btn.config(state='normal')
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleLoginTest()
    app.run()
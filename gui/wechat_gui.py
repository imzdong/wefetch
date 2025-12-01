#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号文章下载器 - GUI版本
支持跨平台图形界面操作
"""

import tkinter as tk
import os
import time
import random
import threading
import json
import requests
import webbrowser
import qrcode
from io import BytesIO
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
from PIL import Image, ImageTk
from urllib.parse import quote
from core.wechat_downloader_core import WeChatArticleDownloader
from login.wechat_login import WeChatPlatformLogin
from login.real_qr_login import RealWeChatQRLogin
from login.working_wechat_login import WorkingWeChatLogin
from login.selenium_wechat_login import SeleniumWeChatLogin
from data.cookie_helper import create_cookie_helper_window
from bs4 import BeautifulSoup

class WeChatDownloaderGUI:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        self.root.title("微信公众号文章下载器")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        

        
        # 设置应用图标
        self.set_app_icon()
        
        # 设置样式
        self.setup_styles()
        
        # 配置信息
        self.config = {
            'cookie': '',
            'token': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }
        
        # 下载器实例
        self.downloader = None
        
        # 微信登录实例
        self.working_login = None
        self.selenium_login = None
        
        # 登录状态
        self.login_uuid = None
        self.login_type = None
        
        # 当前选中的公众号信息
        self.current_account = None
        
        # 导出控制
        self.exporting = False
        self.stop_export_flag = False
        
        # 创建主界面
        self.create_main_interface()
        
    def set_app_icon(self):
        """设置应用图标"""
        try:
            # 优先级：专用图标 > 标准图标 > 备用图标
            icon_files = [
                'wechat_downloader.png',      # macOS专用图标
                'app_icon.png',              # 通用PNG图标  
                'wechat_downloader.ico',      # Windows ICO图标
                'app_icon.ico',              # 通用ICO图标
                'icon_64x64.png',           # 备用图标
                'icon_48x48.png',
                'icon_32x32.png'
            ]
            
            for icon_file in icon_files:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', icon_file)
                if os.path.exists(icon_path):
                    try:
                        if icon_file.endswith('.ico'):
                            # ICO文件使用iconbitmap方法
                            self.root.iconbitmap(icon_path)
                            print(f"✅ 应用图标加载成功 (ICO: {icon_file})")
                            return
                        else:
                            # PNG文件使用iconphoto方法
                            icon = ImageTk.PhotoImage(file=icon_path)
                            self.root.iconphoto(True, icon)
                            print(f"✅ 应用图标加载成功 (PNG: {icon_file})")
                            return
                    except Exception as e:
                        print(f"⚠️ 加载 {icon_file} 失败: {e}")
                        continue
            
            print("⚠️ 未找到可用的图标文件，使用默认图标")
            
        except Exception as e:
            print(f"⚠️ 设置图标失败: {e}")
            # 不影响程序运行，只打印警告
        
        # 配置信息
        self.config = {
            'cookie': '',
            'token': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }
        
        # 下载器实例
        self.downloader = None
        
        # 微信登录实例
        self.working_login = None
        self.selenium_login = None
        
        # 登录状态
        self.login_uuid = None
        self.login_type = None
        
        # 当前选中的公众号信息
        self.current_account = None
        
        # 导出控制
        self.exporting = False
        self.stop_export_flag = False
        
        # 创建主界面
        self.create_main_interface()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用跨平台主题
        
        # 配置样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Heading.TLabel', font=('Microsoft YaHei', 10, 'bold'))
        
    def create_main_interface(self):
        """创建主界面"""
        # 创建笔记本组件（选项卡）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个选项卡
        self.create_login_tab()
        self.create_search_tab()
        self.create_articles_tab()
        self.create_export_tab()
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_login_tab(self):
        """创建登录选项卡"""
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="登录")
        
        # 主容器
        main_container = ttk.Frame(self.login_frame)
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_container, text="微信公众号登录", style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # 登录方式选择
        login_type_frame = ttk.LabelFrame(main_container, text="选择登录方式", padding=20)
        login_type_frame.pack(fill='x', pady=(0, 20))
        
        self.login_method = tk.StringVar(value="qr")
        
        qr_radio = ttk.Radiobutton(login_type_frame, text="扫码登录（推荐）", 
                                   variable=self.login_method, value="qr",
                                   command=self.switch_login_method)
        qr_radio.pack(anchor='w', pady=5)
        
        manual_radio = ttk.Radiobutton(login_type_frame, text="手动配置（Token/Cookie）", 
                                     variable=self.login_method, value="manual",
                                     command=self.switch_login_method)
        manual_radio.pack(anchor='w', pady=5)
        

        
 # 扫码登录区域
        self.qr_frame = ttk.LabelFrame(main_container, text="扫码登录", padding=20)
        self.qr_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.qr_label = ttk.Label(self.qr_frame, text="点击启动浏览器扫码登录")
        self.qr_label.pack(pady=20)
        
        self.generate_qr_btn = ttk.Button(self.qr_frame, text="启动扫码登录", 
                                          command=self.start_selenium_login)
        self.generate_qr_btn.pack(pady=10)
        

        
        # 登录状态
        self.login_status_label = ttk.Label(main_container, text="未登录", foreground="red")
        self.login_status_label.pack(pady=10)
        
        # 帮助按钮
        help_frame = ttk.Frame(main_container)
        help_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(help_frame, text="📖 需要帮助？").pack(side='left', padx=(0, 10))
        self.help_btn = ttk.Button(help_frame, text="详细登录指导", 
                                  command=self.open_login_guide)
        self.help_btn.pack(side='left', padx=(0, 10))
        
        self.helper_btn = ttk.Button(help_frame, text="Cookie获取助手", 
                                  command=self.open_cookie_helper)
        self.helper_btn.pack(side='left')
        
        # 手动输入token区域
        self.manual_frame = ttk.LabelFrame(main_container, text="手动配置", padding=20)
        
        ttk.Label(self.manual_frame, text="Cookie:").grid(row=0, column=0, sticky='nw', pady=5)
        self.cookie_text = scrolledtext.ScrolledText(self.manual_frame, height=3, width=60)
        self.cookie_text.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(self.manual_frame, text="Token:").grid(row=1, column=0, sticky='e', pady=5)
        self.token_entry = ttk.Entry(self.manual_frame, width=60)
        self.token_entry.grid(row=1, column=1, pady=5, padx=(10, 0), sticky='ew')
        
        self.manual_frame.columnconfigure(1, weight=1)
        
        config_btn_frame = ttk.Frame(self.manual_frame)
        config_btn_frame.grid(row=2, column=1, pady=10, sticky='ew')
        
        self.save_config_btn = ttk.Button(config_btn_frame, text="保存配置", 
                                       command=self.save_manual_config)
        self.save_config_btn.pack(side='right', padx=(10, 0))
        
        self.clear_config_btn = ttk.Button(config_btn_frame, text="清除配置", 
                                        command=self.clear_manual_config)
        self.clear_config_btn.pack(side='right')
        
        # 初始时隐藏其他登录区域
        self.switch_login_method()
        
        # 设置窗口关闭行为
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.quit())
    

        
    def create_search_tab(self):
        """创建搜索选项卡"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="搜索公众号")
        
        # 主容器
        main_container = ttk.Frame(self.search_frame)
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 搜索区域
        search_frame = ttk.LabelFrame(main_container, text="搜索公众号", padding=20)
        search_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(search_frame, text="公众号名称:").pack(side='left', padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_accounts())
        
        self.search_btn = ttk.Button(search_frame, text="搜索", command=self.search_accounts)
        self.search_btn.pack(side='left')
        
        # 搜索结果区域
        result_frame = ttk.LabelFrame(main_container, text="搜索结果", padding=10)
        result_frame.pack(fill='both', expand=True)
        
        # 创建Treeview显示搜索结果
        columns = ('nickname', 'alias', 'signature')
        self.accounts_tree = ttk.Treeview(result_frame, columns=columns, show='tree headings', height=15)
        
        self.accounts_tree.heading('#0', text='FakeID')
        self.accounts_tree.heading('nickname', text='公众号名称')
        self.accounts_tree.heading('alias', text='别名')
        self.accounts_tree.heading('signature', text='简介')
        
        self.accounts_tree.column('#0', width=200)
        self.accounts_tree.column('nickname', width=150)
        self.accounts_tree.column('alias', width=100)
        self.accounts_tree.column('signature', width=300)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.accounts_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 双击选择公众号
        self.accounts_tree.bind('<Double-Button-1>', self.select_account)
        
        # 选择按钮
        select_btn_frame = ttk.Frame(main_container)
        select_btn_frame.pack(fill='x', pady=(10, 0))
        
        self.select_account_btn = ttk.Button(select_btn_frame, text="选择该公众号", 
                                            command=self.select_account_from_tree)
        self.select_account_btn.pack(side='right')
        
    def create_articles_tab(self):
        """创建文章列表选项卡"""
        self.articles_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.articles_frame, text="文章列表")
        
        # 主容器
        main_container = ttk.Frame(self.articles_frame)
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 公众号信息显示
        info_frame = ttk.LabelFrame(main_container, text="当前公众号", padding=10)
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.account_info_label = ttk.Label(info_frame, text="未选择公众号", style='Heading.TLabel')
        self.account_info_label.pack()
        
        # 文章列表区域
        articles_frame = ttk.LabelFrame(main_container, text="文章列表", padding=10)
        articles_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # 创建Treeview显示文章列表
        columns = ('title', 'create_time', 'link')
        self.articles_tree = ttk.Treeview(articles_frame, columns=columns, show='tree headings', height=20)
        
        self.articles_tree.heading('#0', text='ID')
        self.articles_tree.heading('title', text='标题')
        self.articles_tree.heading('create_time', text='发布时间')
        self.articles_tree.heading('link', text='链接')
        
        self.articles_tree.column('#0', width=80)
        self.articles_tree.column('title', width=300)
        self.articles_tree.column('create_time', width=150)
        self.articles_tree.column('link', width=200)
        
        # 滚动条
        articles_scrollbar = ttk.Scrollbar(articles_frame, orient='vertical', command=self.articles_tree.yview)
        self.articles_tree.configure(yscrollcommand=articles_scrollbar.set)
        
        self.articles_tree.pack(side='left', fill='both', expand=True)
        articles_scrollbar.pack(side='right', fill='y')
        
        # 分页控制
        pagination_frame = ttk.Frame(main_container)
        pagination_frame.pack(fill='x')
        
        self.page_label = ttk.Label(pagination_frame, text="第 1 页")
        self.page_label.pack(side='left', padx=(0, 20))
        
        self.prev_btn = ttk.Button(pagination_frame, text="上一页", command=self.prev_page)
        self.prev_btn.pack(side='left', padx=(0, 10))
        
        self.next_btn = ttk.Button(pagination_frame, text="下一页", command=self.next_page)
        self.next_btn.pack(side='left')
        
        self.current_page = 1
        self.total_pages = 1
        
    def create_export_tab(self):
        """创建导出选项卡"""
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="导出设置")
        
        # 主容器
        main_container = ttk.Frame(self.export_frame)
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 导出设置
        settings_frame = ttk.LabelFrame(main_container, text="导出设置", padding=20)
        settings_frame.pack(fill='x', pady=(0, 20))
        
        # 导出格式
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(format_frame, text="导出格式:").pack(side='left')
        self.export_format = tk.StringVar(value="markdown")
        ttk.Radiobutton(format_frame, text="Markdown", variable=self.export_format, 
                       value="markdown").pack(side='left', padx=(10, 5))
        ttk.Radiobutton(format_frame, text="HTML", variable=self.export_format, 
                       value="html").pack(side='left', padx=(0, 5))
        
        # 输出目录
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(dir_frame, text="输出目录:").pack(side='left')
        self.output_dir = tk.StringVar(value="./articles")
        ttk.Entry(dir_frame, textvariable=self.output_dir, width=50).pack(side='left', padx=(10, 5))
        ttk.Button(dir_frame, text="选择", command=self.choose_output_dir).pack(side='left')
        
        # 导出选项
        options_frame = ttk.LabelFrame(main_container, text="导出选项", padding=20)
        options_frame.pack(fill='x', pady=(0, 20))
        
        self.download_images = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="下载图片到本地", 
                       variable=self.download_images).pack(anchor='w', pady=5)
        
        self.include_original_link = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含原始链接", 
                       variable=self.include_original_link).pack(anchor='w', pady=5)
        
        # 导出按钮
        export_btn_frame = ttk.Frame(main_container)
        export_btn_frame.pack(fill='x', pady=(20, 0))
        
        self.export_single_btn = ttk.Button(export_btn_frame, text="导出选中文章", 
                                           command=self.export_selected_articles)
        self.export_single_btn.pack(side='left', padx=(0, 10))
        
        self.export_all_btn = ttk.Button(export_btn_frame, text="导出所有文章", 
                                         command=self.export_all_articles)
        self.export_all_btn.pack(side='left', padx=(0, 10))
        
        self.stop_export_btn = ttk.Button(export_btn_frame, text="停止导出", 
                                         command=self.stop_export, state='disabled')
        self.stop_export_btn.pack(side='left')
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_container, text="导出进度", padding=10)
        progress_frame.pack(fill='x', pady=(20, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="就绪")
        self.progress_label.pack()
        
    def switch_login_method(self):
        """切换登录方式"""
        method = self.login_method.get()
        # 隐藏所有登录区域
        self.qr_frame.pack_forget()
        self.manual_frame.pack_forget()
        
        if method == "qr":
            self.qr_frame.pack(fill='both', expand=True, pady=(0, 20))
        elif method == "manual":
            self.manual_frame.pack(fill='x', pady=(0, 20))
        else:
            # 默认显示扫码登录
            self.qr_frame.pack(fill='both', expand=True, pady=(0, 20))
            
    def open_login_guide(self):
        """打开登录指导页面"""
        try:
            # 获取当前脚本的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            guide_path = os.path.join(current_dir, 'login_guide.html')
            
            if os.path.exists(guide_path):
                # 在默认浏览器中打开指导页面
                webbrowser.open(f'file://{guide_path}')
            else:
                # 如果本地文件不存在，打开网页版指导
                webbrowser.open('https://mp.weixin.qq.com/')
                self.show_info("登录指导页面已打开浏览器")
        except Exception as e:
            self.show_error(f"无法打开指导页面: {str(e)}")
            
    def open_cookie_helper(self):
        """打开Cookie获取助手"""
        try:
            create_cookie_helper_window()
        except Exception as e:
            self.show_error(f"无法打开助手工具: {str(e)}")
    
    def open_mp_login_page(self):
        """一键打开微信公众平台登录页面"""
        try:
            import webbrowser
            login_url = "https://mp.weixin.qq.com/"
            webbrowser.open(login_url)
            self.update_status("已打开微信公众平台登录页面")
            self.show_info("✅ 已在浏览器中打开微信公众平台登录页面\n\n请按照以下步骤操作：\n1. 使用微信扫描页面上的登录二维码\n2. 在手机微信中确认登录\n3. 登录成功后使用'Cookie获取助手'获取配置信息")
        except Exception as e:
            self.show_error(f"无法打开登录页面: {str(e)}")
            # 备用方案：复制URL到剪贴板
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append("https://mp.weixin.qq.com/")
                self.show_info("✅ 已复制登录链接到剪贴板\n请在浏览器中粘贴访问：https://mp.weixin.qq.com/")
            except:
                self.show_info("请手动在浏览器中访问：https://mp.weixin.qq.com/")
            
    def clear_manual_config(self):
        """清除手动配置"""
        if messagebox.askyesno("确认清除", "确定要清除当前的Cookie和Token配置吗？"):
            self.cookie_text.delete("1.0", tk.END)
            self.token_entry.delete(0, tk.END)
            self.config['cookie'] = ''
            self.config['token'] = ''
            
            # 重置下载器
            if self.downloader:
                try:
                    self.downloader.session.headers.pop("Cookie", None)
                except:
                    pass
            
            self.login_status_label.config(text="未登录", foreground="red")
            self.update_status("配置已清除")
            
            # 显示清除成功弹窗
            messagebox.showinfo("清除成功", "✅ 配置已成功清除！\n\n"
                              "Cookie和Token已清空\n"
                              "下载器配置已重置\n\n"
                              "如需使用请重新登录或配置。")
            
    def update_status(self, message):
        """更新状态栏"""
        self.status_bar.config(text=message)
        self.root.update()
        
    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        
    def show_info(self, message):
        """显示信息"""
        messagebox.showinfo("信息", message)
        
    def start_selenium_login(self):
        """启动Selenium扫码登录"""
        try:
            self.update_status("正在启动浏览器进行扫码登录...")
            self.generate_qr_btn.config(state='disabled', text="启动中...")
            
            # 创建Selenium登录实例
            if not self.selenium_login:
                self.selenium_login = SeleniumWeChatLogin()
            
            # 启动扫码登录
            result = self.selenium_login.login_with_qr_code(self.selenium_status_callback)
            
            if result.get('success'):
                self.update_status("浏览器已启动，请在浏览器中扫码登录")
                self.qr_label.config(text="🌐 浏览器已启动，请在浏览器中扫码登录")
                
                # 显示操作指导
                guide_text = """🌐 Selenium扫码登录已启动

✅ 浏览器已自动打开微信公众号登录页面
📱 请在浏览器中使用微信扫描二维码
⚡ 扫码后手机确认即可完成登录
🔄 程序会自动检测登录状态

💡 优势：
• 无需手动配置Cookie和Token
• 一次登录，可保存凭据下次使用
• 模拟真实用户行为，更稳定可靠
• 支持所有微信公众号账号类型

⏱️ 请在5分钟内完成扫码操作..."""
                
                if hasattr(self, 'guide_label'):
                    self.guide_label.config(text=guide_text)
                else:
                    self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                               justify='left', font=('Microsoft YaHei', 9))
                    self.guide_label.pack(pady=10)
                    
            else:
                self.show_error(f"启动扫码登录失败: {result.get('message', '未知错误')}")
                self.update_status("启动扫码登录失败")
                
        except Exception as e:
            self.show_error(f"启动扫码登录失败: {str(e)}")
            self.update_status("启动扫码登录失败")
            
        finally:
            self.generate_qr_btn.config(state='normal', text="启动扫码登录")
    

    

    
    def selenium_status_callback(self, status, message):
        """Selenium登录状态回调"""
        # 在主线程中更新UI
        self.root.after(0, lambda: self.handle_selenium_status(status, message))
    
    def handle_selenium_status(self, status, message):
        """处理Selenium登录状态"""
        if status == "waiting":
            self.update_status(f"⏳ {message}")
            self.qr_label.config(text=f"⏳ {message}")
        elif status == "scanned":
            self.update_status(f"🎯 {message}")
            self.qr_label.config(text=f"🎯 {message}")
        elif status == "success":
            self.update_status(f"✅ {message}")
            self.qr_label.config(text=f"✅ {message}")
            
            # 立即获取登录凭据并配置到系统中
            if self.selenium_login:
                try:
                    credentials = self.selenium_login.extract_login_credentials()
                    if credentials.get('success'):
                        token = credentials.get('token')
                        cookie = credentials.get('cookie')
                        
                        if token and cookie:
                            self.config['token'] = token
                            self.config['cookie'] = cookie
                            self.login_status_label.config(text="已登录", foreground="green")
                            self.show_info(f"🎉 {message}\n✅ 登录凭据已自动配置\n🎯 现在可以搜索公众号了")
                            
                            # 更新手动配置区域的显示
                            self.cookie_text.delete("1.0", tk.END)
                            self.cookie_text.insert("1.0", cookie)
                            self.token_entry.delete(0, tk.END)
                            self.token_entry.insert(0, token)
                            
                        else:
                            self.login_status_label.config(text="登录成功，但凭据获取失败", foreground="orange")
                            self.show_info(f"🎉 {message}\n⚠️ 部分凭据获取失败，请手动配置")
                    else:
                        self.login_status_label.config(text="登录成功，但凭据提取失败", foreground="orange")
                        self.show_info(f"🎉 {message}\n⚠️ 凭据提取失败: {credentials.get('message', '未知错误')}")
                except Exception as e:
                    self.login_status_label.config(text="登录成功，但凭据配置失败", foreground="orange")
                    self.show_info(f"🎉 {message}\n⚠️ 凭据配置异常: {str(e)}")
            else:
                self.login_status_label.config(text="已登录", foreground="green")
                self.show_info(f"🎉 {message}")
            
            # 关闭浏览器（可选，或者保持打开状态）
            # if self.selenium_login:
            #     self.selenium_login.close_driver()
                
        elif status == "timeout":
            self.show_error(f"⏰ {message}")
            self.update_status("登录超时")
            self.qr_label.config(text="⏰ 登录超时，请重新尝试")
            
        elif status == "error":
            self.show_error(f"❌ {message}")
            self.update_status(f"登录失败: {message}")
            self.qr_label.config(text=f"❌ {message}")
    
    def generate_qr_code(self):
        """生成二维码（保留原有功能作为备用）"""
        try:
            self.update_status("正在获取微信公众号登录二维码...")
            self.generate_qr_btn.config(state='disabled', text="获取中...")
            
            # 在新线程中获取公众号二维码
            threading.Thread(target=self.get_mp_wechat_qr, daemon=True).start()
            
        except Exception as e:
            self.show_error(f"生成二维码失败: {str(e)}")
            self.update_status("生成二维码失败")
            self.generate_qr_btn.config(state='normal', text="生成二维码")
            
    def get_mp_wechat_qr(self):
        """获取微信公众号登录二维码 - 基于您提供的正确实现"""
        try:
            self.update_status("正在获取微信公众号登录二维码...")
            self.generate_qr_btn.config(state='disabled', text="获取中...")
            
            # 使用真正可用的登录方式
            if not self.working_login:
                self.working_login = WorkingWeChatLogin()
            
            # 在新线程中获取二维码
            threading.Thread(target=self.do_get_working_qr, daemon=True).start()
                
        except Exception as e:
            print(f"获取公众号二维码失败: {e}")
            self.root.after(0, lambda: self.show_error(f"获取二维码失败: {str(e)}"))
            self.root.after(0, lambda: self.generate_qr_btn.config(state='normal', text="生成二维码"))
    
    def do_get_working_qr(self):
        """执行获取二维码"""
        try:
            # 直接获取二维码
            result = self.working_login.direct_qr_login()
            
            if result.get('success') and 'qr_data' in result:
                # 显示二维码
                img = Image.open(BytesIO(result['qr_data']))
                img = Image.open(BytesIO(result['qr_data']))
                photo = ImageTk.PhotoImage(img)
                
                self.root.after(0, lambda: self.display_working_qr(photo, result['message']))
                
            else:
                self.root.after(0, lambda: self.show_error(f"获取二维码失败: {result.get('message', '未知错误')}"))
                
        except Exception as e:
            print(f"获取二维码失败: {e}")
            self.root.after(0, lambda: self.show_error(f"获取二维码失败: {str(e)}"))
            
        finally:
            self.root.after(0, lambda: self.generate_qr_btn.config(state='normal', text="生成二维码"))
            
    def display_mp_wechat_qr(self, photo, method):
        """显示微信公众号登录二维码"""
        # 显示二维码
        self.qr_label.config(image=photo, text="")
        self.qr_label.image = photo
        
        status_text = "✅ 微信公众号登录二维码已生成"
        guide_text = "📱 请使用微信扫描上方二维码\n⚡ 这是公众号管理后台登录\n✅ 扫码后手机确认即可完成登录\n⏱️ 二维码有效期为2分钟\n\n💡 扫码后可管理公众号文章"
        
        self.update_status(status_text)
        
        # 显示操作提示
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='center', font=('Microsoft YaHei', 10))
            self.guide_label.pack(pady=10)
            
        self.generate_qr_btn.config(state='normal', text="重新生成")
    
    def display_working_qr(self, photo, message):
        """显示真正可用的登录二维码"""
        # 显示二维码
        self.qr_label.config(image=photo, text="")
        self.qr_label.image = photo
        
        status_text = "🎉 微信公众号登录二维码已生成（基于正确实现）"
        guide_text = f"""🎉 微信公众号登录 - 基于正确实现
📱 使用微信扫描上方二维码
✅ 扫码后手机确认即可完成登录
⚡ 基于您提供的正确实现方式
⏱️ 二维码有效期2分钟

💡 这是真正可用的登录方式！
📋 状态: {message}"""
        
        self.update_status(status_text)
        
        # 显示操作提示
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='center', font=('Microsoft YaHei', 10))
            self.guide_label.pack(pady=10)
    
    def check_simple_mp_login_status(self):
        """检查简单登录状态"""
        try:
            if not self.qr_status_checker:
                self.qr_status_checker = MPQRStatusChecker(self.simple_mp_login.session if self.simple_mp_login else None)
            
            def status_callback(status, message, data=None):
                if status == 'waiting':
                    self.root.after(0, lambda: self.update_status(f"⏳ {message}"))
                elif status == 'scanned':
                    self.root.after(0, lambda: self.update_status(f"✅ {message}"))
                elif status == 'success':
                    # 登录成功
                    cookie = data.get('cookie', '') if data else ''
                    token = data.get('token', '') if data else ''
                    self.root.after(0, lambda: self.on_login_success(token, cookie))
                    self.root.after(0, lambda: self.show_info("🎉 微信公众号登录成功！"))
                elif status == 'timeout':
                    self.root.after(0, lambda: self.show_error("二维码已过期，请重新生成"))
                    self.root.after(0, lambda: self.update_status("二维码已过期"))
                elif status == 'error':
                    self.root.after(0, lambda: self.show_error(f"登录检查失败: {message}"))
                    self.root.after(0, lambda: self.update_status("登录检查失败"))
            
            self.qr_status_checker.check_qr_status(status_callback)
            
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            self.root.after(0, lambda: self.update_status("登录状态检查失败"))
    
    def display_simple_mp_qr(self, photo, method, login_type):
        """显示简化微信公众号登录二维码"""
        # 显示二维码
        self.qr_label.config(image=photo, text="")
        self.qr_label.image = photo
        
        status_text = "🌟 微信公众号登录二维码已生成"
        guide_text = """🌟 微信公众号登录
📱 扫描上方二维码访问公众平台
✅ 使用微信扫描网页上的登录二维码
⚡ 在手机微信中确认登录
⏱️ 按照页面指引完成操作

💡 这是安全可靠的登录方式"""
        
        self.update_status(status_text)
        
        # 显示操作提示
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='center', font=('Microsoft YaHei', 10))
            self.guide_label.pack(pady=10)
            
        self.generate_qr_btn.config(state='normal', text="重新生成")
        
    def show_practical_solution(self):
        """显示实用解决方案"""
        self.qr_label.config(image="", text="🔧 正在为您准备最佳解决方案...")
        
        solution_text = """🚀 由于安全限制，推荐使用最佳解决方案：

📱 步骤1：点击"一键打开登录页"
   自动打开微信公众平台登录页面

📱 步骤2：扫码登录公众号后台
   使用微信扫描页面上的二维码

📱 步骤3：获取登录凭据
   按F12打开开发者工具获取Cookie和Token

📱 步骤4：一键配置程序
   在下方手动配置区域填入信息

✅ 优势：
• 操作简单 - 2-3分钟完成
• 稳定可靠 - 避免反爬虫限制  
• 一次配置 - 长期有效使用
• 安全放心 - 直接与微信官方交互

💡 现在点击下方"Cookie获取助手"按钮开始！"""
        
        self.update_status("已准备最佳解决方案")
        
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=solution_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=solution_text, 
                                       justify='left', font=('Microsoft YaHei', 9))
            self.guide_label.pack(pady=10)
            
        self.generate_qr_btn.config(state='normal', text="重新生成")
    
    def show_manual_guide(self):
        """显示手动登录指导"""
        # 清空二维码显示
        self.qr_label.config(image="", text="")
        
        guide_text = """🎯 微信公众号手动登录指南

✅ 步骤1：点击下方"一键打开登录页"按钮
   直接访问微信公众平台登录页面

✅ 步骤2：微信扫码登录
   使用微信扫描页面上的登录二维码

✅ 步骤3：获取登录信息
   登录成功后按F12打开开发者工具
   在Network标签中找到任意API请求
   复制请求头中的Cookie信息
   复制URL参数中的token值

✅ 步骤4：配置程序
   在下方"手动配置"区域填入信息
   点击"保存配置"即可使用

🔧 Cookie格式示例：
appmsglist_action_xxx=...; ua_id=...; wxuin=...

🔑 Token获取：
在URL中找到token=后面的数字

💡 现在点击下方"Cookie获取助手"获取详细指导！"""
        
        self.update_status("请按照指南完成登录配置")
        
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='left', font=('Microsoft YaHei', 9))
            self.guide_label.pack(pady=10)
        
        # 添加快捷按钮
        if not hasattr(self, 'quick_open_btn'):
            self.quick_open_btn = ttk.Button(self.qr_frame, text="🚀 一键打开登录页", 
                                           command=self.open_mp_login_page)
            self.quick_open_btn.pack(pady=5)
            self.cookie_helper_btn = ttk.Button(self.qr_frame, text="🔧 Cookie获取助手", 
                                              command=self.open_cookie_helper)
            self.cookie_helper_btn.pack(pady=5)
        
        self.generate_qr_btn.config(state='normal', text="重新尝试扫码")
        
    def check_mp_login_status(self):
        """检查微信公众号登录状态"""
        try:
            if not self.mp_wechat_login:
                return
                
            def login_callback(status, message, data=None):
                if status == 'waiting':
                    self.root.after(0, lambda: self.update_status(f"⏳ {message}"))
                elif status == 'scanned':
                    self.root.after(0, lambda: self.update_status(f"✅ {message}"))
                elif status == 'success':
                    # 登录成功
                    cookie = data.get('cookie', '')
                    token = data.get('token', '')
                    self.root.after(0, lambda: self.on_login_success(token, cookie))
                    self.root.after(0, lambda: self.show_info("🎉 微信公众号登录成功！"))
                elif status == 'expired':
                    self.root.after(0, lambda: self.show_error("二维码已过期，请重新生成"))
                    self.root.after(0, lambda: self.update_status("二维码已过期"))
                elif status == 'timeout':
                    self.root.after(0, lambda: self.show_error("登录超时，请重新生成二维码"))
                    self.root.after(0, lambda: self.update_status("登录超时"))
                elif status == 'error':
                    self.root.after(0, lambda: self.show_error(f"登录检查失败: {message}"))
                    self.root.after(0, lambda: self.update_status("登录检查失败"))
            
            self.mp_wechat_login.check_mp_login_status(login_callback)
            
        except Exception as e:
            print(f"检查公众号登录状态失败: {e}")
            self.root.after(0, lambda: self.update_status("登录状态检查失败"))
    
    def check_new_mp_login_status(self):
        """检查新的微信公众号登录状态"""
        try:
            if not self.mp_qr_login:
                return
                
            def login_callback(status, message, data=None):
                if status == 'waiting':
                    self.root.after(0, lambda: self.update_status(f"⏳ {message}"))
                elif status == 'scanned':
                    self.root.after(0, lambda: self.update_status(f"🎯 已扫描：{message}"))
                elif status == 'success':
                    # 登录成功
                    cookie = data.get('cookie', '')
                    token = data.get('token', '')
                    self.root.after(0, lambda: self.on_login_success(token, cookie))
                    self.root.after(0, lambda: self.show_info("🎉 微信公众号登录成功！"))
                elif status == 'manual_guide':
                    # 需要手动操作
                    self.root.after(0, lambda: self.show_manual_guide())
                elif status == 'expired':
                    self.root.after(0, lambda: self.show_error("二维码已过期，请重新生成"))
                    self.root.after(0, lambda: self.update_status("二维码已过期"))
                elif status == 'timeout':
                    self.root.after(0, lambda: self.show_error("登录超时，请重新生成二维码"))
                    self.root.after(0, lambda: self.update_status("登录超时"))
                elif status == 'error':
                    self.root.after(0, lambda: self.show_error(f"登录检查失败: {message}"))
                    self.root.after(0, lambda: self.update_status("登录检查失败"))
            
            self.mp_qr_login.check_login_status(login_callback)
            
        except Exception as e:
            print(f"检查新公众号登录状态失败: {e}")
            self.root.after(0, lambda: self.update_status("登录状态检查失败"))
            
    def display_real_wechat_qr(self, photo, login_type):
        """显示真正的微信登录二维码"""
        # 显示二维码
        self.qr_label.config(image=photo, text="")
        self.qr_label.image = photo
        
        # 根据登录类型显示不同的提示
        if login_type == 'web_qr':
            status_text = "✅ 真正的微信登录二维码已生成"
            guide_text = "📱 请使用微信扫描上方二维码\n⚡ 直接扫码登录，无需跳转页面\n✅ 扫码后手机确认即可完成登录\n⏱️ 二维码有效期为2分钟"
        else:
            status_text = "✅ 微信登录二维码已生成"
            guide_text = "📱 请使用微信扫描上方二维码\n扫码后在手机上确认登录\n⏱️ 二维码有效期为60秒"
        
        self.update_status(status_text)
        
        # 显示操作提示
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='center', font=('Microsoft YaHei', 10))
            self.guide_label.pack(pady=10)
            
        self.generate_qr_btn.config(state='normal', text="重新生成")
        
    def show_login_fallback(self):
        """显示登录备用方案"""
        self.generate_operation_guide()
        self.generate_qr_btn.config(state='normal', text="重新生成")
        
    def check_wechat_login_status(self, uuid):
        """检查微信登录状态"""
        try:
            if not self.wechat_login:
                return
                
            def login_callback(status, message, data=None):
                if status == 'waiting':
                    self.root.after(0, lambda: self.update_status(message))
                elif status == 'scanned':
                    self.root.after(0, lambda: self.update_status(message))
                elif status == 'success':
                    # 登录成功
                    cookie = data.get('cookie', '')
                    token = data.get('token', '')
                    self.root.after(0, lambda: self.on_login_success(token, cookie))
                elif status == 'expired':
                    self.root.after(0, lambda: self.show_error("二维码已过期，请重新生成"))
                    self.root.after(0, lambda: self.update_status("二维码已过期"))
                elif status == 'timeout':
                    self.root.after(0, lambda: self.show_error("登录超时，请重新生成二维码"))
                    self.root.after(0, lambda: self.update_status("登录超时"))
                elif status == 'error':
                    self.root.after(0, lambda: self.show_error(f"登录检查失败: {message}"))
                    self.root.after(0, lambda: self.update_status("登录检查失败"))
            
            self.wechat_login.check_platform_login(uuid, login_callback)
            
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            self.root.after(0, lambda: self.update_status("登录状态检查失败"))
            
    def check_real_wechat_login_status(self):
        """检查真正的微信登录状态"""
        try:
            if not self.real_wechat_login:
                return
                
            def login_callback(status, message, data=None):
                if status == 'waiting':
                    self.root.after(0, lambda: self.update_status(message))
                elif status == 'scanned':
                    self.root.after(0, lambda: self.update_status(f"✅ {message}"))
                elif status == 'success':
                    # 登录成功
                    cookie = data.get('cookie', '')
                    token = data.get('token', '')
                    self.root.after(0, lambda: self.on_login_success(token, cookie))
                    self.root.after(0, lambda: self.show_info("🎉 微信扫码登录成功！"))
                elif status == 'expired':
                    self.root.after(0, lambda: self.show_error("二维码已过期，请重新生成"))
                    self.root.after(0, lambda: self.update_status("二维码已过期"))
                elif status == 'timeout':
                    self.root.after(0, lambda: self.show_error("登录超时，请重新生成二维码"))
                    self.root.after(0, lambda: self.update_status("登录超时"))
                elif status == 'error':
                    self.root.after(0, lambda: self.show_error(f"登录检查失败: {message}"))
                    self.root.after(0, lambda: self.update_status("登录检查失败"))
            
            self.real_wechat_login.check_login_status(self.login_uuid, self.login_type, login_callback)
            
        except Exception as e:
            print(f"检查真正登录状态失败: {e}")
            self.root.after(0, lambda: self.update_status("登录状态检查失败"))
            
    def generate_operation_guide(self):
        """生成操作指导"""
        try:
            # 创建一个包含完整操作步骤的网页链接
            guide_url = "https://mp.weixin.qq.com/"
            
            # 生成指向微信登录页面的二维码
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(guide_url)
            qr.make(fit=True)
            
            # 生成图像
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 调整大小
            img = img.resize((280, 280))
            photo = ImageTk.PhotoImage(img)
            
            # 显示二维码和操作说明
            self.display_qr_with_guide(photo)
            
        except Exception as e:
            print(f"生成操作指导失败: {e}")
            self.show_text_guide()
            
    def display_qr_with_guide(self, photo):
        """显示二维码和操作说明"""
        # 显示二维码
        self.qr_label.config(image=photo, text="")
        self.qr_label.image = photo
        
        # 更新状态和说明
        self.update_status("二维码已生成，请按照以下步骤操作")
        
        # 显示详细操作说明
        guide_text = """📱 微信公众号登录步骤：

1️⃣ 扫描上方二维码访问微信公众平台
2️⃣ 使用微信扫描网页上的登录二维码  
3️⃣ 在手机微信中确认登录
4️⃣ 登录成功后，按F12打开开发者工具
5️⃣ 在Network标签中找到任意请求
6️⃣ 从请求头复制Cookie和URL中的Token
7️⃣ 将Cookie和Token填入"手动配置"区域

💡 推荐使用手动配置方式，更稳定可靠！"""
        
        # 在二维码区域下方显示说明
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='left', font=('Microsoft YaHei', 9))
            self.guide_label.pack(pady=10)
            
    def show_text_guide(self):
        """显示纯文字指导"""
        self.qr_label.config(image="", text="二维码生成失败\n请按以下步骤操作：")
        
        guide_text = """📋 手动登录步骤：

1. 打开浏览器访问：https://mp.weixin.qq.com/
2. 使用微信扫码登录公众号平台
3. 登录成功后按F12打开开发者工具
4. 切换到Network标签
5. 刷新页面，找到任意请求
6. 复制Request Headers中的Cookie
7. 复制URL参数中的token
8. 将Cookie和Token填入下方"手动配置"区域
9. 点击"保存配置"即可使用

🔧 Cookie格式示例：
appmsglist_action_xxx=...; ua_id=...; wxuin=...

🔑 Token获取：
在URL中找到token=后面的数字"""
        
        if hasattr(self, 'guide_label'):
            self.guide_label.config(text=guide_text)
        else:
            self.guide_label = ttk.Label(self.qr_frame, text=guide_text, 
                                       justify='left', font=('Microsoft YaHei', 9))
            self.guide_label.pack(pady=10)
        
        self.update_status("请按照文字指导进行手动登录配置")
            
    def display_qr_code(self, photo):
        """显示二维码"""
        self.qr_label.config(image=photo, text="二维码已生成")
        self.qr_label.image = photo  # 保持引用
            
    def check_qr_login_status(self):
        """检查二维码登录状态"""
        # 由于技术限制，自动二维码登录暂时不可用
        # 直接引导用户使用手动配置
        pass
            
    # 移除账号密码登录功能，改用Selenium扫码登录
    # def login_with_password(self):
    #     """账号密码登录 - 已移除，改用扫码登录"""
    #     self.show_info("账号密码登录已移除，请使用扫码登录方式。这种方式更安全可靠！")
    
    # 移除账号密码登录功能
    # def do_password_login(self, username, password):
    #     """执行账号密码登录 - 已移除"""
    #     pass
    
    def check_qr_login_status(self):
        """检查二维码登录状态"""
        try:
            if not self.working_login:
                return
            
            # 在新线程中检查状态
            threading.Thread(target=self.do_check_qr_status, daemon=True).start()
            
        except Exception as e:
            print(f"检查二维码状态失败: {e}")
    
    def do_check_qr_status(self):
        """执行二维码状态检查"""
        try:
            def status_callback(status, message, data=None):
                if status == 'success':
                    # 登录成功
                    token = data.get('token', '') if data else ''
                    cookie = data.get('cookie', '') if data else ''
                    self.root.after(0, lambda: self.on_login_success(token, cookie))
                    self.root.after(0, lambda: self.show_info("🎉 扫码登录成功！"))
                elif status == 'waiting':
                    self.root.after(0, lambda: self.update_status(f"⏳ {message}"))
                elif status == 'timeout':
                    self.root.after(0, lambda: self.show_error("登录超时，请重新生成二维码"))
                elif status == 'error':
                    self.root.after(0, lambda: self.show_error(f"登录检查失败: {message}"))
            
            # 使用工作登录的状态检查
            result = self.working_login.check_login_status()
            
            if result.get('success'):
                status_callback('success', '登录成功', {
                    'token': result.get('token', ''),
                    'cookie': result.get('cookie', '')
                })
            else:
                status_callback('error', result.get('message', '状态检查失败'))
                
        except Exception as e:
            print(f"执行状态检查失败: {e}")
            
    # 移除密码登录指导
    # def show_password_login_guide(self):
    #     """显示密码登录指导 - 已移除"""
    #     pass
        
    def on_login_success(self, token=None, cookie=None):
        """登录成功处理"""
        if token:
            self.config['token'] = token
        if cookie:
            self.config['cookie'] = cookie
            
        self.login_status_label.config(text="已登录", foreground="green")
        self.update_status("登录成功")
        self.show_info("登录成功！现在可以搜索公众号了。")
        
    def save_manual_config(self):
        """保存手动配置"""
        cookie = self.cookie_text.get("1.0", tk.END).strip()
        token = self.token_entry.get().strip()
        
        if not cookie or not token:
            self.show_error("请输入完整的Cookie和Token")
            return
        
        # 验证token格式（应该是数字）
        if not token.isdigit():
            self.show_error("Token格式错误，应该是纯数字")
            return
            
        # 验证cookie格式（应该包含等号）
        if "=" not in cookie:
            self.show_error("Cookie格式错误，应该包含键值对")
            return
            
        self.config['cookie'] = cookie
        self.config['token'] = token
        
        # 更新下载器配置
        if self.downloader:
            self.downloader.config = self.config.copy()
            # 更新请求头中的cookie
            self.downloader.session.headers["Cookie"] = cookie
        else:
            # 创建新的下载器实例
            self.downloader = WeChatArticleDownloader(self.config)
        
        self.login_status_label.config(text="已配置", foreground="green")
        self.update_status("配置已保存")
        
        # 显示成功弹窗
        messagebox.showinfo("配置成功", 
                          "✅ 手动配置保存成功！\n\n"
                          f"Token: {token[:10]}...\n"
                          f"Cookie: {len(cookie)}个字符\n\n"
                          "现在可以搜索公众号了！")
        
        # 验证配置是否有效
        threading.Thread(target=self.validate_manual_config, daemon=True).start()
    
    def validate_manual_config(self):
        """验证手动配置是否有效"""
        try:
            # 创建临时下载器进行验证
            temp_downloader = WeChatArticleDownloader(self.config)
            
            # 尝试搜索一个测试关键词
            test_result = temp_downloader.search_accounts("微信", self.config['token'])
            
            if test_result:
                self.root.after(0, lambda: self.show_info("🎉 配置验证成功！\n\n您的Cookie和Token配置正确，\n搜索功能正常工作。"))
            else:
                self.root.after(0, lambda: self.show_info("⚠️ 配置可能有问题\n\n虽然配置已保存，但搜索测试失败。\n请检查Cookie和Token是否正确。"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_info(f"⚠️ 配置验证失败\n\n配置已保存，但验证时出现错误：\n{str(e)}\n\n请检查配置是否正确。"))
        
    def search_accounts(self):
        """搜索公众号"""
        keyword = self.search_entry.get().strip()
        
        if not keyword:
            self.show_error("请输入搜索关键词")
            return
            
        # 检查token是否配置（多种来源）
        token = self.config.get('token') or self.token_entry.get().strip()
        
        if not token:
            self.show_error("请先登录或配置Token\n\n"
                          "您可以选择：\n"
                          "1. 使用扫码登录自动配置\n"
                          "2. 在下方手动配置区域填入Cookie和Token")
            return
        
        # 确保token已保存到config中
        if not self.config.get('token'):
            self.config['token'] = token
            
        # 确保cookie也配置了
        if not self.config.get('cookie'):
            cookie = self.cookie_text.get("1.0", tk.END).strip()
            if cookie:
                self.config['cookie'] = cookie
        
        # 打印调试信息
        print(f"🔍 搜索公众号: {keyword}")
        print(f"📋 Token: {token[:10]}..." if len(token) > 10 else f"📋 Token: {token}")
        print(f"📋 Cookie: {len(self.config.get('cookie', ''))}个字符")
            
        try:
            self.update_status("正在搜索公众号...")
            
            # 在新线程中执行搜索
            threading.Thread(target=self.do_search_accounts, args=(keyword,), daemon=True).start()
            
        except Exception as e:
            self.show_error(f"搜索失败: {str(e)}")
            self.update_status("搜索失败")
            
    def do_search_accounts(self, keyword):
        """执行公众号搜索"""
        try:
            # 确保使用最新的配置创建下载器
            current_config = {
                'cookie': self.config.get('cookie') or self.cookie_text.get("1.0", tk.END).strip(),
                'token': self.config.get('token') or self.token_entry.get().strip(),
                'user_agent': self.config.get('user_agent', 
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
            }
            
            # 验证配置完整性
            if not current_config['token']:
                raise Exception("Token未配置")
                
            if not current_config['cookie']:
                raise Exception("Cookie未配置")
            
            # 创建或更新下载器
            if not self.downloader:
                self.downloader = WeChatArticleDownloader(current_config)
            else:
                # 更新现有下载器的配置
                self.downloader.config = current_config
                self.downloader.session.headers["Cookie"] = current_config['cookie']
            
            print(f"🔍 使用配置搜索: Token={current_config['token'][:10]}..., Cookie长度={len(current_config['cookie'])}")
            
            accounts = self.downloader.search_accounts(keyword, current_config['token'])
            self.root.after(0, lambda: self.display_search_results(accounts))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"搜索失败: {str(e)}"))
            self.root.after(0, lambda: self.update_status("搜索失败"))
            
    def display_search_results(self, accounts):
        """显示搜索结果"""
        # 清空现有结果
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
            
        # 添加搜索结果
        for account in accounts:
            self.accounts_tree.insert('', 'end', 
                                     text=account.get('fakeid', ''),
                                     values=(account.get('nickname', ''),
                                            account.get('alias', ''),
                                            account.get('signature', '')))
                                            
        self.update_status(f"找到 {len(accounts)} 个公众号")
        
    def select_account(self, event=None):
        """双击选择公众号"""
        self.select_account_from_tree()
        
    def select_account_from_tree(self):
        """从树中选择公众号"""
        selection = self.accounts_tree.selection()
        if not selection:
            self.show_error("请先选择一个公众号")
            return
            
        item = self.accounts_tree.item(selection[0])
        fakeid = item['text']
        nickname = item['values'][0]
        
        self.current_account = {
            'fakeid': fakeid,
            'nickname': nickname
        }
        
        # 更新文章选项卡显示
        self.account_info_label.config(text=f"当前公众号: {nickname}")
        
        # 切换到文章列表选项卡
        self.notebook.select(self.articles_frame)
        
        # 开始加载文章列表
        self.load_articles(1)
        
        self.update_status(f"已选择公众号: {nickname}")
        self.show_info(f"已选择公众号: {nickname}")
        
    def load_articles(self, page=1):
        """加载文章列表"""
        if not self.current_account:
            self.show_error("请先选择公众号")
            return
            
        try:
            self.update_status(f"正在加载第 {page} 页文章...")
            
            # 在新线程中执行加载
            threading.Thread(target=self.do_load_articles, args=(page,), daemon=True).start()
            
        except Exception as e:
            self.show_error(f"加载文章失败: {str(e)}")
            self.update_status("加载文章失败")
            
    def do_load_articles(self, page):
        """执行文章加载"""
        try:
            if not self.downloader:
                self.downloader = WeChatArticleDownloader(self.config)
            
            articles = self.downloader.get_articles_list(
                self.current_account['fakeid'], 
                self.config['token'], 
                page, 
                5
            )
            self.root.after(0, lambda: self.display_articles(articles, page))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"加载文章失败: {str(e)}"))
            self.root.after(0, lambda: self.update_status("加载文章失败"))
            
    def display_articles(self, articles, page):
        """显示文章列表"""
        # 清空现有结果
        for item in self.articles_tree.get_children():
            self.articles_tree.delete(item)
            
        # 添加文章列表
        for i, article in enumerate(articles):
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", 
                                       time.localtime(article.get('create_time', 0)))
            self.articles_tree.insert('', 'end',
                                     text=str(i + 1),
                                     values=(article.get('title', ''),
                                            create_time,
                                            article.get('link', '')))
                                            
        self.current_page = page
        self.page_label.config(text=f"第 {page} 页")
        
        # 更新分页按钮状态
        self.prev_btn.config(state='normal' if page > 1 else 'disabled')
        self.next_btn.config(state='normal' if len(articles) == 5 else 'disabled')
        
        self.update_status(f"第 {page} 页，共 {len(articles)} 篇文章")
        
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.load_articles(self.current_page - 1)
            
    def next_page(self):
        """下一页"""
        self.load_articles(self.current_page + 1)
        
    def choose_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
            
    def export_selected_articles(self):
        """导出选中的文章"""
        selection = self.articles_tree.selection()
        if not selection:
            self.show_error("请先选择要导出的文章")
            return
            
        articles = []
        for item in selection:
            article_data = self.articles_tree.item(item)
            articles.append({
                'title': article_data['values'][0],
                'link': article_data['values'][2]
            })
            
        self.export_articles(articles)
        
    def export_all_articles(self):
        """导出所有历史文章"""
        if not self.current_account:
            self.show_error("请先选择公众号")
            return
            
        # 询问用户确认
        if not messagebox.askyesno("确认导出所有文章", 
                                "确定要导出该公众号的所有历史文章吗？\n\n"
                                "⚠️ 这可能需要较长时间（取决于文章数量）\n"
                                "📥 将按人类点击速度自动下载，避免被限制\n"
                                "⏱️ 平均每篇文章间隔2-4秒"):
            return
            
        # 在新线程中获取所有文章并导出
        threading.Thread(target=self.do_export_all_articles, daemon=True).start()
    
    def do_export_all_articles(self):
        """执行所有文章导出"""
        try:
            self.root.after(0, lambda: self.show_info("正在获取所有历史文章列表..."))
            self.root.after(0, lambda: self.update_status("正在获取文章总数..."))
            
            if not self.downloader:
                self.downloader = WeChatArticleDownloader(self.config)
            
            # 获取所有文章
            all_articles = []
            page = 1
            total_pages = 1
            
            while page <= total_pages:
                try:
                    # 获取当前页文章
                    articles_data = self.downloader.get_articles_list(
                        self.current_account['fakeid'], 
                        self.config['token'], 
                        page, 
                        5  # 每页显示数量
                    )
                    
                    if not articles_data.get('articles'):
                        break
                        
                    # 更新总页数
                    total_pages = articles_data.get('total_pages', 1)
                    
                    # 添加到文章列表
                    for article in articles_data['articles']:
                        all_articles.append({
                            'title': article['title'],
                            'link': article['link']
                        })
                    
                    # 更新进度
                    self.root.after(0, lambda p=page, tp=total_pages: 
                                  self.progress_label.config(text=f"正在获取文章列表: {p}/{tp} 页"))
                    
                    page += 1
                    
                    # 添加延迟避免请求过快
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"获取第{page}页文章失败: {e}")
                    break
            
            if not all_articles:
                self.root.after(0, lambda: self.show_error("未找到任何文章"))
                return
            
            self.root.after(0, lambda: self.show_info(f"已获取到 {len(all_articles)} 篇文章，开始下载..."))
            self.root.after(0, lambda: self.update_status(f"开始导出 {len(all_articles)} 篇文章..."))
            
            # 创建输出目录
            output_path = self.output_dir.get()
            if self.current_account:
                output_path = os.path.join(output_path, self.current_account['nickname'])
            os.makedirs(output_path, exist_ok=True)
            
            # 开始导出所有文章
            self.batch_export_articles(all_articles, output_path)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"获取文章列表失败: {str(e)}"))
            self.root.after(0, lambda: self.update_status("获取文章失败"))
    
    def stop_export(self):
        """停止导出"""
        if self.exporting:
            self.stop_export_flag = True
            self.update_status("正在停止导出...")
            self.stop_export_btn.config(state='disabled')
            self.show_info("正在停止导出，请稍候...")
    
    def batch_export_articles(self, articles, output_path):
        """批量导出文章"""
        try:
            # 设置导出状态
            self.exporting = True
            self.stop_export_flag = False
            self.root.after(0, lambda: self.stop_export_btn.config(state='normal'))
            
            total = len(articles)
            success = 0
            failed = 0
            
            for i, article in enumerate(articles):
                # 检查是否需要停止
                if self.stop_export_flag:
                    self.root.after(0, lambda: self.update_status("导出已停止"))
                    self.root.after(0, lambda: self.progress_label.config(
                        text=f"已停止: 成功 {success} 篇，失败 {failed} 篇 (共处理 {i}/{total} 篇)"))
                    break
                
                try:
                    # 更新进度
                    progress = (i / total) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    self.root.after(0, lambda i=i, total=total: 
                                  self.progress_label.config(text=f"正在下载: {i+1}/{total} - {article['title'][:20]}..."))
                    
                    # 获取文章内容
                    article_data = self.downloader.get_article_content(article['link'])
                    
                    # 保存文章
                    format_type = self.export_format.get()
                    filepath = self.downloader.save_article(article_data, output_path, format_type)
                    
                    success += 1
                    
                    # 人类点击速度：每篇文章间隔2-4秒，模拟真实用户行为
                    sleep_time = random.uniform(2.0, 4.0)
                    self.root.after(0, lambda t=sleep_time: 
                                  self.update_status(f"下载完成，等待 {t:.1f} 秒后继续..."))
                    
                    # 分段睡眠，支持中断
                    for _ in range(int(sleep_time * 2)):  # 每0.5秒检查一次
                        if self.stop_export_flag:
                            break
                        time.sleep(0.5)
                    
                    if self.stop_export_flag:
                        break
                    
                except Exception as e:
                    failed += 1
                    print(f"下载文章失败: {article.get('title', '')}, 错误: {e}")
                    # 如果失败，稍等一下再继续
                    time.sleep(random.uniform(1, 2))
            
            # 完成导出
            self.exporting = False
            self.root.after(0, lambda: self.stop_export_btn.config(state='disabled'))
            
            if self.stop_export_flag:
                result_msg = f"导出已停止！\n\n📊 统计信息:\n✅ 成功: {success} 篇\n❌ 失败: {failed} 篇\n⏹️ 已处理: {i+1}/{total} 篇\n📁 保存位置: {output_path}"
            else:
                self.root.after(0, lambda: self.progress_var.set(100))
                result_msg = f"导出完成！\n\n📊 统计信息:\n✅ 成功: {success} 篇\n❌ 失败: {failed} 篇\n📁 保存位置: {output_path}"
                
                if failed > 0:
                    result_msg += f"\n\n⚠️ 提示: 有 {failed} 篇文章下载失败，可能是网络问题或文章已被删除"
            
            self.root.after(0, lambda: self.progress_label.config(
                text=f"{'停止' if self.stop_export_flag else '完成'}: 成功 {success} 篇，失败 {failed} 篇"))
            self.root.after(0, lambda: self.update_status(f"导出{'已停止' if self.stop_export_flag else '完成'}: 成功 {success}/{total} 篇文章"))
            self.root.after(0, lambda: self.show_info(result_msg))
            
        except Exception as e:
            self.exporting = False
            self.root.after(0, lambda: self.stop_export_btn.config(state='disabled'))
            self.root.after(0, lambda: self.show_error(f"批量导出过程中出错: {str(e)}"))
            self.root.after(0, lambda: self.update_status("批量导出失败"))
        
    def export_articles(self, articles):
        """导出文章"""
        if not articles:
            self.show_error("没有要导出的文章")
            return
            
        try:
            self.update_status(f"正在导出 {len(articles)} 篇文章...")
            
            # 在新线程中执行导出
            threading.Thread(target=self.do_export_articles, args=(articles,), daemon=True).start()
            
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")
            self.update_status("导出失败")
            
    def do_export_articles(self, articles):
        """执行文章导出"""
        try:
            # 设置导出状态
            self.exporting = True
            self.stop_export_flag = False
            self.root.after(0, lambda: self.stop_export_btn.config(state='normal'))
            
            if not self.downloader:
                self.downloader = WeChatArticleDownloader(self.config)
            
            # 创建输出目录
            output_path = self.output_dir.get()
            if self.current_account:
                output_path = os.path.join(output_path, self.current_account['nickname'])
            os.makedirs(output_path, exist_ok=True)
            
            total = len(articles)
            success = 0
            
            for i, article in enumerate(articles):
                # 检查是否需要停止
                if self.stop_export_flag:
                    self.root.after(0, lambda: self.update_status("导出已停止"))
                    self.root.after(0, lambda: self.progress_label.config(
                        text=f"已停止: 成功 {success} 篇 (共处理 {i}/{total} 篇)"))
                    break
                
                try:
                    # 更新进度
                    progress = (i / total) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    self.root.after(0, lambda i=i, total=total: self.progress_label.config(text=f"正在下载第 {i+1}/{total} 篇文章"))
                    
                    # 获取文章内容
                    article_data = self.downloader.get_article_content(article['link'])
                    
                    # 保存文章
                    format_type = self.export_format.get()
                    filepath = self.downloader.save_article(article_data, output_path, format_type)
                    
                    success += 1
                    
                    # 人类点击速度：每篇文章间隔2-4秒
                    sleep_time = random.uniform(2.0, 4.0)
                    self.root.after(0, lambda t=sleep_time: 
                                  self.update_status(f"下载完成，等待 {t:.1f} 秒后继续..."))
                    
                    # 分段睡眠，支持中断
                    for _ in range(int(sleep_time * 2)):  # 每0.5秒检查一次
                        if self.stop_export_flag:
                            break
                        time.sleep(0.5)
                    
                    if self.stop_export_flag:
                        break
                    
                except Exception as e:
                    print(f"导出文章失败: {article.get('title', '')}, 错误: {e}")
            
            # 完成导出
            self.exporting = False
            self.root.after(0, lambda: self.stop_export_btn.config(state='disabled'))
            
            if self.stop_export_flag:
                self.root.after(0, lambda: self.progress_var.set((i+1)/total*100))
                result_msg = f"导出已停止！\n\n📊 统计信息:\n✅ 成功: {success} 篇\n⏹️ 已处理: {i+1}/{total} 篇\n📁 保存位置: {output_path}"
            else:
                self.root.after(0, lambda: self.progress_var.set(100))
                result_msg = f"导出完成！成功导出 {success}/{total} 篇文章到:\n{output_path}"
            
            self.root.after(0, lambda: self.progress_label.config(
                text=f"{'停止' if self.stop_export_flag else '完成'}: 成功 {success}/{total} 篇"))
            self.root.after(0, lambda: self.update_status(f"导出{'已停止' if self.stop_export_flag else '完成'}: 成功 {success}/{total} 篇文章"))
            self.root.after(0, lambda: self.show_info(result_msg))
            
        except Exception as e:
            self.exporting = False
            self.root.after(0, lambda: self.stop_export_btn.config(state='disabled'))
            self.root.after(0, lambda: self.show_error(f"导出过程中出错: {str(e)}"))
            self.root.after(0, lambda: self.update_status("导出失败"))

    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WeChatDownloaderGUI()
    app.run()
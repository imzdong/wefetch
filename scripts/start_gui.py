#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号文章下载器启动脚本
"""

import sys
import os

def main():
    """主函数"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # 检查依赖
        try:
            import tkinter
            import requests
            import bs4
            import PIL
            import qrcode
            import markdownify
            import openpyxl
        except ImportError as e:
            print(f"缺少依赖包: {e}")
            print("请运行: pip install -r requirements.txt")
            return
        
        # 启动GUI
        from gui.wechat_gui import WeChatDownloaderGUI
        import tkinter as tk
        
        print("正在启动微信公众号文章下载器...")
        root = tk.Tk()
        app = WeChatDownloaderGUI(root)
        root.mainloop()
        
    except Exception as e:
        print(f"启动失败: {e}")
        input("按Enter键退出...")

if __name__ == "__main__":
    main()
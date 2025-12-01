#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号文章下载器启动脚本 - 简化版
"""

import sys
import os

def main():
    """主函数"""
    print("=" * 50)
    print("📱 微信公众号文章下载器 GUI版本")
    print("=" * 50)
    
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 检查依赖
    print("🔍 检查依赖包...")
    missing_deps = []
    
    try:
        import tkinter
        print("✅ tkinter - 可用")
    except ImportError:
        missing_deps.append("tkinter")
        print("❌ tkinter - 缺失")
    
    try:
        import requests
        print("✅ requests - 可用")
    except ImportError:
        missing_deps.append("requests")
        print("❌ requests - 缺失")
    
    try:
        import bs4
        print("✅ beautifulsoup4 - 可用")
    except ImportError:
        missing_deps.append("beautifulsoup4")
        print("❌ beautifulsoup4 - 缺失")
    
    try:
        import PIL
        print("✅ Pillow - 可用")
    except ImportError:
        missing_deps.append("Pillow")
        print("❌ Pillow - 缺失")
    
    try:
        import qrcode
        print("✅ qrcode - 可用")
    except ImportError:
        missing_deps.append("qrcode")
        print("❌ qrcode - 缺失")
    
    if missing_deps:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        input("按Enter键退出...")
        return
    
    print("\n🚀 正在启动GUI程序...")
    
    try:
        from gui.wechat_gui import WeChatDownloaderGUI
        import tkinter as tk
        
        # 创建并运行GUI
        root = tk.Tk()
        app = WeChatDownloaderGUI(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请检查文件是否完整")
        input("按Enter键退出...")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")

if __name__ == "__main__":
    main()
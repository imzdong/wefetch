#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cookie和Token获取辅助工具
"""

import re
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog

def get_cookie_format_example():
    """返回Cookie格式示例"""
    return """Cookie格式示例：
appmsglist_action_3094473706=card; 
ua_id=rTisf6no8nQ6Z2EpAAAAAE0nkbQrFlZq1A7-67LqGnU=; 
wxuin=22044998669898; 
uuid=e97fca24606f7c01a7fb3cd1ce3c8ae2; 
_clck=6s741v|1|fnt|0; 
rand_info=CAESIIFwJvXVCYaaNxOrlF5oVVrHO7PD4l0NSbFBr60xeihz; 
slave_bizuin=3094473706; 
data_bizuin=3094473706; 
bizuin=3094473706; 
data_ticket=PcUMElrHiY0jd+fBQkn8WWDrd7fNtben8VE3VYLs1YLSrcipat/O2soiIuY1LUeh; 
slave_sid=UFlGeE85Qm5nMzhsY1dQcXhZUV83ZWJfRHM0Z3NsSExYUkg4eE5ndjVqOXpDSVU4TE9sMXNHbHRRTXRRc3dBWDAyeHVyd2ZlTXBzbnI3V1BLSEV4RmFsNGlfSFpxdVo4RTJ4VnZIMVdxVG1iVzlNd2Y4bVVrcW9uQ2pYNWdPaWZuN0hMNDdTSWdEdHBIZUNq; 
slave_user=gh_195ed1058a3c; 
xid=8e39e241dcd2b96bb3d869f1049417a6; 
mm_lang=zh_CN; 
_clsk=hxabmm|1722044983139|3|1|mp.weixin.qq.com/weheat-agent/payload/record"""

def get_token_format_example():
    """返回Token格式示例"""
    return """Token格式：
在URL中找到 token= 参数，例如：
https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin=0&count=5&fakeid=...&token=223369894&...
                                                       ↑
                                                   这里的值就是token"""

def open_wechat_platform():
    """打开微信公众平台"""
    try:
        webbrowser.open('https://mp.weixin.qq.com/')
        messagebox.showinfo("提示", "已打开微信公众平台\n\n请按以下步骤操作：\n1. 使用微信扫码登录\n2. 登录成功后按F12\n3. 切换到Network标签\n4. 刷新页面\n5. 复制Cookie和Token")
    except Exception as e:
        messagebox.showerror("错误", f"无法打开浏览器: {e}")

def show_step_by_step_guide():
    """显示分步指导"""
    steps = """
📋 获取Cookie和Token详细步骤：

第1步：打开登录页面
• 浏览器访问：https://mp.weixin.qq.com/
• 使用微信扫描页面上的二维码登录

第2步：打开开发者工具
• 按 F12 打开开发者工具
• 切换到 Network (网络) 标签页

第3步：获取Cookie
• 刷新页面或点击其他链接
• 点击任意一个请求
• 在 Request Headers 中找到 Cookie 字段
• 复制完整的Cookie值

第4步：获取Token  
• 在URL中找到 token= 参数
• 复制token后面的值

第5步：填入程序
• 将Cookie粘贴到Cookie输入框
• 将Token粘贴到Token输入框
• 点击"保存配置"

💡 小提示：
• Cookie通常很长，包含多个参数
• Token通常是数字串
• 确保复制完整，不要遗漏
"""
    
    # 创建新窗口显示指导
    guide_window = tk.Toplevel()
    guide_window.title("获取Cookie和Token指导")
    guide_window.geometry("600x500")
    
    text_widget = tk.Text(guide_window, wrap=tk.WORD, padx=10, pady=10)
    text_widget.pack(fill='both', expand=True)
    
    text_widget.insert('1.0', steps)
    text_widget.config(state='disabled')
    
    close_btn = tk.Button(guide_window, text="关闭", command=guide_window.destroy)
    close_btn.pack(pady=10)

def create_cookie_helper_window():
    """创建Cookie获取辅助窗口"""
    root = tk.Tk()
    root.title("Cookie和Token获取助手")
    root.geometry("500x400")
    
    # 标题
    title_label = tk.Label(root, text="🔑 Cookie和Token获取助手", 
                         font=("Microsoft YaHei", 14, "bold"))
    title_label.pack(pady=20)
    
    # 按钮区域
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)
    
    open_btn = tk.Button(btn_frame, text="🌐 打开微信公众平台", 
                       command=open_wechat_platform, width=20, height=2)
    open_btn.pack(pady=10)
    
    guide_btn = tk.Button(btn_frame, text="📋 查看详细指导", 
                        command=show_step_by_step_guide, width=20, height=2)
    guide_btn.pack(pady=10)
    
    example_btn = tk.Button(btn_frame, text="📝 查看格式示例", 
                         command=lambda: messagebox.showinfo("格式示例", 
                            get_cookie_format_example() + "\n\n" + get_token_format_example()),
                         width=20, height=2)
    example_btn.pack(pady=10)
    
    # 说明文字
    info_text = """
💡 使用说明：
1. 点击"打开微信公众平台"登录
2. 按照提示获取Cookie和Token  
3. 在主程序的"手动配置"中填入信息
4. 点击"保存配置"完成登录

⚠️  注意事项：
• 请确保复制完整的Cookie
• Token通常在URL参数中
• Cookie失效后需要重新获取
"""
    
    info_label = tk.Label(root, text=info_text, justify='left', font=("Microsoft YaHei", 9))
    info_label.pack(pady=20, padx=20)
    
    root.mainloop()

if __name__ == "__main__":
    create_cookie_helper_window()
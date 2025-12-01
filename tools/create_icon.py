#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建GUI程序图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_wechat_icon():
    """创建微信公众号下载器图标"""
    
    # 创建不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 微信绿色
        wechat_green = (7, 193, 96)  # #07C160
        
        # 计算绘制参数
        margin = size // 16
        box_size = size - 2 * margin
        
        # 绘制圆角矩形背景
        if size >= 32:
            # 大尺寸用圆角矩形
            radius = size // 8
            draw.rounded_rectangle(
                [margin, margin, size - margin, size - margin],
                radius=radius,
                fill=wechat_green
            )
        else:
            # 小尺寸用普通矩形
            draw.rectangle(
                [margin, margin, size - margin, size - margin],
                fill=wechat_green
            )
        
        # 绘制微信对话图标（简化版）
        if size >= 48:
            # 大尺寸绘制详细图标
            chat_width = box_size // 2
            chat_height = chat_width // 2
            chat_x = (size - chat_width) // 2
            chat_y = (size - chat_height) // 2 - 2
            
            # 绘制两个对话气泡
            bubble1_size = chat_width // 3
            bubble2_size = chat_width // 4
            
            # 第一个气泡（较大）
            draw.ellipse(
                [chat_x - bubble1_size//2, chat_y - bubble1_size//3,
                 chat_x + bubble1_size//2, chat_y + bubble1_size//3],
                fill='white'
            )
            
            # 第二个气泡（较小）
            draw.ellipse(
                [chat_x + chat_width//3 - bubble2_size//2, 
                 chat_y + bubble1_size//3 - bubble2_size//3,
                 chat_x + chat_width//3 + bubble2_size//2,
                 chat_y + bubble1_size//3 + bubble2_size//3],
                fill='white'
            )
            
            # 下载箭头
            arrow_size = box_size // 6
            arrow_y = chat_y + chat_height + margin
            arrow_x = size // 2
            
            # 绘制下载箭头
            draw.polygon([
                (arrow_x, arrow_y + arrow_size//2),  # 底部中心
                (arrow_x - arrow_size//2, arrow_y),  # 左上
                (arrow_x - arrow_size//4, arrow_y),  # 左中
                (arrow_x - arrow_size//4, arrow_y - arrow_size//3),  # 左上角
                (arrow_x + arrow_size//4, arrow_y - arrow_size//3),  # 右上角
                (arrow_x + arrow_size//4, arrow_y),  # 右中
                (arrow_x + arrow_size//2, arrow_y),  # 右上
            ], fill='white')
            
        elif size >= 32:
            # 中等尺寸绘制简化图标
            draw.rectangle([size//4, size//3, 3*size//4, 2*size//3], fill='white')
            # 绘制下载箭头
            arrow_size = size // 8
            arrow_x = size // 2
            arrow_y = 2*size // 3 + size // 16
            draw.polygon([
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x - arrow_size//2, arrow_y),
                (arrow_x, arrow_y - arrow_size//2),
                (arrow_x + arrow_size//2, arrow_y),
            ], fill='white')
        else:
            # 小尺寸绘制最简图标
            draw.rectangle([size//4, size//3, 3*size//4, 2*size//3], fill='white')
            # 下载指示器
            draw.rectangle([3*size//8, 2*size//3, 5*size//8, 7*size//8], fill='white')
        
        # 保存图标
        img.save(f'icon_{size}x{size}.png')
        print(f"✅ 创建图标 {size}x{size}")
    
    # 创建ICO文件（Windows）
    create_ico_file(sizes)
    
    # 创建ICNS文件（macOS）- 可选
    # create_icns_file(sizes)

def create_ico_file(sizes):
    """创建Windows ICO文件"""
    try:
        images = []
        for size in sizes:
            if os.path.exists(f'icon_{size}x{size}.png'):
                img = Image.open(f'icon_{size}x{size}.png')
                images.append(img)
        
        # 保存为ICO文件
        images[0].save('wechat_downloader.ico', format='ICO', sizes=[(img.width, img.height) for img in images])
        print("✅ 创建 Windows ICO 图标")
        
    except Exception as e:
        print(f"⚠️ 创建ICO文件失败: {e}")

def create_app_icon():
    """创建应用专用图标"""
    # 创建一个更精美的256x256图标
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 微信绿色渐变背景
    wechat_green = (7, 193, 96)
    darker_green = (5, 150, 75)
    
    # 绘制渐变圆角矩形
    steps = 20
    for i in range(steps):
        ratio = i / steps
        color = (
            int(wechat_green[0] * (1 - ratio) + darker_green[0] * ratio),
            int(wechat_green[1] * (1 - ratio) + darker_green[1] * ratio),
            int(wechat_green[2] * (1 - ratio) + darker_green[2] * ratio)
        )
        radius = size // 8 - i
        draw.rounded_rectangle(
            [i, i, size - i, size - i],
            radius=radius,
            fill=color
        )
    
    # 绘制微信对话图标
    chat_width = size // 3
    chat_height = chat_width // 2
    chat_x = (size - chat_width) // 2
    chat_y = (size - chat_height) // 2 - 10
    
    # 绘制对话气泡
    bubble1_size = chat_width // 3
    bubble2_size = chat_width // 4
    
    # 第一个气泡
    draw.ellipse(
        [chat_x - bubble1_size//2, chat_y - bubble1_size//3,
         chat_x + bubble1_size//2, chat_y + bubble1_size//3],
        fill='white',
        outline='white',
        width=2
    )
    
    # 第二个气泡
    draw.ellipse(
        [chat_x + chat_width//3 - bubble2_size//2, 
         chat_y + bubble1_size//3 - bubble2_size//3,
         chat_x + chat_width//3 + bubble2_size//2,
         chat_y + bubble1_size//3 + bubble2_size//3],
        fill='white',
        outline='white',
        width=2
    )
    
    # 下载箭头
    arrow_size = box_size = size // 8
    arrow_y = chat_y + chat_height + 20
    arrow_x = size // 2
    
    # 绘制下载箭头
    draw.polygon([
        (arrow_x, arrow_y + arrow_size//2),  # 底部中心
        (arrow_x - arrow_size//2, arrow_y),  # 左上
        (arrow_x - arrow_size//4, arrow_y),  # 左中
        (arrow_x - arrow_size//4, arrow_y - arrow_size//3),  # 左上角
        (arrow_x + arrow_size//4, arrow_y - arrow_size//3),  # 右上角
        (arrow_x + arrow_size//4, arrow_y),  # 右中
        (arrow_x + arrow_size//2, arrow_y),  # 右上
    ], fill='white', outline='white')
    
    # 添加光泽效果
    for i in range(10):
        alpha = 20 - i * 2
        draw.ellipse(
            [size//4 - i*5, size//4 - i*5, 3*size//4 + i*5, size//2 + i*5],
            fill=(255, 255, 255, alpha)
        )
    
    img.save('app_icon.png')
    img.save('app_icon.ico', format='ICO')
    print("✅ 创建应用主图标 app_icon.png 和 app_icon.ico")

if __name__ == "__main__":
    print("=== 创建微信公众号下载器图标 ===")
    
    try:
        create_wechat_icon()
        create_app_icon()
        
        print("\n🎉 图标创建完成！")
        print("生成的文件:")
        print("- app_icon.png (PNG格式，256x256)")
        print("- app_icon.ico (Windows ICO格式)")
        print("- icon_16x16.png 到 icon_256x256.png (多尺寸)")
        
        print("\n💡 使用方法:")
        print("1. 将 app_icon.ico 复制为 wechat_downloader.ico")
        print("2. 在GUI程序中调用: root.iconphoto(True, ImageTk.PhotoImage(file='app_icon.png'))")
        
    except Exception as e:
        print(f"❌ 创建图标失败: {e}")
        print("💡 请确保安装了 Pillow 库: pip3 install Pillow")
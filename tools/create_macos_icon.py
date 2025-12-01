#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建macOS应用图标
"""

from PIL import Image, ImageDraw
import subprocess
import os

def create_macos_icns():
    """创建macOS ICNS图标文件"""
    
    # 创建不同尺寸的图标
    sizes = [16, 32, 128, 256, 512, 1024]
    iconset_dir = "AppIcon.iconset"
    
    # 创建图标集目录
    if os.path.exists(iconset_dir):
        subprocess.run(['rm', '-rf', iconset_dir])
    os.makedirs(iconset_dir)
    
    print("🎨 创建macOS应用图标...")
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 微信绿色
        wechat_green = (7, 193, 96)  # #07C160
        darker_green = (5, 150, 75)   # 深绿色
        
        # 绘制圆角矩形背景
        if size >= 32:
            radius = size // 8
            
            # 绘制渐变背景
            steps = min(20, size // 10)
            for i in range(steps):
                ratio = i / steps
                color = (
                    int(wechat_green[0] * (1 - ratio) + darker_green[0] * ratio),
                    int(wechat_green[1] * (1 - ratio) + darker_green[1] * ratio),
                    int(wechat_green[2] * (1 - ratio) + darker_green[2] * ratio)
                )
                current_radius = max(1, radius - i // 2)
                draw.rounded_rectangle(
                    [i, i, size - i, size - i],
                    radius=current_radius,
                    fill=color
                )
        else:
            # 小尺寸用普通矩形
            margin = size // 16
            draw.rectangle(
                [margin, margin, size - margin, size - margin],
                fill=wechat_green
            )
        
        # 绘制图标内容（大尺寸时）
        if size >= 128:
            # 绘制微信对话图标
            chat_width = size // 3
            chat_height = chat_width // 2
            chat_x = (size - chat_width) // 2
            chat_y = (size - chat_height) // 2 - 10
            
            # 对话气泡
            bubble1_size = chat_width // 3
            bubble2_size = chat_width // 4
            
            # 第一个气泡
            draw.ellipse(
                [chat_x - bubble1_size//2, chat_y - bubble1_size//3,
                 chat_x + bubble1_size//2, chat_y + bubble1_size//3],
                fill='white',
                outline='white',
                width=max(1, size // 256)
            )
            
            # 第二个气泡
            draw.ellipse(
                [chat_x + chat_width//3 - bubble2_size//2, 
                 chat_y + bubble1_size//3 - bubble2_size//3,
                 chat_x + chat_width//3 + bubble2_size//2,
                 chat_y + bubble1_size//3 + bubble2_size//3],
                fill='white',
                outline='white',
                width=max(1, size // 256)
            )
            
            # 下载箭头
            arrow_size = size // 12
            arrow_y = chat_y + chat_height + size // 20
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
            if size >= 256:
                for i in range(min(15, size // 20)):
                    alpha = max(5, 30 - i * 2)
                    draw.ellipse(
                        [size//3 - i*3, size//3 - i*3, 2*size//3 + i*3, size//2 + i*3],
                        fill=(255, 255, 255, alpha)
                    )
        
        elif size >= 32:
            # 中等尺寸绘制简化图标
            margin = size // 8
            box_width = size - 2 * margin
            box_height = box_width // 2
            box_x = margin
            box_y = (size - box_height) // 2
            
            # 绘制白色矩形和箭头
            draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], fill='white')
            
            # 箭头
            arrow_size = size // 10
            arrow_x = size // 2
            arrow_y = box_y + box_height + size // 20
            
            draw.polygon([
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x - arrow_size//2, arrow_y),
                (arrow_x, arrow_y - arrow_size//2),
                (arrow_x + arrow_size//2, arrow_y),
            ], fill='white')
        
        # 保存图标到图标集
        # macOS需要特定的命名格式
        if size == 16:
            img.save(f"{iconset_dir}/icon_16x16.png")
            img.save(f"{iconset_dir}/icon_32x32@2x.png")  # 2x版本
        elif size == 32:
            img.save(f"{iconset_dir}/icon_16x16@2x.png")
            img.save(f"{iconset_dir}/icon_32x32.png")
            img.save(f"{iconset_dir}/icon_64x64@2x.png")
        elif size == 128:
            img.save(f"{iconset_dir}/icon_128x128.png")
            img.save(f"{iconset_dir}/icon_256x256@2x.png")
        elif size == 256:
            img.save(f"{iconset_dir}/icon_128x128@2x.png")
            img.save(f"{iconset_dir}/icon_256x256.png")
            img.save(f"{iconset_dir}/icon_512x512@2x.png")
        elif size == 512:
            img.save(f"{iconset_dir}/icon_256x256@2x.png")
            img.save(f"{iconset_dir}/icon_512x512.png")
            img.save(f"{iconset_dir}/icon_1024x1024@2x.png")
        elif size == 1024:
            img.save(f"{iconset_dir}/icon_512x512@2x.png")
            img.save(f"{iconset_dir}/icon_1024x1024.png")
        
        print(f"✅ 创建图标 {size}x{size}")
    
    # 使用iconutil创建ICNS文件（macOS工具）
    try:
        result = subprocess.run(['iconutil', '-c', 'icns', iconset_dir], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 成功创建 ICNS 文件: AppIcon.icns")
            
            # 清理临时文件
            subprocess.run(['rm', '-rf', iconset_dir])
            
            # 复制为标准名称
            subprocess.run(['cp', 'AppIcon.icns', 'wechat_downloader.icns'])
            print("✅ 复制为 wechat_downloader.icns")
            
        else:
            print(f"❌ 创建ICNS失败: {result.stderr}")
            print("💡 请确保在macOS上运行此脚本")
            
    except FileNotFoundError:
        print("❌ 找不到iconutil工具")
        print("💡 此脚本需要在macOS上运行")
    
    except Exception as e:
        print(f"❌ 创建ICNS失败: {e}")

def create_simple_icon():
    """创建简单的PNG图标（备用方案）"""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 微信绿色背景
    wechat_green = (7, 193, 96)
    radius = size // 8
    draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=wechat_green)
    
    # 绘制简单的下载图标
    box_size = size // 3
    box_x = (size - box_size) // 2
    box_y = (size - box_size) // 2 - 10
    
    # 白色矩形
    draw.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], fill='white')
    
    # 下载箭头
    arrow_size = size // 8
    arrow_x = size // 2
    arrow_y = box_y + box_size + 20
    
    draw.polygon([
        (arrow_x, arrow_y + arrow_size//2),
        (arrow_x - arrow_size//2, arrow_y),
        (arrow_x, arrow_y - arrow_size//2),
        (arrow_x + arrow_size//2, arrow_y),
    ], fill='white')
    
    img.save('wechat_downloader.png')
    print("✅ 创建备用图标: wechat_downloader.png")

if __name__ == "__main__":
    print("=== 创建macOS应用图标 ===")
    
    try:
        # 尝试创建完整的ICNS文件
        create_macos_icns()
        
        # 创建备用PNG图标
        create_simple_icon()
        
        print("\n🎉 图标创建完成！")
        print("生成的文件:")
        print("- AppIcon.icns (macOS ICNS格式)")
        print("- wechat_downloader.icns (重命名的ICNS)")
        print("- wechat_downloader.png (PNG备用图标)")
        
        print("\n💡 使用方法:")
        print("1. ICNS文件用于macOS应用包")
        print("2. PNG文件可在GUI中使用:")
        print("   root.iconphoto(True, ImageTk.PhotoImage(file='wechat_downloader.png'))")
        
    except Exception as e:
        print(f"❌ 创建图标失败: {e}")
        print("💡 请确保安装了 Pillow 库")
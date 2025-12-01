# 微信公众号文章下载器

一个功能强大的微信公众号文章批量下载工具，支持文章导出为 Markdown 和 HTML 格式。

## 🌟 功能特性

- 📱 **多种登录方式**：支持二维码登录、手动配置登录、Selenium 自动登录
- 📚 **批量下载**：支持一键下载公众号所有文章
- 🎯 **精准搜索**：支持搜索并下载指定公众号的文章
- 💾 **多格式导出**：支持 Markdown、HTML 格式导出
- 🖼️ **图片本地化**：自动下载并本地化文章中的图片
- 🌐 **跨平台支持**：支持 Windows、macOS、Linux

## 📁 项目结构

```
wechat/
├── gui/                    # GUI 界面
│   └── wechat_gui.py      # 主界面
├── core/                   # 核心功能
│   ├── wechat_downloader_core.py
│   └── wechat2md.py
├── login/                  # 登录模块
│   ├── wechat_login.py
│   ├── real_qr_login.py
│   ├── working_wechat_login.py
│   ├── selenium_wechat_login.py
│   └── ...
├── data/                   # 数据和配置
│   ├── config.py
│   ├── cookie_helper.py
│   └── mp_cookies.json
├── tools/                  # 工具脚本
│   ├── create_icon.py
│   └── create_macos_icon.py
├── scripts/                # 启动脚本
│   ├── start_gui.py
│   └── run_gui.py
├── icons/                  # 图标资源
│   ├── wechat_downloader.png
│   ├── app_icon.png
│   └── ...
├── docs/                   # 文档
│   └── README_GUI.md
├── articles/               # 下载的文章目录
└── requirements.txt        # 依赖包
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动程序

#### 方式一：使用启动脚本（推荐）
```bash
python scripts/start_gui.py
```

#### 方式二：直接运行GUI
```bash
python -m gui.wechat_gui
```

#### 方式三：使用详细启动脚本
```bash
python scripts/run_gui.py
```

## 📖 使用说明

### 登录方式

1. **二维码登录**：显示二维码，使用微信扫码登录
2. **手动配置**：手动输入 token 和 cookie
3. **Selenium 登录**：自动化浏览器登录（需安装浏览器驱动）

### 下载文章

1. 在登录界面选择登录方式并完成登录
2. 在"搜索公众号"标签页搜索公众号
3. 选择要下载的文章
4. 在"导出设置"标签页选择导出格式和路径
5. 开始下载

## 🛠️ 依赖要求

- Python 3.7+
- tkinter
- requests
- beautifulsoup4
- Pillow
- qrcode
- markdownify
- openpyxl
- selenium（可选，用于自动登录）

## 📋 主要文件说明

- **gui/wechat_gui.py**：主程序界面
- **core/wechat_downloader_core.py**：核心下载逻辑
- **core/wechat2md.py**：HTML 转 Markdown 工具
- **login/**：各种登录方式的实现
- **scripts/start_gui.py**：推荐使用的启动脚本

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**注意**：本工具仅供学习和个人使用，请遵守相关法律法规和微信平台的使用条款。
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信文章下载核心功能模块
"""

import requests
import markdownify
from bs4 import BeautifulSoup
import re
import unicodedata
import hashlib
import time
import json
import csv
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path
import os


@dataclass
class ContentFilterConfig:
    """内容过滤配置"""
    paragraph_keywords: List[str] = field(default_factory=list)
    image_hashes: List[str] = field(default_factory=list)
    skip_ads: bool = False
    skip_promotions: bool = False


class WeChatArticleDownloader:
    """微信公众号文章下载器核心类"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.filter_config = ContentFilterConfig()
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            "User-Agent": self.config.get('user_agent', 
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"),
            "Referer": "https://mp.weixin.qq.com/"
        })
        
        if self.config.get('cookie'):
            self.session.headers["Cookie"] = self.config['cookie']

    @staticmethod
    def hash_byte_data(byte_data: bytes) -> str:
        """计算字节数据的哈希值"""
        return hashlib.sha256(byte_data).hexdigest()

    @staticmethod
    def remove_nonvisible_chars(text: str) -> str:
        """移除不可见字符"""
        return ''.join(c for c in text if (unicodedata.category(c) != 'Cn'
                                           and c not in (' ', '\n', '\r')))

    def search_accounts(self, keyword: str, token: str) -> List[Dict]:
        """搜索公众号"""
        try:
            url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"
            params = {
                "action": "search_biz",
                "begin": 0,
                "count": 5,
                "query": keyword,
                "fingerprint": "218c2fd3f4653e1a13b56f5e90c5a675",
                "token": token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('base_resp', {}).get('ret') == 0:
                return data.get('list', [])
            else:
                raise Exception(data.get('base_resp', {}).get('err_msg', '搜索失败'))
                
        except Exception as e:
            raise Exception(f"搜索公众号失败: {str(e)}")

    def get_articles_list(self, fakeid: str, token: str, page: int = 1, count: int = 5) -> List[Dict]:
        """获取文章列表"""
        try:
            url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
            params = {
                "action": "list_ex",
                "begin": (page - 1) * count,
                "count": count,
                "fakeid": fakeid,
                "type": "9",
                "token": token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('base_resp', {}).get('ret') == 0:
                return data.get('app_msg_list', [])
            else:
                raise Exception(data.get('base_resp', {}).get('err_msg', '获取文章列表失败'))
                
        except Exception as e:
            raise Exception(f"获取文章列表失败: {str(e)}")

    def get_article_content(self, url: str, max_retries: int = 3) -> Dict:
        """获取文章内容"""
        retries = 0
        while retries < max_retries:
            try:
                print(f"正在获取文章内容: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'lxml')
                title_element = soup.find('h1', id="activity-name")
                
                if not title_element:
                    title_element = soup.find('h2', class_="rich_media_title") or \
                                    soup.find('h1', class_="article-title")

                if not title_element:
                    raise AttributeError("Title element not found")

                title = title_element.text.strip()
                
                # 获取发布时间
                create_time = ""
                match = re.search(r'createTime\s+=\s*\'(.*)\'', str(soup))
                if match:
                    create_time = match.group(1)
                
                # 获取内容
                content_soup = soup.find('div', {'class': 'rich_media_content'})
                if not content_soup:
                    content_soup = soup.find('div', {'id': 'js_content'})
                
                if not content_soup:
                    raise Exception("无法找到文章内容")

                # 验证必要的数据
                if not title:
                    title = "未命名文章"
                
                # 确保content_soup不为None
                if content_soup is None:
                    raise Exception("文章内容解析失败")

                # 验证数据完整性
                if not title:
                    title = "未命名文章"
                
                if not content_soup:
                    raise Exception("文章内容解析失败：content_soup为空")
                
                # 确保content_soup是BeautifulSoup对象
                if not hasattr(content_soup, 'find_all'):
                    raise Exception(f"文章内容格式错误：content_soup不是BeautifulSoup对象，类型为{type(content_soup)}")
                
                # 检查content_soup的copy方法
                if not hasattr(content_soup, 'copy'):
                    print(f"警告：content_soup没有copy方法，类型: {type(content_soup)}")
                    # 尝试重新创建
                    content_soup = BeautifulSoup(str(content_soup), 'html.parser')
                elif not callable(getattr(content_soup, 'copy')):
                    print(f"警告：content_soup.copy不是可调用的，类型: {type(content_soup)}")
                    content_soup = BeautifulSoup(str(content_soup), 'html.parser')
                
                result = {
                    'title': title,
                    'create_time': create_time,
                    'content_soup': content_soup,
                    'url': url,
                    'full_soup': soup
                }
                
                print(f"文章内容获取成功，标题: {title}")
                print(f"content_soup类型: {type(content_soup)}, 是否有copy方法: {hasattr(content_soup, 'copy')}")
                return result

            except Exception as e:
                print(f"获取文章内容失败 (尝试 {retries + 1}/{max_retries}): {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(2 ** retries)
                else:
                    raise Exception(f"获取文章内容失败: {str(e)}")

    def download_images(self, soup: BeautifulSoup, output_dir: str) -> None:
        """下载文章中的所有图片并保存到本地"""
        # 创建images目录
        image_folder = os.path.join(output_dir, 'images')
        os.makedirs(image_folder, exist_ok=True)
        
        for img in soup.find_all('img'):
            img_link = img.get('data-src') or img.get('src')
            if not img_link:
                continue
                
            img_link = img_link.replace(' ', '%20')

            if not img_link.startswith(('http://', 'https://')):
                img_link = 'https://mp.weixin.qq.com' + img_link
                
            try:
                with requests.get(img_link, stream=True, timeout=10) as response:
                    response.raise_for_status()
                    file_content = response.content

                    img_hash = self.hash_byte_data(file_content)
                    if img_hash in self.filter_config.image_hashes:
                        continue
                        
                    file_ext = (img.get('data-type') or 'jpg').split('?')[0]
                    filename = f"{img_hash}.{file_ext}"
                    filepath = os.path.join(image_folder, filename)

                    if not os.path.exists(filepath):
                        with open(filepath, 'wb') as f:
                            f.write(file_content)
                    
                    # 更新图片属性指向本地文件
                    relative_path = f"./images/{filename}"
                    img['data-src'] = relative_path
                    img['src'] = relative_path
                    
            except requests.exceptions.RequestException as e:
                print(f"图片下载失败，URL: {img_link}, 错误: {e}")

    def convert_to_markdown(self, article_data: Dict, output_dir: str) -> str:
        """将文章内容转换为Markdown格式"""
        content_soup = article_data.get('content_soup')
        if content_soup is None:
            raise Exception("文章内容为空，无法转换为Markdown")
        
        # 确保content_soup是BeautifulSoup对象
        if isinstance(content_soup, str):
            print("检测到content_soup是字符串，正在转换为BeautifulSoup对象...")
            content_soup = BeautifulSoup(content_soup, 'html.parser')
        elif not hasattr(content_soup, 'find_all'):
            raise Exception(f"文章内容格式错误，期望BeautifulSoup对象，实际类型: {type(content_soup)}")
        
        # 下载图片
        self.download_images(content_soup, output_dir)
        
        # 转换为Markdown
        markdown_content = markdownify.markdownify(str(content_soup))
        
        # 处理图片路径
        markdown_soup = BeautifulSoup(markdown_content, 'html.parser')
        for img in markdown_soup.find_all('img'):
            if img.get('data-src') and not img['data-src'].startswith(('http://', 'https://')):
                img['src'] = img['data-src']
        markdown_content = '\n'.join([line + '\n' for line in markdown_content.split('\n') if line.strip()])
        
        # 清理标题
        clean_title = self.remove_nonvisible_chars(article_data['title'])
        
        # 格式化时间
        create_time_str = ""
        if article_data['create_time']:
            try:
                create_time_str = time.strftime("%Y-%m-%d %H:%M:%S", 
                                               time.localtime(int(article_data['create_time'])))
            except:
                create_time_str = article_data['create_time']
        
        # 构建完整Markdown
        markdown = f"# {clean_title}\n\n"
        if create_time_str:
            markdown += f"发布时间: {create_time_str}\n\n"
        markdown += f"原文链接: {article_data['url']}\n\n"
        markdown += markdown_content
        
        # 清理多余字符
        markdown = re.sub('\xa0{1,}', '\n', markdown, flags=re.UNICODE)
        markdown = re.sub(r'\]\(http([^)]*)\)',
                          lambda x: '](http' + x.group(1).replace(' ', '%20') + ')',
                          markdown)
        
        # 确保不过滤时出现问题
        try:
            filtered_markdown = self.filter_content(markdown) if self.filter_content else markdown
        except Exception as e:
            print(f"过滤markdown内容时出错: {e}")
            filtered_markdown = markdown
        
        return filtered_markdown, clean_title

    def convert_to_html(self, article_data: Dict, output_dir: str) -> str:
        """将文章内容转换为HTML格式"""
        content_soup = article_data.get('content_soup')
        if content_soup is None:
            raise Exception("文章内容为空，无法转换为HTML")
        
        # 确保content_soup是BeautifulSoup对象
        if isinstance(content_soup, str):
            print("检测到content_soup是字符串，正在转换为BeautifulSoup对象...")
            content_soup = BeautifulSoup(content_soup, 'html.parser')
        elif not hasattr(content_soup, 'find_all'):
            raise Exception(f"content_soup不是有效的HTML对象，类型: {type(content_soup)}")
        
        # 创建内容副本进行清理
        try:
            content_soup = content_soup.copy()
        except Exception as e:
            print(f"复制content_soup失败，尝试直接使用: {e}")
            # 如果复制失败，直接使用原对象
        
        # 移除隐藏样式
        if content_soup.get('style'):
            content_soup['style'] = content_soup['style'].replace('visibility: hidden;', '').replace('opacity: 0;', '')
        
        # 移除所有隐藏元素的style属性
        for element in content_soup.find_all(style=True):
            if 'visibility: hidden' in element.get('style', '') or 'opacity: 0' in element.get('style', ''):
                element['style'] = element['style'].replace('visibility: hidden;', '').replace('opacity: 0;', '')
        
        # 清理微信特有的标签和属性
        for tag in content_soup.find_all():
            # 移除微信特有属性
            attrs_to_remove = ['data-pm-slice', 'leaf', 'textstyle', 'nodeleaf', 'data-backh', 'data-backw', 'data-imgfileid', 
                              'data-ratio', 'data-s', 'data-type', 'data-w', 'type']
            for attr in attrs_to_remove:
                if tag.get(attr):
                    del tag[attr]
            
            # 清理class属性
            if tag.get('class'):
                # 保留一些有用的class，移除微信特有的
                classes = tag['class']
                if isinstance(classes, list):
                    tag['class'] = [c for c in classes if not c.startswith(('js_', 'rich_media_', 'wxw-', 'autoTypeSetting'))]
                    if not tag['class']:
                        del tag['class']
                else:
                    tag['class'] = ''
        
        # 下载图片
        self.download_images(content_soup, output_dir)
        
        # 清理HTML内容，移除空的span和font标签
        for empty_span in content_soup.find_all('span'):
            if not empty_span.get_text(strip=True) and not empty_span.find('img'):
                empty_span.decompose()
        
        for empty_font in content_soup.find_all('font'):
            if not empty_font.get_text(strip=True) and not empty_font.find('img'):
                empty_font.decompose()
        
        # 获取清理后的HTML内容
        clean_content = str(content_soup)
        
        # 创建完整的HTML
        title = article_data['title']
        
        # 格式化时间
        create_time_str = ""
        if article_data['create_time']:
            try:
                create_time_str = time.strftime("%Y-%m-%d %H:%M:%S", 
                                               time.localtime(int(article_data['create_time'])))
            except:
                create_time_str = article_data['create_time']
        
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .article-header {{
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .article-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .article-meta {{
            color: #666;
            font-size: 14px;
        }}
        .article-content {{
            font-size: 16px;
        }}
        .article-content p {{
            margin-bottom: 1em;
            line-height: 1.75em;
        }}
        .article-content section {{
            text-align: center;
            margin: 2em 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10px auto;
        }}
    </style>
</head>
<body>
    <div class="article-header">
        <h1 class="article-title">{title}</h1>
        <div class="article-meta">
            {'发布时间: ' + create_time_str if create_time_str else ''}
            <br>
            <a href="{article_data['url']}" target="_blank">原文链接</a>
        </div>
    </div>
    <div class="article-content">
        {clean_content}
    </div>
</body>
</html>"""
        
        # 确保返回值不为None
        if html_template is None:
            html_template = ""
        if title is None:
            title = "untitled"
            
        return html_template, title

    def filter_content(self, text: str) -> str:
        """过滤内容"""
        try:
            if self.filter_config and self.filter_config.paragraph_keywords:
                text = self._filter_paragraphs(text, self.filter_config.paragraph_keywords)
            return text
        except Exception as e:
            print(f"过滤内容时出错: {e}")
            return text

    def _filter_paragraphs(self, text: str, keywords: List[str]) -> str:
        """过滤包含特定关键词的段落"""
        lines = [line.strip() for line in text.split('\n')]
        filtered_lines = []
        current_paragraph = []

        for line in lines:
            if not line.strip():
                if not self._paragraph_contains_keywords(current_paragraph, keywords):
                    filtered_lines.extend(current_paragraph)
                current_paragraph = []
            else:
                current_paragraph.append(line)
                
        if not self._paragraph_contains_keywords(current_paragraph, keywords):
            filtered_lines.extend(current_paragraph)
            
        return '\n\n'.join(filtered_lines) + '\n\n'

    def _paragraph_contains_keywords(self, paragraph: List[str], keywords: List[str]) -> bool:
        """检查段落是否包含关键词"""
        paragraph_text = ' '.join(paragraph)
        return any(keyword in paragraph_text for keyword in keywords)

    def save_article(self, article_data: Dict, output_dir: str, format_type: str = 'markdown') -> str:
        """保存文章"""
        try:
            print(f"开始保存文章，格式: {format_type}")
            print(f"文章数据: {list(article_data.keys())}")
            
            # 验证文章数据完整性
            if not article_data or not isinstance(article_data, dict):
                raise Exception("文章数据为空或格式错误")
            
            if 'content_soup' not in article_data:
                raise Exception("文章数据中缺少content_soup字段")
            
            content_soup = article_data['content_soup']
            if content_soup is None:
                raise Exception("文章内容为空，可能是获取文章内容时失败")
            
            print(f"content_soup详细信息: 类型={type(content_soup)}, 值={content_soup}")
            
            if not hasattr(content_soup, 'copy'):
                raise Exception(f"content_soup对象错误，无法调用copy方法，类型: {type(content_soup)}")
            
            if 'title' not in article_data or not article_data['title']:
                raise Exception("文章标题为空")
            
            if format_type == 'markdown':
                print("调用convert_to_markdown...")
                result = self.convert_to_markdown(article_data, output_dir)
                print(f"convert_to_markdown返回: {type(result)}, 值: {result}")
                if not isinstance(result, tuple) or len(result) != 2:
                    raise Exception(f"convert_to_markdown返回值错误: {result}")
                content, clean_title = result
                filename = f"{clean_title}.md"
            else:  # html
                print("调用convert_to_html...")
                result = self.convert_to_html(article_data, output_dir)
                print(f"convert_to_html返回: {type(result)}, 值: {result}")
                if not isinstance(result, tuple) or len(result) != 2:
                    raise Exception(f"convert_to_html返回值错误: {result}")
                content, clean_title = result
                filename = f"{clean_title}.html"
            
            print(f"清理前的文件名: {clean_title}")
            # 清理文件名
            filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
            print(f"清理后的文件名: {filename}")
            filepath = os.path.join(output_dir, filename)
            
            # 确保目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"保存文件到: {filepath}")
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"保存文章详细错误: {error_detail}")
            raise Exception(f"保存文章失败: {str(e)}")
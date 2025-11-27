"""
文档解析器模块

该模块负责解析各种格式的文档，包括：
- PDF文档解析
- Word文档解析
- PowerPoint文档解析
- 文本文件解析
- 图像文档解析（OCR）
- Markdown文档解析

主要功能：
1. 识别文档格式
2. 提取文档内容
3. 处理文档元数据
4. 支持多语言文档解析

对每个文档进行解析，解析的结果包括一个纯文本的md, 一个images目录，包括所有的图表，一个pages目录，包括所有的页面


work_dir
|-- file_name.md
|-- images
|   |-- image1.png
|   |-- image2.jpg
|   |-- ...
|-- pages
|   |-- page1.png
|   |-- page2.png
|   |-- ...
"""
import os
import shutil
import tempfile
import time
import uuid
import zipfile
from typing import Optional

import fitz
import pdfplumber
import requests

from ..utils import oss_utils, download_utils
from ..utils.logger_utils import logger


def ensure_dir_exists(dir_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


class DocumentParser:
    """文档解析器基类"""

    def __init__(self, work_dir: str, file_path: str):
        self._work_dir = work_dir
        self._file_path = file_path
        basename = os.path.basename(file_path)
        self._filename = os.path.splitext(basename)[0]
        self._file_extension = os.path.splitext(basename)[1]
        self._md_file_path = os.path.join(work_dir, f"{self._filename}.md")
        self._images_dir = os.path.join(work_dir, "images")
        self._pages_dir = os.path.join(work_dir, "pages")

        ensure_dir_exists(self._work_dir)
        ensure_dir_exists(self._images_dir)
        ensure_dir_exists(self._pages_dir)

    @property
    def md_file_path(self):
        return self._md_file_path

    @property
    def images_dir(self):
        return self._images_dir

    @property
    def pages_dir(self):
        return self._pages_dir

    def parsed_text(self):
        if not os.path.exists(self.md_file_path):
            return ""
        with open(self.md_file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text

    def parsed_images(self) -> list[str]:
        """列出所有图片的文件路径"""
        return [os.path.abspath(os.path.join(self.images_dir, img)) for img in os.listdir(self.images_dir)]

    def parsed_pages(self):
        """列出所有页面的文件路径"""
        return [os.path.abspath(os.path.join(self.pages_dir, page)) for page in os.listdir(self.pages_dir)]


class DocxDocumentParser(DocumentParser):
    """Docx文档解析器"""

    def __init__(self, work_dir: str, file_path: str):
        super().__init__(work_dir, file_path)

    def parse(self):
        """
        解析docx文档

        执行完整的解析流程：
        1. 提取文本内容和图片
        2. 将每页转换为图片
        """
        try:
            logger.info(f"开始解析 docx 文档: {self._file_path}")

            # 解析内容（文本和图片）
            self.parse_content()

            # 解析页面（每页转为图片）
            self.parse_pages()

            logger.info(f"docx 文档解析完成: {self._file_path}")
            return True
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"解析 docx 文档失败: {self._file_path}, 错误: {e}")
            return False

    def _detect_chinese_heading(self, text: str) -> int:
        """
        检测中文层级结构并返回对应的标题级别

        支持的格式：
        - 一、二、三、... → ## (level 2)
        - （一）（二）（三）... → ### (level 3)
        - 1. 2. 3. ... → #### (level 4)
        - (1) (2) (3) ... → ##### (level 5)

        Args:
            text: 段落文本

        Returns:
            int: 标题级别 (2-5)，如果不是标题则返回 0
        """
        import re

        # 一、二、三、四、五、六、七、八、九、十
        if re.match(r'^[一二三四五六七八九十]+、', text):
            return 2

        # （一）（二）（三）
        if re.match(r'^[（(][一二三四五六七八九十]+[）)]', text):
            return 3

        # 1. 2. 3. (数字后面跟点和空格或直接是内容)
        if re.match(r'^\d+[.、]', text):
            return 4

        # (1) (2) (3)
        if re.match(r'^[（(]\d+[）)]', text):
            return 5

        return 0

    def _accept_all_revisions(self, doc):
        """
        接受文档中的所有修订

        Word 的修订模式（Track Changes）会导致内容无法正常读取。
        此方法会删除所有修订标记，保留最终内容。

        Args:
            doc: Document 对象
        """
        try:
            from docx.oxml import parse_xml
            from docx.oxml.ns import qn

            logger.info("检查并处理文档修订...")

            # 获取文档的 XML
            body = doc.element.body

            # 删除所有的删除标记 (w:del)
            for del_element in body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}del'):
                parent = del_element.getparent()
                if parent is not None:
                    parent.remove(del_element)

            # 处理所有的插入标记 (w:ins) - 保留内容，删除标记
            for ins_element in body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ins'):
                parent = ins_element.getparent()
                if parent is not None:
                    # 将插入标记中的内容移到父元素
                    index = list(parent).index(ins_element)
                    for child in list(ins_element):
                        parent.insert(index, child)
                        index += 1
                    # 删除插入标记
                    parent.remove(ins_element)

            # 删除所有的移动标记 (w:moveFrom, w:moveTo)
            for move_from in body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}moveFrom'):
                parent = move_from.getparent()
                if parent is not None:
                    parent.remove(move_from)

            for move_to in body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}moveTo'):
                parent = move_to.getparent()
                if parent is not None:
                    # 将移动标记中的内容移到父元素
                    index = list(parent).index(move_to)
                    for child in list(move_to):
                        parent.insert(index, child)
                        index += 1
                    # 删除移动标记
                    parent.remove(move_to)

            logger.info("文档修订处理完成")

        except Exception as e:
            logger.warning(f"处理文档修订时出错: {e}，将尝试继续解析")
            # 即使处理修订失败，也继续解析文档

    def parse_content(self):
        """
        读取docx的文件内容，文字写到md里，图片写到images里

        功能：
        1. 提取文档中的所有文本内容
        2. 提取文档中的所有图片
        3. 将文本转换为 Markdown 格式
        4. 保存图片到 images 目录
        """
        try:
            from docx import Document
            from docx.oxml.text.paragraph import CT_P
            from docx.oxml.table import CT_Tbl
            from docx.table import _Cell, Table
            from docx.text.paragraph import Paragraph

            logger.info(f"开始提取 docx 内容: {os.path.abspath(self._file_path)}")

            # 打开文档
            doc = Document(self._file_path)

            # 处理修订模式：接受所有修订
            self._accept_all_revisions(doc)

            # 用于存储 Markdown 内容
            md_content = []

            # 图片计数器
            image_counter = 0

            # 遍历文档中的所有元素（段落和表格）
            for element in doc.element.body:
                if isinstance(element, CT_P):
                    # 处理段落
                    paragraph = Paragraph(element, doc)

                    # 先处理段落文本
                    text = paragraph.text.strip()
                    if text:
                        # 根据段落样式转换为 Markdown
                        style = paragraph.style.name if paragraph.style else ""

                        if "Heading 1" in style:
                            md_content.append(f"\n# {text}\n\n")
                        elif "Heading 2" in style:
                            md_content.append(f"\n## {text}\n\n")
                        elif "Heading 3" in style:
                            md_content.append(f"\n### {text}\n\n")
                        elif "Heading 4" in style:
                            md_content.append(f"\n#### {text}\n\n")
                        elif "Heading 5" in style:
                            md_content.append(f"\n##### {text}\n\n")
                        elif "Heading 6" in style:
                            md_content.append(f"\n###### {text}\n\n")
                        else:
                            # 检测中文层级结构并转换为标题
                            heading_level = self._detect_chinese_heading(text)
                            if heading_level:
                                md_content.append(f"\n{'#' * heading_level} {text}\n\n")
                            else:
                                # 普通段落，添加空行分隔
                                md_content.append(f"{text}\n\n")

                    # 然后提取段落中的图片
                    for run in paragraph.runs:
                        # 检查是否包含图片
                        for drawing in run.element.findall(
                                './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'):
                            # 提取图片
                            for blip in drawing.findall(
                                    './/{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                                embed_id = blip.get(
                                    '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                                if embed_id:
                                    image_part = doc.part.related_parts[embed_id]
                                    image_counter += 1
                                    image_filename = f"image_{image_counter}.png"
                                    image_path = os.path.join(self._images_dir, image_filename)

                                    # 保存图片
                                    with open(image_path, 'wb') as f:
                                        f.write(image_part.blob)

                                    logger.debug(f"提取图片: {image_filename}")

                                    # 在 Markdown 中添加图片引用
                                    md_content.append(f"\n![{image_filename}](images/{image_filename})\n")

                elif isinstance(element, CT_Tbl):
                    # 处理表格
                    table = Table(element, doc)
                    md_content.append("\n")

                    # 表格头部
                    if len(table.rows) > 0:
                        header_cells = table.rows[0].cells
                        header = "| " + " | ".join([cell.text.strip() for cell in header_cells]) + " |"
                        md_content.append(header + "\n")

                        # 表格分隔符
                        separator = "| " + " | ".join(["---" for _ in header_cells]) + " |"
                        md_content.append(separator + "\n")

                        # 表格内容
                        for row in table.rows[1:]:
                            cells = row.cells
                            row_text = "| " + " | ".join([cell.text.strip() for cell in cells]) + " |"
                            md_content.append(row_text + "\n")

                    md_content.append("\n")

            # 写入 Markdown 文件
            with open(self._md_file_path, 'w', encoding='utf-8') as f:
                f.writelines(md_content)

            logger.info(f"内容提取完成，共提取 {image_counter} 张图片")
            logger.info(f"Markdown 文件已保存: {self._md_file_path}")

        except ImportError:
            logger.error("未安装 python-docx 库，请运行: pip install python-docx")
            raise
        except Exception as e:
            logger.error(f"提取 docx 内容失败: {e}")
            raise

    def parse_pages(self):
        """
        把docx的每页作为图片，保存到pages

        功能：
        1. 将 docx 文档转换为 PDF
        2. 将 PDF 的每一页转换为图片
        3. 保存到 pages 目录

        注意：此功能需要安装以下依赖之一：
        - Windows: Microsoft Word (通过 COM)
        - Linux/Mac: LibreOffice
        - 或使用 docx2pdf 库
        """
        try:
            logger.info(f"开始将 docx 转换为页面图片: {self._file_path}")

            # 尝试使用不同的方法转换
            success = False

            # 方法1: 尝试使用 docx2pdf (Windows)
            if os.name == 'nt':
                success = self._convert_with_docx2pdf()

            # 方法2: 尝试使用 LibreOffice (跨平台)
            if not success:
                success = self._convert_with_libreoffice()

            # 方法3: 尝试使用 unoconv (Linux)
            if not success:
                success = self._convert_with_unoconv()

            if not success:
                logger.warning(
                    "无法将 docx 转换为页面图片。请安装以下工具之一：\n"
                    "- Windows: pip install docx2pdf (需要 Microsoft Word)\n"
                    "- Linux/Mac: 安装 LibreOffice\n"
                    "- Linux: 安装 unoconv"
                )
                return False

            logger.info(f"页面图片转换完成")
            return True

        except Exception as e:
            logger.error(f"转换页面图片失败: {e}")
            return False

    def _convert_with_docx2pdf(self) -> bool:
        """
        使用 docx2pdf 库转换（Windows，需要 Microsoft Word）

        Returns:
            bool: 是否转换成功
        """
        try:
            from docx2pdf import convert
            import pdf2image

            logger.info("尝试使用 docx2pdf 转换...")

            # 转换为 PDF
            pdf_path = os.path.join(self._work_dir, f"{self._filename}.pdf")
            convert(self._file_path, pdf_path)

            # 将 PDF 转换为图片
            images = pdf2image.convert_from_path(pdf_path)

            # 保存每一页
            for i, image in enumerate(images, start=1):
                page_filename = f"page_{i}.png"
                page_path = os.path.join(self._pages_dir, page_filename)
                image.save(page_path, 'PNG')
                logger.debug(f"保存页面: {page_filename}")

            # 删除临时 PDF 文件
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            logger.info(f"使用 docx2pdf 转换成功，共 {len(images)} 页")
            return True

        except ImportError:
            logger.debug("docx2pdf 或 pdf2image 未安装")
            return False
        except Exception as e:
            logger.debug(f"docx2pdf 转换失败: {e}")
            return False

    def _convert_with_libreoffice(self) -> bool:
        """
        使用 LibreOffice 转换（跨平台）

        Returns:
            bool: 是否转换成功
        """
        try:
            import subprocess
            import pdf2image

            logger.info("尝试使用 LibreOffice 转换...")

            # 检查 LibreOffice 是否安装
            libreoffice_cmd = None
            for cmd in ['libreoffice', 'soffice']:
                try:
                    subprocess.run([cmd, '--version'],
                                   capture_output=True,
                                   check=True,
                                   timeout=5)
                    libreoffice_cmd = cmd
                    break
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue

            if not libreoffice_cmd:
                logger.debug("LibreOffice 未安装")
                return False

            # 转换为 PDF
            pdf_path = os.path.join(self._work_dir, f"{self._filename}.pdf")

            # 使用 LibreOffice 转换
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', self._work_dir,
                self._file_path
            ]

            result = subprocess.run(cmd,
                                    capture_output=True,
                                    text=True,
                                    timeout=60)

            if result.returncode != 0:
                logger.debug(f"LibreOffice 转换失败: {result.stderr}")
                return False

            # 检查 PDF 是否生成
            if not os.path.exists(pdf_path):
                logger.debug("PDF 文件未生成")
                return False

            # 将 PDF 转换为图片
            images = pdf2image.convert_from_path(pdf_path)

            # 保存每一页
            for i, image in enumerate(images, start=1):
                page_filename = f"page_{i}.png"
                page_path = os.path.join(self._pages_dir, page_filename)
                image.save(page_path, 'PNG')
                logger.debug(f"保存页面: {page_filename}")

            # 删除临时 PDF 文件
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            logger.info(f"使用 LibreOffice 转换成功，共 {len(images)} 页")
            return True

        except ImportError:
            logger.debug("pdf2image 未安装")
            return False
        except subprocess.TimeoutExpired:
            logger.debug("LibreOffice 转换超时")
            return False
        except Exception as e:
            logger.debug(f"LibreOffice 转换失败: {e}")
            return False

    def _convert_with_unoconv(self) -> bool:
        """
        使用 unoconv 转换（Linux）

        Returns:
            bool: 是否转换成功
        """
        try:
            import subprocess
            import pdf2image

            logger.info("尝试使用 unoconv 转换...")

            # 检查 unoconv 是否安装
            try:
                subprocess.run(['unoconv', '--version'],
                               capture_output=True,
                               check=True,
                               timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                logger.debug("unoconv 未安装")
                return False

            # 转换为 PDF
            pdf_path = os.path.join(self._work_dir, f"{self._filename}.pdf")

            cmd = [
                'unoconv',
                '-f', 'pdf',
                '-o', pdf_path,
                self._file_path
            ]

            result = subprocess.run(cmd,
                                    capture_output=True,
                                    text=True,
                                    timeout=60)

            if result.returncode != 0:
                logger.debug(f"unoconv 转换失败: {result.stderr}")
                return False

            # 检查 PDF 是否生成
            if not os.path.exists(pdf_path):
                logger.debug("PDF 文件未生成")
                return False

            # 将 PDF 转换为图片
            images = pdf2image.convert_from_path(pdf_path)

            # 保存每一页
            for i, image in enumerate(images, start=1):
                page_filename = f"page_{i}.png"
                page_path = os.path.join(self._pages_dir, page_filename)
                image.save(page_path, 'PNG')
                logger.debug(f"保存页面: {page_filename}")

            # 删除临时 PDF 文件
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            logger.info(f"使用 unoconv 转换成功，共 {len(images)} 页")
            return True

        except ImportError:
            logger.debug("pdf2image 未安装")
            return False
        except subprocess.TimeoutExpired:
            logger.debug("unoconv 转换超时")
            return False
        except Exception as e:
            logger.debug(f"unoconv 转换失败: {e}")
            return False


class MarkdownDocumentParser(DocumentParser):
    """Markdown文档解析器"""

    def __init__(self, work_dir: str, file_path: str):
        super().__init__(work_dir, file_path)

    def parse(self):
        """
        如果file_path不在work_dir里，则把file_path复制到work_dir里
        读取文档里的图片链接，如果是http开头的，下载到images目录里
        预览md,分页保存到pages里
        """
        try:
            logger.info(f"开始解析 Markdown 文档: {self._file_path}")

            # 1. 复制文件到work_dir（如果不在work_dir里）
            self._copy_file_to_workdir()

            # 2. 下载HTTP图片并更新链接
            self._download_and_update_images()

            # 3. 生成预览页面
            self._generate_preview_pages()

            logger.info(f"Markdown 文档解析完成: {self._file_path}")
            return True
        except Exception as e:
            logger.error(f"解析 Markdown 文档失败: {self._file_path}, 错误: {e}")
            return False

    def _copy_file_to_workdir(self):
        """
        如果file_path不在work_dir里，则把file_path复制到work_dir里
        """
        import shutil

        # 获取file_path的绝对路径
        abs_file_path = os.path.abspath(self._file_path)
        abs_work_dir = os.path.abspath(self._work_dir)

        # 检查文件是否在work_dir里
        if not abs_file_path.startswith(abs_work_dir):
            logger.info(f"文件不在work_dir里，复制文件: {abs_file_path} -> {self._md_file_path}")
            shutil.copy2(abs_file_path, self._md_file_path)
        else:
            # 如果文件已经在work_dir里，但文件名不是标准的md文件名，则复制
            if abs_file_path != os.path.abspath(self._md_file_path):
                logger.info(f"重命名文件: {abs_file_path} -> {self._md_file_path}")
                shutil.copy2(abs_file_path, self._md_file_path)
            else:
                logger.info(f"文件已在work_dir里: {abs_file_path}")

    def _download_and_update_images(self):
        """
        读取文档里的图片链接，如果是http开头的，下载到images目录里
        并更新Markdown中的图片链接
        """
        import re
        import urllib.request
        import urllib.parse
        from urllib.error import URLError, HTTPError

        logger.info(f"开始处理图片链接: {self._md_file_path}")

        # 读取Markdown文件
        with open(self._md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 匹配Markdown图片语法: ![alt](url)
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        matches = re.finditer(image_pattern, content)

        image_counter = 0
        updated_content = content

        for match in matches:
            alt_text = match.group(1)
            image_url = match.group(2)

            # 检查是否是HTTP/HTTPS链接
            if image_url.startswith('http://') or image_url.startswith('https://'):
                try:
                    image_counter += 1

                    # 获取文件扩展名
                    parsed_url = urllib.parse.urlparse(image_url)
                    url_path = parsed_url.path
                    ext = os.path.splitext(url_path)[1]
                    if not ext or ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']:
                        ext = '.png'  # 默认使用png

                    # 生成本地文件名
                    image_filename = f"image_{image_counter}{ext}"
                    image_path = os.path.join(self._images_dir, image_filename)

                    # 下载图片
                    logger.info(f"下载图片: {image_url} -> {image_filename}")

                    # 设置User-Agent避免被某些网站拒绝
                    req = urllib.request.Request(
                        image_url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )

                    with urllib.request.urlopen(req, timeout=30) as response:
                        image_data = response.read()
                        with open(image_path, 'wb') as f:
                            f.write(image_data)

                    logger.debug(f"图片下载成功: {image_filename}")

                    # 更新Markdown中的图片链接
                    old_image_ref = f"![{alt_text}]({image_url})"
                    new_image_ref = f"![{alt_text}](images/{image_filename})"
                    updated_content = updated_content.replace(old_image_ref, new_image_ref)

                except (URLError, HTTPError) as e:
                    logger.warning(f"下载图片失败: {image_url}, 错误: {e}")
                except Exception as e:
                    logger.warning(f"处理图片失败: {image_url}, 错误: {e}")

        # 保存更新后的Markdown文件
        if updated_content != content:
            with open(self._md_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            logger.info(f"已更新Markdown文件，共下载 {image_counter} 张图片")
        else:
            logger.info(f"没有需要下载的HTTP图片")

    def _generate_preview_pages(self):
        """
        预览md,分页保存到pages里
        使用markdown渲染库将Markdown转换为HTML，然后转换为图片
        """
        try:
            logger.info(f"开始生成预览页面: {self._md_file_path}")

            # 尝试使用不同的方法生成预览
            success = False

            # 方法1: 使用markdown2和imgkit
            success = self._generate_pages_with_imgkit()

            # 方法2: 使用playwright
            if not success:
                success = self._generate_pages_with_playwright()

            if not success:
                logger.warning(
                    "无法生成Markdown预览页面。请安装以下工具之一：\n"
                    "- pip install markdown2 imgkit (需要安装wkhtmltoimage)\n"
                    "- pip install playwright markdown2 (然后运行 playwright install)"
                )
                return False

            logger.info(f"预览页面生成完成")
            return True

        except Exception as e:
            logger.error(f"生成预览页面失败: {e}")
            return False

    def _generate_pages_with_imgkit(self) -> bool:
        """
        使用markdown2和imgkit生成预览页面

        Returns:
            bool: 是否生成成功
        """
        try:
            import markdown2
            import imgkit

            logger.info("尝试使用 imgkit 生成预览...")

            # 读取Markdown内容
            with open(self._md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 转换为HTML
            html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

            # 添加CSS样式
            html_with_style = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 20px;
                        line-height: 1.6;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # 生成图片
            page_path = os.path.join(self._pages_dir, "page_1.png")

            options = {
                'format': 'png',
                'encoding': 'UTF-8',
                'width': 800,
            }

            imgkit.from_string(html_with_style, page_path, options=options)

            logger.info(f"使用 imgkit 生成预览成功")
            return True

        except ImportError:
            logger.debug("markdown2 或 imgkit 未安装")
            return False
        except Exception as e:
            logger.debug(f"imgkit 生成预览失败: {e}")
            return False

    def _generate_pages_with_playwright(self) -> bool:
        """
        使用playwright生成预览页面

        Returns:
            bool: 是否生成成功
        """
        try:
            import markdown2
            from playwright.sync_api import sync_playwright

            logger.info("尝试使用 playwright 生成预览...")

            # 读取Markdown内容
            with open(self._md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 转换为HTML
            html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

            # 添加CSS样式
            html_with_style = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 20px;
                        line-height: 1.6;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # 使用playwright截图
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 800, 'height': 600})
                page.set_content(html_with_style)

                # 等待页面加载完成
                page.wait_for_load_state('networkidle')

                # 截图
                page_path = os.path.join(self._pages_dir, "page_1.png")
                page.screenshot(path=page_path, full_page=True)

                browser.close()

            logger.info(f"使用 playwright 生成预览成功")
            return True

        except ImportError:
            logger.debug("markdown2 或 playwright 未安装")
            return False
        except Exception as e:
            logger.debug(f"playwright 生成预览失败: {e}")
            return False


class PdfParser(DocumentParser):

    def __init__(self, work_dir: str, file_path: str):
        super().__init__(work_dir, file_path)

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("MINERU_API_KEY"),
        }
        self.uid = uuid.uuid4().hex

    def _get_pdf_page_count(self) -> int:
        """获取PDF文件的总页数"""
        try:
            with fitz.open(self._file_path) as doc:
                return doc.page_count
        except Exception as e:
            logger.error(f"获取PDF页数失败: {e}")
            # 如果无法获取页数，返回一个较大的值以触发分页处理
            return 100

    def _split_pdf_by_pages(self, start_page: int, end_page: int, output_path: str) -> bool:
        """按页数范围拆分PDF文件"""
        try:
            with fitz.open(self._file_path) as doc:
                # 确保页数范围有效
                total_pages = doc.page_count
                start_page = max(0, min(start_page, total_pages - 1))
                end_page = max(start_page, min(end_page, total_pages - 1))

                # 创建新的PDF文档
                new_doc = fitz.open()
                for page_num in range(start_page, end_page + 1):
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

                new_doc.save(output_path)
                new_doc.close()
                return True
        except Exception as e:
            logger.error(f"拆分PDF失败 (页码 {start_page}-{end_page}): {e}")
            return False

    def _call_mineru_api(self, file_url: str) -> str:
        """调用MinerU API处理单个PDF文件"""
        data = {
            "url": file_url,
            "model_version": "vlm"
        }

        response = requests.post(os.getenv("MINERU_BASE_URL"), headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Mineru API error: {response.text}")

        return response.json()['data']['task_id']

    def _wait_for_mineru_result(self, task_id: str) -> Optional[str]:
        """等待MinerU处理完成并返回结果URL"""
        start_time = time.time()

        while True:
            response = requests.get(os.getenv("MINERU_BASE_URL") + "/" + task_id, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Mineru API error: {response.text}")

            data = response.json()['data']
            logger.debug(f"MinerU task {task_id} status: {data}")

            if data.get('state') == 'done':
                return data.get('full_zip_url')

            if data.get('state') == 'failed':
                raise Exception(f"Mineru API error: {data['message']}")

            time.sleep(5)

            cost_time = time.time() - start_time
            if cost_time > 300:  # 5分钟超时
                raise Exception(f"Mineru API timeout")

    def _download_and_extract_mineru_result(self, full_zip_url: str, output_dir: str) -> Optional[str]:
        """下载并解压MinerU处理结果"""
        tmp_file_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.zip")
        try:
            download_utils.download_file(full_zip_url, tmp_file_path)
            logger.info(f"Downloaded MinerU result to: {tmp_file_path}")

            # 解压文件
            zipfile.ZipFile(tmp_file_path, 'r').extractall(output_dir)

            # 找到markdown文件
            md_files = [file for file in os.listdir(output_dir) if file.endswith(".md")]
            if md_files:
                return os.path.join(output_dir, md_files[0])
            else:
                logger.error("No markdown file found in MinerU result")
                return None

        except Exception as e:
            logger.error(f"下载或解压MinerU结果失败: {e}")
            return None
        finally:
            # 清理临时zip文件
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def _process_single_pdf_chunk(self, pdf_path: str, chunk_index: int) -> Optional[str]:
        """处理单个PDF分块，直接返回处理后的markdown内容"""
        try:
            # 上传到OSS
            _, _, file_url = oss_utils.upload_oss(pdf_path, dir_=f"mrag/{self.uid}/chunk_{chunk_index}",
                                                  is_delete=False)

            # 调用MinerU API
            task_id = self._call_mineru_api(file_url)

            # 等待结果
            full_zip_url = self._wait_for_mineru_result(task_id)
            if not full_zip_url:
                return None

            # 创建临时目录存储结果
            chunk_output_dir = os.path.join(tempfile.gettempdir(), f"mineru_chunk_{chunk_index}_{uuid.uuid4().hex}")
            os.makedirs(chunk_output_dir, exist_ok=True)

            try:
                # 下载并解压MinerU结果
                tmp_file_path = os.path.join(chunk_output_dir, f"chunk_{chunk_index}_result.zip")
                download_utils.download_file(full_zip_url, tmp_file_path)

                # 解压zip文件
                zipfile.ZipFile(tmp_file_path, 'r').extractall(chunk_output_dir)

                # 找到markdown文件
                md_files = [file for file in os.listdir(chunk_output_dir) if file.endswith(".md")]
                if not md_files:
                    logger.error(f"分块 {chunk_index} 未找到markdown文件")
                    return None

                md_file = md_files[0]
                md_file_path = os.path.join(chunk_output_dir, md_file)

                # 读取markdown内容
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 处理图片 - 将图片复制到主images目录
                chunk_images_dir = os.path.join(chunk_output_dir, "images")
                if os.path.exists(chunk_images_dir):
                    # 为分块创建子目录，避免图片名冲突
                    chunk_images_subdir = os.path.join(self._images_dir, f"chunk_{chunk_index}")
                    os.makedirs(chunk_images_subdir, exist_ok=True)

                    # 复制所有图片到分块子目录
                    for image_file in os.listdir(chunk_images_dir):
                        src_path = os.path.join(chunk_images_dir, image_file)
                        dst_path = os.path.join(chunk_images_subdir, image_file)
                        if os.path.isfile(src_path):
                            shutil.copy2(src_path, dst_path)
                            logger.info(f"复制分块 {chunk_index} 图片: {image_file}")

                    # 更新markdown内容中的图片路径
                    content = content.replace("](images/", f"](images/chunk_{chunk_index}/")

                logger.info(f"分块 {chunk_index} 处理完成")
                return content

            finally:
                # 清理临时目录
                if os.path.exists(chunk_output_dir):
                    shutil.rmtree(chunk_output_dir, ignore_errors=True)

        except Exception as e:
            logger.error(f"处理PDF分块 {chunk_index} 失败: {e}")
            return None

    def mineru_parse(self):
        """优化的MinerU解析方法，支持智能分页处理"""
        try:
            # 获取PDF页数
            total_pages = self._get_pdf_page_count()
            logger.info(f"PDF文件总页数: {total_pages}")

            # 配置参数
            SMALL_PDF_THRESHOLD = int(os.getenv("SMALL_PDF_PAGE_THRESHOLD", "10"))
            CHUNK_SIZE = int(os.getenv("PDF_CHUNK_SIZE", "4"))

            all_content = []

            if total_pages <= SMALL_PDF_THRESHOLD:
                # 小PDF文件，直接处理
                logger.info(f"PDF页数 {total_pages} 小于阈值 {SMALL_PDF_THRESHOLD}，直接处理整个文件")

                # 上传整个文件
                _, _, file_url = oss_utils.upload_oss(self._file_path, dir_=f"mrag/{self.uid}", is_delete=False)

                # 调用MinerU API
                task_id = self._call_mineru_api(file_url)

                # 等待结果
                full_zip_url = self._wait_for_mineru_result(task_id)
                if full_zip_url:
                    # 创建临时目录
                    tmpdir = tempfile.gettempdir()
                    tmp_file_path = os.path.join(tmpdir, f"{self._filename}.zip")

                    # 下载结果
                    download_utils.download_file(full_zip_url, tmp_file_path)
                    logger.info(f"Downloaded result to: {tmp_file_path}")

                    # 解压
                    tmp_empty_dir = os.path.join(tmpdir, f"tmp_empty_dir_{uuid.uuid4().hex}")
                    os.makedirs(tmp_empty_dir, exist_ok=True)
                    zipfile.ZipFile(tmp_file_path, 'r').extractall(tmp_empty_dir)

                    # 处理markdown文件
                    md_files = [file for file in os.listdir(tmp_empty_dir) if file.endswith(".md")]
                    if md_files:
                        md_file = md_files[0]
                        logger.info(f"Found markdown file: {md_file}")

                        # 移动markdown文件
                        shutil.move(os.path.join(tmp_empty_dir, md_file), self._md_file_path)

                        # 处理图片目录
                        image_dir = os.path.dirname(self._images_dir)
                        if os.path.exists(self._images_dir):
                            shutil.rmtree(self._images_dir)
                        mineru_images_dir = os.path.join(tmp_empty_dir, "images")
                        if os.path.exists(mineru_images_dir):
                            shutil.move(mineru_images_dir, image_dir)

                        logger.info("整个PDF文件处理完成")
                        return
                    else:
                        logger.error("No markdown file found in result")
                        raise Exception("MinerU processing failed: no markdown file generated")
                else:
                    raise Exception("MinerU processing failed: no result URL")

            else:
                # 大PDF文件，分页处理
                logger.info(f"PDF页数 {total_pages} 超过阈值 {SMALL_PDF_THRESHOLD}，将按每 {CHUNK_SIZE} 页进行分页处理")

                # 创建临时目录存储分块文件
                temp_chunks_dir = os.path.join(tempfile.gettempdir(), f"pdf_chunks_{self.uid}")
                os.makedirs(temp_chunks_dir, exist_ok=True)

                try:
                    # 分页处理
                    chunk_index = 0
                    for start_page in range(0, total_pages, CHUNK_SIZE):
                        end_page = min(start_page + CHUNK_SIZE - 1, total_pages - 1)

                        logger.info(f"处理分块 {chunk_index}: 页码 {start_page + 1}-{end_page + 1}")

                        # 创建分块PDF文件
                        chunk_pdf_path = os.path.join(temp_chunks_dir, f"chunk_{chunk_index}.pdf")

                        if self._split_pdf_by_pages(start_page, end_page, chunk_pdf_path):
                            # 处理分块
                            chunk_content = self._process_single_pdf_chunk(chunk_pdf_path, chunk_index)

                            if chunk_content:
                                # 添加页码标记
                                all_content.append(
                                    f"\n<!-- Chunk {chunk_index}: Pages {start_page + 1}-{end_page + 1} -->\n")
                                all_content.append(chunk_content)
                                logger.info(f"分块 {chunk_index} 处理完成")
                            else:
                                logger.warning(f"分块 {chunk_index} 处理失败，将使用备用方案")
                                # 对该分块使用直接提取方法
                                try:
                                    with fitz.open(chunk_pdf_path) as chunk_doc:
                                        chunk_text = ""
                                        for page in chunk_doc:
                                            chunk_text += page.get_text()
                                        if chunk_text:
                                            all_content.append(
                                                f"\n<!-- Chunk {chunk_index}: Pages {start_page + 1}-{end_page + 1} -->\n")
                                            all_content.append(chunk_text)
                                except Exception as e:
                                    logger.error(f"分块 {chunk_index} 备用方案也失败: {e}")

                        chunk_index += 1

                    # 合并所有内容
                    if all_content:
                        final_content = "\n".join(all_content)
                        with open(self._md_file_path, "w", encoding="utf-8") as f:
                            f.write(final_content)
                        logger.info(f"PDF分页处理完成，共处理 {chunk_index} 个分块")
                    else:
                        raise Exception("所有分块处理都失败")

                finally:
                    # 清理临时分块文件
                    if os.path.exists(temp_chunks_dir):
                        shutil.rmtree(temp_chunks_dir, ignore_errors=True)

        except Exception as e:
            logger.error(f"MinerU分页处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _extract_pdf_directly(self):
        """直接读取PDF内容，不通过外部服务转换"""
        logger.info(f"直接读取PDF文件: {self._file_path}")
        content = ""

        try:
            doc = fitz.open(self._file_path)
            for page in doc:
                text = page.get_text()
                content += text

                images = page.get_images()
                for img in images:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]
                    image_ext = base_image["ext"]
                    # 保存图片到本地
                    image_path = os.path.join(self._images_dir, f"image_{xref}.{image_ext}")
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
        except Exception as e:
            logger.error(f"直接读取PDF文件失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

        try:
            with pdfplumber.open(self._file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            row = [str(cell) if cell is not None else "" for cell in row]
                            content += " | ".join(row) + "\n"

        except Exception as e:
            logger.error(f"提取PDF表格失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

        if content:
            with open(self._md_file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def parse(self):
        """优化的PDF解析方法，支持智能切分调度"""
        try:
            logger.info(f"开始解析PDF文档: {self._file_path}")

            # 使用新的智能切分逻辑
            self.mineru_parse()

            logger.info(f"PDF文档解析完成: {self._file_path}")

        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"MinerU 解析 pdf 文档失败: {self._file_path}, 错误: {e}")

            # 如果MinerU处理失败，使用备用方案
            logger.info("尝试使用备用方案直接提取PDF内容")
            self._extract_pdf_directly()

        try:
            # 生成页面预览图片
            logger.info("开始生成PDF页面预览图片")
            import pdf2image
            images = pdf2image.convert_from_path(self._file_path)

            # 保存每一页
            for i, image in enumerate(images, start=1):
                page_filename = f"page_{i}.png"
                page_path = os.path.join(self._pages_dir, page_filename)
                image.save(page_path, 'PNG')
                logger.debug(f"保存页面: {page_filename}")

            logger.info(f"PDF页面预览生成完成，共 {len(images)} 页")

        except Exception as e:
            logger.error(f"生成PDF页面预览失败: {e}")
            # 页面预览失败不影响主流程


class ImageParser(DocumentParser):
    def __init__(self, work_dir: str, file_path: str):
        super().__init__(work_dir, file_path)

    def parse(self):
        with open(self._md_file_path, "w", encoding="utf-8") as f:
            f.write("")

        shutil.copy(self._file_path, self._pages_dir)


def get_document_parser(file_extension: str):
    if file_extension == ".docx":
        return DocxDocumentParser
    elif file_extension == ".md":
        return MarkdownDocumentParser
    elif file_extension == ".pdf":
        return PdfParser
    elif file_extension in {".png", ".jpg", ".jpeg"}:
        return ImageParser
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

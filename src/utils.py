"""
心理测试反馈报告生成器 - 工具函数模块
包含各种辅助功能和工具函数
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import tkinter as tk
from tkinter import messagebox

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """设置日志系统"""
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 创建日志文件名（包含日期）
    log_file = log_path / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def validate_excel_file(file_path: str) -> Tuple[bool, str]:
    """验证Excel文件是否有效"""
    if not file_path:
        return False, "请选择Excel文件"
    
    path = Path(file_path)
    if not path.exists():
        return False, "文件不存在"
    
    if not path.suffix.lower() in ['.xlsx', '.xls']:
        return False, "文件格式不正确，请选择Excel文件"
    
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        
        # 检查必要的列
        required_columns = ['姓名', '性别', '生日', '年龄', '测试日期', 'ID']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Excel文件缺少必要的列: {', '.join(missing_columns)}"
        
        if len(df) == 0:
            return False, "Excel文件没有数据行"
        
        return True, "文件验证通过"
        
    except Exception as e:
        return False, f"文件读取错误: {str(e)}"

def validate_image_directory(dir_path: str) -> Tuple[bool, str]:
    """验证图片目录是否有效（可选）"""
    if not dir_path or dir_path.strip() == "":
        return True, "未指定图片目录，将自动生成雷达图"
    
    path = Path(dir_path)
    if not path.exists():
        return False, "目录不存在"
    
    if not path.is_dir():
        return False, "路径不是一个目录"
    
    # 检查是否有图片文件
    image_files = list(path.glob("*.png")) + list(path.glob("*.jpg")) + list(path.glob("*.jpeg"))
    if not image_files:
        return False, "目录中没有找到图片文件（支持PNG、JPG格式）"
    
    return True, f"找到 {len(image_files)} 个图片文件"

def validate_output_directory(dir_path: str) -> Tuple[bool, str]:
    """验证输出目录是否有效"""
    if not dir_path:
        return False, "请选择输出目录"
    
    path = Path(dir_path)
    
    # 如果目录不存在，尝试创建
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"无法创建输出目录: {str(e)}"
    
    # 检查写入权限
    try:
        test_file = path / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        return True, "输出目录可用"
    except Exception as e:
        return False, f"输出目录没有写入权限: {str(e)}"

def show_error(title: str, message: str):
    """显示错误对话框"""
    messagebox.showerror(title, message)

def show_info(title: str, message: str):
    """显示信息对话框"""
    messagebox.showinfo(title, message)

def show_warning(title: str, message: str):
    """显示警告对话框"""
    messagebox.showwarning(title, message)

def ask_yes_no(title: str, message: str) -> bool:
    """显示是否确认对话框"""
    return messagebox.askyesno(title, message)

def center_window(window: tk.Tk, width: int, height: int):
    """将窗口居中显示"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def get_resource_path(relative_path: str) -> str:
    """获取资源文件路径（支持打包后的exe）"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def safe_filename(filename: str) -> str:
    """生成安全的文件名（移除非法字符）"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

class ProgressCallback:
    """进度回调类"""
    
    def __init__(self, callback_func=None):
        self.callback_func = callback_func
        self.total = 0
        self.current = 0
    
    def set_total(self, total: int):
        """设置总数"""
        self.total = total
        self.current = 0
    
    def update(self, message: str = ""):
        """更新进度"""
        self.current += 1
        if self.callback_func:
            progress = (self.current / self.total * 100) if self.total > 0 else 0
            self.callback_func(progress, message)
    
    def finish(self, message: str = "完成"):
        """完成进度"""
        if self.callback_func:
            self.callback_func(100, message)
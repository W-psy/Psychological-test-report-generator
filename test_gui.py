#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的GUI测试脚本
用于验证新增的自定义PDF文件名功能
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui():
    """测试GUI功能"""
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("GUI测试 - v1.0.2")
        root.geometry("600x400")
        
        # 创建标签
        label = ttk.Label(root, text="GUI测试成功！版本 1.0.2", font=("Arial", 16))
        label.pack(pady=20)
        
        # 测试文件命名变量
        filename_mode_var = tk.StringVar(value="name_custom")
        filename_separator_var = tk.StringVar(value="心理测评")
        
        # 创建文件命名测试框架
        frame = ttk.LabelFrame(root, text="文件命名测试", padding="10")
        frame.pack(pady=20, padx=20, fill="x")
        
        # 命名模式选择
        ttk.Radiobutton(frame, text="使用ID号", variable=filename_mode_var, 
                       value="id_only").pack(anchor="w", pady=2)
        ttk.Radiobutton(frame, text="姓名+自定义内容+报告", variable=filename_mode_var, 
                       value="name_custom").pack(anchor="w", pady=2)
        
        # 自定义内容输入
        custom_frame = ttk.Frame(frame)
        custom_frame.pack(fill="x", pady=5)
        ttk.Label(custom_frame, text="自定义内容:").pack(side="left")
        ttk.Entry(custom_frame, textvariable=filename_separator_var, width=20).pack(side="left", padx=5)
        
        # 测试按钮
        def show_values():
            mode = filename_mode_var.get()
            separator = filename_separator_var.get()
            result_label.config(text=f"模式: {mode}, 分隔符: {separator}")
        
        ttk.Button(frame, text="测试设置", command=show_values).pack(pady=10)
        
        # 结果显示
        result_label = ttk.Label(frame, text="点击测试按钮查看设置")
        result_label.pack(pady=5)
        
        # 版本信息
        version_label = ttk.Label(root, text="v1.0.2 - 新增自定义PDF文件名功能")
        version_label.pack(side="bottom", pady=10)
        
        print("GUI测试窗口已创建，版本 1.0.2")
        print("新功能：自定义PDF文件名")
        print("- 模式1：仅使用ID号")
        print("- 模式2：姓名+自定义内容+报告")
        
        # 运行GUI
        root.mainloop()
        
    except Exception as e:
        print(f"GUI测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui()
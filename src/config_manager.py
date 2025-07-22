"""
心理测试反馈报告生成器 - 配置管理模块
支持自定义评分配置和评价规则的管理
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器 - 管理评分配置和评价规则"""
    
    def __init__(self):
        self.task_config = self._get_default_task_config()
        # 默认使用空的评价规则字典，不预置变量
        self.evaluation_dict = {}
        self.config_file_path = None
        
    def _get_default_task_config(self) -> Dict:
        """获取默认任务配置 - 空配置，等待用户导入"""
        return {
            "常规任务": [],
            "特殊任务": []
        }
    
    def _get_default_evaluation_dict(self) -> Dict:
        """获取默认评价规则字典 - 空字典，等待用户导入配置"""
        return {}
    
    def load_config_from_excel(self, file_path: str) -> bool:
        """
        从Excel文件加载配置
        
        Excel文件格式要求：
        - 第一列：测评项目名称
        - 第二列开始：阈值列（可以有多个，支持2-7档）
        - 最后几列：对应档次的评价说明
        
        支持的分档模式：
        - 2档：阈值1 | 低分说明 | 高分说明
        - 3档：阈值1 | 阈值2 | 低分说明 | 中等分说明 | 高分说明
        - 4档：阈值1 | 阈值2 | 阈值3 | 很低说明 | 低分说明 | 中等分说明 | 高分说明
        - 5档：阈值1 | 阈值2 | 阈值3 | 阈值4 | 很低说明 | 低分说明 | 中等分说明 | 高分说明 | 很高说明
        - 6档：阈值1 | 阈值2 | 阈值3 | 阈值4 | 阈值5 | 极低说明 | 低分说明 | 中低说明 | 中高说明 | 高分说明 | 极高说明
        - 7档：阈值1 | 阈值2 | 阈值3 | 阈值4 | 阈值5 | 阈值6 | 极低说明 | 低分说明 | 中低说明 | 中等说明 | 中高说明 | 高分说明 | 极高说明
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            是否加载成功
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 验证最少列数
            if len(df.columns) < 4:
                raise ValueError("Excel文件列数不足，最少需要4列：测评项目、阈值、低分说明、高分说明")
            
            # 自动检测分档模式
            first_row = df.iloc[0]
            col_count = len(df.columns)
            
            # 分析列结构，确定分档数量
            if col_count == 4:  # 2档模式
                level_count = 2
                threshold_count = 1
                df.columns = ['测评项目', '阈值1', '低分说明', '高分说明']
                level_names = ['low', 'high']
                level_labels = ['低分说明', '高分说明']
            elif col_count == 6:  # 3档模式（原有格式）
                level_count = 3
                threshold_count = 2
                df.columns = ['测评项目', '阈值1', '阈值2', '低分说明', '中等分说明', '高分说明']
                level_names = ['low', 'mid', 'high']
                level_labels = ['低分说明', '中等分说明', '高分说明']
            elif col_count == 8:  # 4档模式
                level_count = 4
                threshold_count = 3
                df.columns = ['测评项目', '阈值1', '阈值2', '阈值3', '很低说明', '低分说明', '中等分说明', '高分说明']
                level_names = ['very_low', 'low', 'mid', 'high']
                level_labels = ['很低说明', '低分说明', '中等分说明', '高分说明']
            elif col_count == 10:  # 5档模式
                level_count = 5
                threshold_count = 4
                df.columns = ['测评项目', '阈值1', '阈值2', '阈值3', '阈值4', '很低说明', '低分说明', '中等分说明', '高分说明', '很高说明']
                level_names = ['very_low', 'low', 'mid', 'high', 'very_high']
                level_labels = ['很低说明', '低分说明', '中等分说明', '高分说明', '很高说明']
            elif col_count == 12:  # 6档模式
                level_count = 6
                threshold_count = 5
                df.columns = ['测评项目', '阈值1', '阈值2', '阈值3', '阈值4', '阈值5', '极低说明', '低分说明', '中低说明', '中高说明', '高分说明', '极高说明']
                level_names = ['extremely_low', 'low', 'mid_low', 'mid_high', 'high', 'extremely_high']
                level_labels = ['极低说明', '低分说明', '中低说明', '中高说明', '高分说明', '极高说明']
            elif col_count == 14:  # 7档模式
                level_count = 7
                threshold_count = 6
                df.columns = ['测评项目', '阈值1', '阈值2', '阈值3', '阈值4', '阈值5', '阈值6', '极低说明', '低分说明', '中低说明', '中等说明', '中高说明', '高分说明', '极高说明']
                level_names = ['extremely_low', 'low', 'mid_low', 'mid', 'mid_high', 'high', 'extremely_high']
                level_labels = ['极低说明', '低分说明', '中低说明', '中等说明', '中高说明', '高分说明', '极高说明']
            else:
                raise ValueError(f"不支持的列数：{col_count}。支持的格式：4列(2档)、6列(3档)、8列(4档)、10列(5档)、12列(6档)、14列(7档)")
            
            # 验证数据
            for idx, row in df.iterrows():
                if pd.isna(row['测评项目']):
                    continue
                    
                # 验证阈值
                thresholds = []
                for i in range(1, threshold_count + 1):
                    try:
                        threshold = float(row[f'阈值{i}'])
                        thresholds.append(threshold)
                    except (ValueError, TypeError):
                        raise ValueError(f"第{idx+2}行：阈值{i}必须是有效数字")
                
                # 验证阈值递增
                for i in range(len(thresholds) - 1):
                    if thresholds[i] >= thresholds[i + 1]:
                        raise ValueError(f"第{idx+2}行：阈值必须递增排列")
                
                # 验证说明文本
                for label in level_labels:
                    if pd.isna(row[label]) or str(row[label]).strip() == '':
                        raise ValueError(f"第{idx+2}行：{label}不能为空")
            
            # 构建新的配置
            new_evaluation_dict = {}
            task_items = []
            
            for idx, row in df.iterrows():
                if pd.isna(row['测评项目']):
                    continue
                    
                item_name = str(row['测评项目']).strip()
                task_items.append(item_name)
                
                # 构建阈值列表
                thresholds = []
                for i in range(1, threshold_count + 1):
                    thresholds.append(float(row[f'阈值{i}']))
                
                # 构建等级说明字典
                levels = {}
                for i, (level_name, level_label) in enumerate(zip(level_names, level_labels)):
                    levels[level_name] = str(row[level_label]).strip()
                
                new_evaluation_dict[item_name] = {
                    "thresholds": thresholds,
                    "levels": levels,
                    "level_count": level_count,
                    "level_names": level_names
                }
            
            # 更新配置
            self.evaluation_dict = new_evaluation_dict
            self.task_config = {
                "常规任务": task_items,
                "特殊任务": []
            }
            self.config_file_path = file_path
            
            logger.info(f"成功从Excel文件加载配置：{file_path}")
            logger.info(f"加载了{len(task_items)}个测评项目，使用{level_count}档评价模式")
            
            return True
            
        except Exception as e:
            logger.error(f"加载Excel配置文件失败：{str(e)}")
            raise
    
    def save_config_to_json(self, file_path: str) -> bool:
        """
        保存配置到JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            是否保存成功
        """
        try:
            config_data = {
                "task_config": self.task_config,
                "evaluation_dict": self.evaluation_dict,
                "source_file": self.config_file_path
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已保存到：{file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败：{str(e)}")
            return False
    
    def load_config_from_json(self, file_path: str) -> bool:
        """
        从JSON文件加载配置
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.task_config = config_data.get("task_config", self._get_default_task_config())
            self.evaluation_dict = config_data.get("evaluation_dict", self._get_default_evaluation_dict())
            self.config_file_path = config_data.get("source_file")
            
            logger.info(f"成功从JSON文件加载配置：{file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载JSON配置文件失败：{str(e)}")
            return False
    
    def get_task_config(self) -> Dict:
        """获取任务配置"""
        return self.task_config.copy()
    
    def get_evaluation_dict(self) -> Dict:
        """获取评价规则字典"""
        return self.evaluation_dict.copy()
    
    def get_all_variables(self) -> List[str]:
        """获取所有变量列表"""
        return self.task_config["常规任务"] + self.task_config["特殊任务"]
    
    def reset_to_default(self):
        """重置为空配置"""
        self.task_config = self._get_default_task_config()
        # 重置为空的评价规则字典，不预置变量
        self.evaluation_dict = {}
        self.config_file_path = None
        logger.info("配置已重置为空配置")
    
    def export_template_excel(self, file_path: str) -> bool:
        """
        导出配置模板Excel文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 创建模板数据
            template_data = []
            for item_name, config in self.evaluation_dict.items():
                # 构建基础行数据
                row_data = {
                    '测评项目': item_name,
                }
                
                # 添加阈值
                thresholds = config['thresholds']
                for i, threshold in enumerate(thresholds):
                    row_data[f'阈值{i+1}'] = threshold
                
                # 添加级别说明
                levels = config['levels']
                if 'level_names' in config:
                    # 使用level_names顺序
                    level_names = config['level_names']
                    for i, level_name in enumerate(level_names):
                        if level_name in levels:
                            row_data[f'级别{i+1}说明'] = levels[level_name]
                else:
                    # 使用默认顺序（兼容旧格式）
                    level_order = ['low', 'mid', 'high']
                    for i, level_key in enumerate(level_order):
                        if level_key in levels:
                            row_data[f'级别{i+1}说明'] = levels[level_key]
                
                template_data.append(row_data)
            
            # 创建DataFrame并保存
            df = pd.DataFrame(template_data)
            df.to_excel(file_path, index=False)
            
            logger.info(f"配置模板已导出到：{file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置模板失败：{str(e)}")
            return False


class ConfigDialog:
    """配置对话框 - 用于管理评分配置的GUI界面"""
    
    def __init__(self, parent, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.result = None
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("评分配置管理")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_dialog()
        
        # 创建界面
        self.create_widgets()
        
        # 加载当前配置
        self.load_current_config()
    
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
    
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="评分配置管理", 
                               font=("Microsoft YaHei", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="从Excel加载配置", 
                  command=self.load_from_excel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导出配置模板", 
                  command=self.export_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置为默认", 
                  command=self.reset_to_default).pack(side=tk.LEFT, padx=5)
        
        # 配置显示区域
        config_frame = ttk.LabelFrame(main_frame, text="当前配置", padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建树形视图容器
        tree_frame = ttk.Frame(config_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始创建树形视图（将在load_current_config中重建）
        self.tree = None
        self.scrollbar = None
        
        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="确定", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(bottom_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
        # 保存树形视图容器的引用
        self.tree_frame = tree_frame
    
    def load_current_config(self):
        """加载当前配置到树形视图"""
        # 销毁现有的树形视图
        if self.tree:
            self.tree.destroy()
        if self.scrollbar:
            self.scrollbar.destroy()
        
        # 分析配置结构，确定列数
        evaluation_dict = self.config_manager.get_evaluation_dict()
        if not evaluation_dict:
            # 如果配置为空，创建一个简单的提示视图
            self.tree = ttk.Treeview(self.tree_frame, columns=['提示'], show='headings', height=15)
            self.tree.heading('提示', text='当前配置状态')
            self.tree.column('提示', width=600)
            
            # 添加滚动条
            self.scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=self.scrollbar.set)
            
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 插入提示信息
            self.tree.insert('', tk.END, values=['当前无评分配置，请从Excel文件加载配置'])
            return
        
        # 获取第一个配置项来确定结构
        first_config = next(iter(evaluation_dict.values()))
        level_count = first_config.get('level_count', 3)
        level_names = first_config.get('level_names', ['low', 'mid', 'high'])
        
        # 构建动态列结构
        columns = ['项目']
        
        # 添加阈值列
        threshold_count = len(first_config['thresholds'])
        for i in range(threshold_count):
            columns.append(f'阈值{i+1}')
        
        # 添加级别说明列
        level_labels = {
            'extremely_low': '极低说明',
            'very_low': '很低说明',
            'low': '低分说明', 
            'mid': '中等分说明',
            'high': '高分说明',
            'very_high': '很高说明',
            'extremely_high': '极高说明'
        }
        
        for level_name in level_names:
            label = level_labels.get(level_name, f'{level_name}说明')
            columns.append(label)
        
        # 创建新的树形视图
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        for col in columns:
            self.tree.heading(col, text=col)
            if col == '项目':
                self.tree.column(col, width=100)
            elif '阈值' in col:
                self.tree.column(col, width=80)
            else:
                self.tree.column(col, width=150)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加配置项目
        for item_name, config in evaluation_dict.items():
            # 构建行数据
            row_values = [item_name]
            
            # 添加阈值
            for threshold in config['thresholds']:
                row_values.append(str(threshold))
            
            # 添加级别说明
            levels = config['levels']
            item_level_names = config.get('level_names', level_names)
            for level_name in item_level_names:
                if level_name in levels:
                    text = levels[level_name]
                    # 截断过长的文本
                    if len(text) > 50:
                        text = text[:50] + '...'
                    row_values.append(text)
                else:
                    row_values.append('-')
            
            self.tree.insert('', tk.END, values=row_values)
    
    def load_from_excel(self):
        """从Excel文件加载配置"""
        file_path = filedialog.askopenfilename(
            title="选择配置Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                self.config_manager.load_config_from_excel(file_path)
                self.load_current_config()
                messagebox.showinfo("成功", "配置已成功加载！")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败：{str(e)}")
    
    def export_template(self):
        """导出配置模板"""
        file_path = filedialog.asksaveasfilename(
            title="导出配置模板",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                self.config_manager.export_template_excel(file_path)
                messagebox.showinfo("成功", f"配置模板已导出到：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出模板失败：{str(e)}")
    
    def reset_to_default(self):
        """重置为默认配置"""
        if messagebox.askyesno("确认", "确定要重置为默认配置吗？这将丢失当前的自定义配置。"):
            self.config_manager.reset_to_default()
            self.load_current_config()
            messagebox.showinfo("成功", "配置已重置为默认值！")
    
    def ok_clicked(self):
        """确定按钮点击"""
        self.result = True
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = False
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
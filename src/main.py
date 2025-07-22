"""
心理测试反馈报告生成器 - GUI主程序
提供友好的图形界面用于批量生成心理测试反馈报告
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):
    # PyInstaller打包后的路径
    base_path = sys._MEIPASS
else:
    # 开发环境路径
    base_path = current_dir

sys.path.insert(0, base_path)
sys.path.insert(0, current_dir)

try:
    from config import app_config
    from utils import (
        setup_logging, validate_excel_file, validate_image_directory, 
        validate_output_directory, center_window, show_error, show_info,
        ask_yes_no, ProgressCallback
    )
    from report_generator import ReportGenerator
    from config_manager import ConfigManager, ConfigDialog
except ImportError as e:
    # 如果相对导入失败，尝试绝对导入
    try:
        import config
        app_config = config.app_config
        import utils
        setup_logging = utils.setup_logging
        validate_excel_file = utils.validate_excel_file
        validate_image_directory = utils.validate_image_directory
        validate_output_directory = utils.validate_output_directory
        center_window = utils.center_window
        show_error = utils.show_error
        show_info = utils.show_info
        ask_yes_no = utils.ask_yes_no
        ProgressCallback = utils.ProgressCallback
        import report_generator
        ReportGenerator = report_generator.ReportGenerator
        import config_manager
        ConfigManager = config_manager.ConfigManager
        ConfigDialog = config_manager.ConfigDialog
    except ImportError:
        print(f"模块导入失败: {e}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"Python路径: {sys.path}")
        raise


class ReportGeneratorGUI:
    """心理测试反馈报告生成器GUI主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        self.setup_logging()
        self.load_last_settings()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化报告生成器
        self.report_generator = ReportGenerator(
            task_config=self.config_manager.get_task_config(),
            evaluation_dict=self.config_manager.get_evaluation_dict(),
            report_title=self.report_title_var.get(),
            disclaimer=self.disclaimer_var.get()
        )
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title(app_config.get("app.title", "心理测试反馈报告生成器"))
        self.root.geometry(app_config.get("app.window_size", "1000x700"))
        
        # 设置窗口图标
        try:
            # 使用项目内的默认图标
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            self.logger.warning(f"设置窗口图标失败: {e}")
            pass
        
        # 居中显示
        center_window(self.root, 1000, 700)
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_variables(self):
        """设置变量"""
        self.data_file_var = tk.StringVar()
        self.image_dir_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="就绪")
        
        # 新增：报告标题设置
        self.report_title_var = tk.StringVar(value="心理测试反馈报告")
        
        # 新增：结果说明设置
        self.disclaimer_var = tk.StringVar(value="测试结果与受试者当时的状态有关，良好状态下的评估结果更可靠。")
        
        # 生成状态
        self.is_generating = False
        self.generation_thread = None
    
    def setup_widgets(self):
        """设置界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="心理测试反馈报告生成器", 
                               font=("Microsoft YaHei", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        self.create_file_selection_area(main_frame)
        
        # 操作按钮区域
        self.create_action_area(main_frame)
        
        # 进度显示区域
        self.create_progress_area(main_frame)
        
        # 日志显示区域
        self.create_log_area(main_frame)
        
        # 状态栏
        self.create_status_bar(main_frame)
    
    def create_file_selection_area(self, parent):
        """创建文件选择区域"""
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="文件设置", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Excel数据文件
        ttk.Label(file_frame, text="Excel数据文件:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.data_file_var, width=60).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=2)
        ttk.Button(file_frame, text="浏览", command=self.browse_data_file).grid(
            row=0, column=2, pady=2)
        
        # 图片目录（可选）
        ttk.Label(file_frame, text="雷达图目录（可选）:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.image_dir_var, width=60).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=2)
        ttk.Button(file_frame, text="浏览", command=self.browse_image_dir).grid(
            row=1, column=2, pady=2)
        
        # 输出目录
        ttk.Label(file_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(file_frame, textvariable=self.output_dir_var, width=60).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=2)
        ttk.Button(file_frame, text="浏览", command=self.browse_output_dir).grid(
            row=2, column=2, pady=2)
        
        # 报告设置框架
        settings_frame = ttk.LabelFrame(parent, text="报告设置", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # 报告标题
        ttk.Label(settings_frame, text="报告标题:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.report_title_var, width=60).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=2)
        
        # 结果说明
        ttk.Label(settings_frame, text="结果说明:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=2)
        disclaimer_text = tk.Text(settings_frame, height=3, width=60, wrap=tk.WORD)
        disclaimer_text.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=2)
        disclaimer_text.insert(tk.END, self.disclaimer_var.get())
        
        # 绑定文本框变化事件
        def on_disclaimer_change(event=None):
            self.disclaimer_var.set(disclaimer_text.get("1.0", tk.END).strip())
        
        disclaimer_text.bind('<KeyRelease>', on_disclaimer_change)
        disclaimer_text.bind('<FocusOut>', on_disclaimer_change)
    
    def create_action_area(self, parent):
        """创建操作按钮区域"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 配置管理按钮
        self.config_btn = ttk.Button(action_frame, text="评分配置", 
                                    command=self.open_config_dialog)
        self.config_btn.pack(side=tk.LEFT, padx=5)
        
        # 验证按钮
        self.validate_btn = ttk.Button(action_frame, text="验证设置", 
                                      command=self.validate_settings)
        self.validate_btn.pack(side=tk.LEFT, padx=5)
        
        # 生成报告按钮
        self.generate_btn = ttk.Button(action_frame, text="生成报告", 
                                      command=self.start_generation, 
                                      style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(action_frame, text="停止生成", 
                                  command=self.stop_generation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 打开输出目录按钮
        self.open_output_btn = ttk.Button(action_frame, text="打开输出目录", 
                                         command=self.open_output_directory)
        self.open_output_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空日志按钮
        self.clear_log_btn = ttk.Button(action_frame, text="清空日志", 
                                       command=self.clear_log)
        self.clear_log_btn.pack(side=tk.LEFT, padx=5)
    
    def create_progress_area(self, parent):
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(parent, text="生成进度", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # 进度标签
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1, padx=(10, 0), pady=2)
    
    def create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 配置主框架的行权重
        parent.rowconfigure(5, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        # 状态标签
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 版本信息
        version_label = ttk.Label(status_frame, text=f"v{app_config.get('app.version', '1.0.0')}")
        version_label.grid(row=0, column=1, sticky=tk.E)
    
    def setup_logging(self):
        """设置日志系统"""
        self.logger = setup_logging()
        
        # 创建GUI日志处理器
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        # 添加GUI处理器
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(gui_handler)
        
        # 记录启动信息
        self.logger.info("心理测试反馈报告生成器启动")
    
    def load_last_settings(self):
        """加载上次的设置 - 不加载路径，确保每次启动都是空路径"""
        # 不加载路径，确保每次启动时路径都是空的
        self.data_file_var.set("")
        self.image_dir_var.set("")
        self.output_dir_var.set("")
    
    def save_settings(self):
        """保存当前设置"""
        app_config.update_last_paths(
            data_file=self.data_file_var.get(),
            image_dir=self.image_dir_var.get(),
            output_dir=self.output_dir_var.get()
        )
    
    def browse_data_file(self):
        """浏览Excel数据文件"""
        filename = filedialog.askopenfilename(
            title="选择Excel数据文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if filename:
            self.data_file_var.set(filename)
            self.logger.info(f"选择数据文件: {filename}")
    
    def browse_image_dir(self):
        """浏览图片目录"""
        dirname = filedialog.askdirectory(title="选择雷达图目录")
        if dirname:
            self.image_dir_var.set(dirname)
            self.logger.info(f"选择图片目录: {dirname}")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir_var.set(dirname)
            self.logger.info(f"选择输出目录: {dirname}")
    
    def validate_settings(self):
        """验证设置"""
        self.logger.info("开始验证设置...")
        
        # 验证Excel文件
        is_valid, message = validate_excel_file(self.data_file_var.get())
        if not is_valid:
            show_error("Excel文件验证失败", message)
            self.logger.error(f"Excel文件验证失败: {message}")
            return False
        self.logger.info(f"Excel文件验证通过: {message}")
        
        # 验证图片目录（可选）
        image_dir = self.image_dir_var.get()
        if image_dir:  # 只有当用户提供了图片目录时才验证
            is_valid, message = validate_image_directory(image_dir)
            if not is_valid:
                show_error("图片目录验证失败", message)
                self.logger.error(f"图片目录验证失败: {message}")
                return False
            self.logger.info(f"图片目录验证通过: {message}")
        else:
            self.logger.info("未指定图片目录，将自动生成雷达图")
        
        # 验证输出目录
        is_valid, message = validate_output_directory(self.output_dir_var.get())
        if not is_valid:
            show_error("输出目录验证失败", message)
            self.logger.error(f"输出目录验证失败: {message}")
            return False
        self.logger.info(f"输出目录验证通过: {message}")
        
        show_info("验证成功", "所有设置验证通过，可以开始生成报告！")
        self.logger.info("所有设置验证通过")
        return True
    
    def start_generation(self):
        """开始生成报告"""
        if self.is_generating:
            return
        
        # 验证设置
        if not self.validate_settings():
            return
        
        # 确认生成
        if not ask_yes_no("确认生成", "确定要开始生成报告吗？"):
            return
        
        # 保存设置
        self.save_settings()
        
        # 更新界面状态
        self.is_generating = True
        self.generate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("正在生成报告...")
        
        # 重置进度
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        
        # 启动生成线程
        self.generation_thread = threading.Thread(target=self._generate_reports_thread)
        self.generation_thread.daemon = True
        self.generation_thread.start()
    
    def _generate_reports_thread(self):
        """生成报告的线程函数"""
        try:
            # 更新报告生成器的设置
            self.report_generator.report_title = self.report_title_var.get()
            self.report_generator.disclaimer = self.disclaimer_var.get()
            
            # 创建进度回调
            def progress_callback(progress, message):
                self.root.after(0, lambda: self._update_progress(progress, message))
            
            # 生成报告
            image_dir = self.image_dir_var.get() if self.image_dir_var.get() else None
            results = self.report_generator.generate_batch_reports(
                data_file=self.data_file_var.get(),
                image_dir=image_dir,
                output_dir=self.output_dir_var.get(),
                progress_callback=progress_callback
            )
            
            # 显示结果
            self.root.after(0, lambda: self._show_generation_results(results))
            
        except Exception as e:
            self.logger.error(f"生成过程中出现错误: {str(e)}")
            self.root.after(0, lambda: show_error("生成错误", f"生成过程中出现错误：{str(e)}"))
        finally:
            # 恢复界面状态
            self.root.after(0, self._reset_generation_state)
    
    def _update_progress(self, progress, message):
        """更新进度显示"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")
        self.status_var.set(message)
    
    def _show_generation_results(self, results):
        """显示生成结果"""
        total = results["total"]
        success = results["success"]
        failed = results["failed"]
        
        message = f"生成完成！\n\n"
        message += f"总计: {total} 个报告\n"
        message += f"成功: {success} 个\n"
        message += f"失败: {failed} 个\n"
        
        if results["errors"]:
            message += f"\n错误详情:\n"
            for error in results["errors"][:5]:  # 只显示前5个错误
                message += f"• {error}\n"
            if len(results["errors"]) > 5:
                message += f"... 还有 {len(results['errors']) - 5} 个错误"
        
        if failed == 0:
            show_info("生成成功", message)
        else:
            messagebox.showwarning("生成完成（有错误）", message)
        
        self.logger.info(f"批量生成完成: 成功{success}个，失败{failed}个")
    
    def _reset_generation_state(self):
        """重置生成状态"""
        self.is_generating = False
        self.generate_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("就绪")
    
    def stop_generation(self):
        """停止生成（注意：这只是界面状态，实际生成可能仍在继续）"""
        if ask_yes_no("确认停止", "确定要停止生成吗？\n注意：已开始的报告生成可能仍会继续。"):
            self.logger.info("用户请求停止生成")
            self._reset_generation_state()
    
    def open_output_directory(self):
        """打开输出目录"""
        output_dir = self.output_dir_var.get()
        if output_dir and os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            show_error("错误", "输出目录不存在或未设置")
    
    def open_config_dialog(self):
        """打开配置对话框"""
        dialog = ConfigDialog(self.root, self.config_manager)
        result = dialog.show()
        
        if result:
            # 配置已更新，重新初始化报告生成器
            self.report_generator = ReportGenerator(
                task_config=self.config_manager.get_task_config(),
                evaluation_dict=self.config_manager.get_evaluation_dict()
            )
            self.logger.info("评分配置已更新")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.logger.info("日志已清空")
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_generating:
            if not ask_yes_no("确认退出", "正在生成报告，确定要退出吗？"):
                return
        
        # 保存设置
        self.save_settings()
        
        # 关闭窗口
        self.root.destroy()
    
    def run(self):
        """运行GUI"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI运行错误: {str(e)}")
            show_error("程序错误", f"程序运行出现错误：{str(e)}")


def main():
    """主函数"""
    try:
        # 创建并运行GUI
        app = ReportGeneratorGUI()
        app.run()
    except Exception as e:
        # 如果GUI启动失败，显示错误信息
        import traceback
        error_msg = f"程序启动失败：{str(e)}\n\n详细错误信息：\n{traceback.format_exc()}"
        
        # 尝试显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("启动错误", error_msg)
        except:
            # 如果连对话框都无法显示，则打印到控制台
            print(error_msg)


if __name__ == "__main__":
    main()
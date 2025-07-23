"""
心理测试反馈报告生成器 - 核心报告生成模块
基于原有脚本重构，提供模块化的报告生成功能
"""

import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging
from typing import Dict, Any, Optional, Callable
import io

from utils import ProgressCallback
from radar_chart import RadarChartGenerator


class FontManager:
    """字体管理器 - 负责注册和管理中文字体"""
    
    def __init__(self):
        self.registered_fonts = {}
        self.default_font = None
    
    def register_chinese_fonts(self) -> str:
        """注册中文字体并返回默认字体名称"""
        # 字体配置
        font_configs = {
            "SimSun": [
                r'C:\Windows\Fonts\SimSun.ttc',
                'SimSun.ttc',
                '/System/Library/Fonts/STSong.ttf',
                '/usr/share/fonts/truetype/Simsun.ttf'
            ],
            "SimKai": [
                r'C:\Windows\Fonts\SIMKAI.TTF',
                'SIMKAI.TTF',
            ],
            "SimHei": [
                r'C:\Windows\Fonts\simhei.ttf',
                'simhei.ttf',
                '/System/Library/Fonts/STHeiti-Light.ttc',
                '/usr/share/fonts/truetype/simhei.ttf'
            ]
        }
        
        # 注册字体
        for font_name, paths in font_configs.items():
            for path in paths:
                try:
                    pdfmetrics.registerFont(TTFont(font_name, path))
                    self.registered_fonts[font_name] = path
                    logging.info(f"成功加载字体: {font_name} ({path})")
                    if self.default_font is None:
                        self.default_font = font_name
                    break
                except Exception as e:
                    logging.debug(f"字体加载失败: {font_name} ({path}) - {str(e)}")
                    continue
        
        return self.default_font or "SimSun"


class ReportStyleManager:
    """报告样式管理器"""
    
    def __init__(self, font_manager: FontManager):
        self.font_manager = font_manager
        self.styles = getSampleStyleSheet()
        self._register_custom_styles()
    
    def _register_custom_styles(self):
        """注册自定义样式"""
        # 主标题样式
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontName="SimHei",
            fontSize=26,
            leading=24,
            alignment=1,
            spaceAfter=30,
            spaceBefore=5,
            textColor=colors.black
        ))

        # 表格标题样式
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontName="SimHei",
            fontSize=12,
            leading=14,
            textColor=colors.white,
            alignment=1
        ))

        # 数据样式
        self.styles.add(ParagraphStyle(
            name='Data_Body',
            parent=self.styles['Normal'],
            fontName="SimHei",
            fontSize=10,
            leading=14,
            textColor=colors.black,
            alignment=TA_CENTER
        ))

        # 说明样式
        self.styles.add(ParagraphStyle(
            name='CN_Body',
            parent=self.styles['Normal'],
            fontName="SimSun",
            fontSize=10,
            leading=14,
            textColor=colors.black
        ))

        # 结果说明样式
        self.styles.add(ParagraphStyle(
            name='note_style',
            parent=self.styles['Normal'],
            fontName="SimKai",
            fontSize=11,
            leading=14,
            textColor=colors.black,
            alignment=TA_LEFT,
            wordWrap='CJK',  # 支持中文换行
            leftIndent=0,
            rightIndent=0,
            spaceAfter=0,
            spaceBefore=0
        ))


class ReportGenerator:
    """心理测试反馈报告生成器"""
    
    def __init__(self, task_config: Dict = None, evaluation_dict: Dict = None, 
                 report_title: str = "心理测试反馈报告", 
                 disclaimer: str = "测试结果与受试者当时的状态有关，良好状态下的评估结果更可靠。"):
        """
        初始化报告生成器
        
        Args:
            task_config: 任务配置字典
            evaluation_dict: 评价规则字典
            report_title: 报告标题
            disclaimer: 结果说明
        """
        self.font_manager = FontManager()
        self.font_manager.register_chinese_fonts()
        self.style_manager = ReportStyleManager(self.font_manager)
        
        # 初始化雷达图生成器
        self.radar_generator = RadarChartGenerator()
        
        # 设置默认配置
        self.task_config = task_config or self._get_default_task_config()
        self.evaluation_dict = evaluation_dict or self._get_default_evaluation_dict()
        self.report_title = report_title  # 添加可自定义的报告标题
        self.disclaimer = disclaimer  # 添加可自定义的结果说明
        
        # 更新雷达图生成器的变量列表
        all_variables = self.task_config["常规任务"] + self.task_config["特殊任务"]
        self.radar_generator.set_variables(all_variables)
        
        self.logger = logging.getLogger(__name__)
    
    def _get_default_task_config(self) -> Dict:
        """获取默认任务配置"""
        return {
            "常规任务": [],
            "特殊任务": []
        }
    
    def _get_default_evaluation_dict(self) -> Dict:
        """获取默认评价规则字典"""
        return {}
    
    def _calculate_age(self, birth_date) -> str:
        """计算年龄"""
        try:
            date_str = str(int(birth_date))
            birth = datetime.strptime(date_str, "%Y%m%d")
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return str(age)
        except Exception as e:
            self.logger.warning(f"日期解析错误: {birth_date} - {str(e)}")
            return "N/A"
    
    def _get_evaluation(self, task: str, score: float) -> str:
        """获取评价内容 - 支持灵活分档"""
        if pd.isna(score):
            return "-"

        if task in self.task_config["常规任务"] + self.task_config["特殊任务"]:
            # 获取该项目的配置
            if task in self.evaluation_dict:
                config = self.evaluation_dict[task]
                thresholds = config["thresholds"]
                levels = config["levels"]
                level_names = config.get("level_names", ["low", "mid", "high"])
                
                # 根据分数确定等级
                level_index = 0
                for threshold in thresholds:
                    if score > threshold:
                        level_index += 1
                    else:
                        break
                
                # 确保索引不超出范围
                if level_index >= len(level_names):
                    level_index = len(level_names) - 1
                
                level_key = level_names[level_index]
                return levels.get(level_key, "-")
            else:
                # 向后兼容：使用旧的固定三档逻辑
                if score <= 85:
                    level = "low"
                elif 86 <= score <= 115:
                    level = "mid"
                else:
                    level = "high"
                
                # 如果有配置则使用配置，否则返回默认值
                if task in self.evaluation_dict:
                    return self.evaluation_dict[task]["levels"].get(level, "-")
        
        return "-"
    
    def _build_header(self, row: pd.Series, image_dir: Path = None) -> Table:
        """构建报告头部 - 规范化个人信息表格"""
        
        # 规范化个人信息字段，按指定顺序：姓名、ID编号、出生日期、年龄、测试日期、结果说明
        def get_field_value(field_name, default="-"):
            """获取字段值，如果不存在或为空则返回默认值"""
            if field_name in row and pd.notna(row[field_name]) and str(row[field_name]).strip():
                return str(row[field_name]).strip()
            return default
        
        # 格式化年龄 - 直接取Excel字符串并保留两位小数
        age_value = get_field_value('年龄')
        if age_value != "-":
            try:
                age_float = float(age_value)
                age_value = f"{age_float:.2f}岁"  # 保留两位小数
            except (ValueError, TypeError):
                age_value = f"{age_value}岁" if not age_value.endswith('岁') else age_value

        # 创建个人信息表格 - 按规定顺序
        info_data = [
            ["姓　　名", get_field_value('姓名')],
            ["ID  编号", get_field_value('ID')],
            ["出生日期", get_field_value('生日')],
            ["年　　龄", age_value],
            ["测试日期", get_field_value('测试日期')],
            ["结果说明", get_field_value('结果说明', self.disclaimer)]
        ]
        
        # 处理结果说明的格式
        special_note = info_data[-1][1]
        if len(special_note) > 20:  # 如果结果说明较长，使用段落格式（降低阈值确保换行）
            info_data[-1][1] = Paragraph(special_note, self.style_manager.styles['note_style'])
              
        row_heights = [1.2 * cm] * 5 + [2.0 * cm]  # 结果说明行高度为2.0cm，总高度为8cm匹配雷达图
        
        info_table = Table(
            info_data,
            colWidths=[2 * cm, 7 * cm],
            rowHeights=row_heights,
            style=TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'SimKai'),
                ('FONTSIZE', (0, 0), (-1, -1), 13),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D3DFEE')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有单元格垂直居中
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),   # 所有单元格水平居中
                ('ALIGN', (0, -1), (0, -1), 'CENTER'),   # 结果说明标签也居中
                ('ALIGN', (1, -1), (1, -1), 'LEFT'),     # 结果说明内容左对齐
                ('LEADING', (0, 0), (-1, -1), 18),       # 行间距
            ])
        )

        # 生成雷达图
        try:
            # 首先尝试生成雷达图
            image_bytes = self.radar_generator.generate_radar_chart(row)
            if image_bytes:
                # 从字节数据创建Image对象
                img = Image(io.BytesIO(image_bytes), width=8 * cm, height=8 * cm)
                self.logger.info(f"成功生成雷达图: {row.get('ID', 'Unknown')}")
            else:
                raise ValueError("雷达图生成返回空数据")
        except Exception as e:
            self.logger.warning(f"雷达图生成失败: {row.get('ID', 'Unknown')} - {str(e)}")
            # 如果生成失败，尝试从文件加载（向后兼容）
            if image_dir:
                img_path = Path(image_dir) / f"{row.get('ID', 'unknown')}.png"
                try:
                    img = Image(str(img_path.resolve()), width=8 * cm, height=8 * cm)
                    self.logger.info(f"从文件加载雷达图: {img_path}")
                except Exception as e2:
                    self.logger.warning(f"图片文件加载也失败: {img_path} - {str(e2)}")
                    img = Paragraph("[雷达图生成失败]", self.style_manager.styles['CN_Body'])
            else:
                img = Paragraph("[雷达图生成失败]", self.style_manager.styles['CN_Body'])

        # 创建图片表格 - 固定尺寸8x8cm，边框叠加在图片上
        img_table = Table(
            [[img]],
            colWidths=[8 * cm],
            rowHeights=[8 * cm],
            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D3DFEE')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ])
        )

        # 组合头部表格
        return Table(
            [[info_table, img_table]],
            colWidths=[8 * cm, 10 * cm],
            style=TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0)
            ])
        )
    
    def _build_evaluation_table(self, row: pd.Series) -> Table:
        """构建评价表格 - 支持文本类型的成绩/风格列，动态从第7列开始读取变量"""
        
        # 动态从第7列开始读取变量名（索引从0开始，所以第7列是索引6）
        all_columns = list(row.index)
        if len(all_columns) > 6:
            score_columns = all_columns[6:]  # 从第7列开始
            self.logger.info(f"动态读取评价变量（从第7列开始）: {score_columns}")
        else:
            # 如果列数不足7列，使用传统方法
            score_columns = [col for col in row.index if col not in ['姓名', 'ID', '生日', '年龄', '测试日期', '结果说明', '性别']]
            self.logger.warning(f"列数不足7列，使用传统方法筛选变量: {score_columns}")
        
        # 判断是否为文本类型（风格）数据
        is_text_data = False
        if score_columns:
            # 检查第一个成绩列的数据类型
            first_score = row[score_columns[0]]
            try:
                float(first_score)
                is_text_data = False
            except (ValueError, TypeError):
                is_text_data = True
        
        # 根据数据类型设置列标题
        score_header = "风格" if is_text_data else "成绩"
        
        data = [
            [Paragraph("测评项目", self.style_manager.styles['TableHeader']),
             Paragraph(score_header, self.style_manager.styles['TableHeader']),
             Paragraph("描述", self.style_manager.styles['TableHeader'])]
        ]

        # 使用动态读取的变量列表
        for task in score_columns:
            if task in row.index:
                score_value = row[task]
                
                if is_text_data:
                    # 文本数据直接显示，不进行评估
                    evaluation = "风格描述"
                    score_display = str(score_value) if pd.notna(score_value) else "-"
                else:
                    # 数值数据进行评估
                    evaluation = self._get_evaluation(task, score_value) if pd.notna(score_value) else "-"
                    try:
                        score_display = f"{float(score_value):.0f}" if pd.notna(score_value) else "-"
                    except (ValueError, TypeError):
                        score_display = str(score_value) if pd.notna(score_value) else "-"
                
                data.append([
                    Paragraph(task, self.style_manager.styles['Data_Body']),
                    Paragraph(score_display, self.style_manager.styles['Data_Body']),
                    Paragraph(evaluation, self.style_manager.styles['CN_Body'])
                ])

        return Table(
            data,
            colWidths=[4 * cm, 4 * cm, 10 * cm],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
                ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D3DFEE')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#4F81BD')),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ]),
            repeatRows=1
        )
    
    def generate_single_report(self, row: pd.Series, output_path: str, image_dir: str = None) -> bool:
        """
        生成单个报告
        
        Args:
            row: 数据行
            output_path: 输出路径
            image_dir: 图片目录（可选，用于向后兼容）
            
        Returns:
            bool: 是否成功生成
        """
        try:
            # 创建PDF文档 - 允许表格分页
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                leftMargin=1.5 * cm,
                rightMargin=1.5 * cm,
                topMargin=1 * cm,
                bottomMargin=0.5 * cm,
                pageCompression=0,
                invariant=True,
                allowSplitting=1,  # 允许分页
                showBoundary=0,
            )

            elements = []
            
            # 添加标题
            elements.append(Paragraph(
                self.report_title,
                self.style_manager.styles['ReportTitle']
            ))

            # 添加头部信息（现在会自动生成雷达图）
            elements.append(self._build_header(row, Path(image_dir) if image_dir else None))
            elements.append(Spacer(1, 0.5 * cm))
            
            # 添加评价表格（支持跨页和重复表头）
            elements.append(self._build_evaluation_table(row))

            # 生成PDF
            doc.build(elements)
            self.logger.info(f"成功生成报告: {output_path}")
            return True
            
        except Exception as e:
            # 安全获取姓名，避免错误
            name = "未知"
            try:
                if '姓名' in row and pd.notna(row['姓名']):
                    name = str(row['姓名'])
                elif 'ID' in row and pd.notna(row['ID']):
                    name = f"ID_{row['ID']}"
            except:
                pass
            
            self.logger.error(f"报告生成失败（{name}）：{str(e)}")
            return False
    
    def generate_batch_reports(self, data_file: str, output_dir: str, image_dir: str = None,
                             progress_callback: Optional[Callable] = None,
                             filename_mode: str = "name_custom",
                             filename_separator: str = "心理测评") -> Dict[str, Any]:
        """
        批量生成报告
        
        Args:
            data_file: Excel数据文件路径
            output_dir: 输出目录路径
            image_dir: 图片目录路径（可选，用于向后兼容）
            progress_callback: 进度回调函数
            filename_mode: 文件命名模式 ("id_only" 或 "name_custom")
            filename_separator: 自定义分隔符（仅在name_custom模式下使用）
            
        Returns:
            Dict: 生成结果统计
        """
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # 读取数据
            df = pd.read_excel(data_file)
            results["total"] = len(df)
            
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 转换日期列
            date_cols = ['生日', '测试日期']
            for col in date_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(r'\D', '', regex=True).str.zfill(8)
            
            # 设置进度回调
            if progress_callback:
                progress_callback(0, "开始生成报告...")
            
            # 逐个生成报告
            for index, (_, row) in enumerate(df.iterrows()):
                try:
                    # 根据命名模式生成文件名
                    if filename_mode == "id_only":
                        # 模式1：仅使用ID号
                        id_value = row.get('ID', '')
                        if pd.notna(id_value) and str(id_value).strip():
                            safe_name = str(id_value).strip()
                        else:
                            # 如果ID为空，使用行号
                            safe_name = f"报告_{index + 1}"
                        output_file = output_path / f"{safe_name}.pdf"
                    else:
                        # 模式2：姓名+自定义内容+报告
                        name_value = row.get('姓名', '')
                        if pd.isna(name_value) or not str(name_value).strip():
                            # 如果姓名为空，使用ID或行号
                            id_value = row.get('ID', '')
                            if pd.notna(id_value) and str(id_value).strip():
                                safe_name = f"ID_{str(id_value).strip()}"
                            else:
                                safe_name = f"报告_{index + 1}"
                        else:
                            safe_name = "".join(c for c in str(name_value) if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            if not safe_name:  # 如果处理后为空
                                safe_name = f"报告_{index + 1}"
                        
                        # 构建完整文件名：姓名+分隔符+报告
                        separator = filename_separator.strip() if filename_separator.strip() else "心理测评"
                        output_file = output_path / f"{safe_name}{separator}报告.pdf"
                    
                    # 生成报告
                    if self.generate_single_report(row, str(output_file), image_dir):
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        # 安全获取姓名用于错误信息
                        error_name = safe_name if safe_name else "未知"
                        results["errors"].append(f"{error_name}: 生成失败")
                    
                    # 更新进度 - 根据命名模式获取显示名称
                    if filename_mode == "id_only":
                        progress_name = safe_name
                    else:
                        progress_name = safe_name if safe_name else f"第{index + 1}个"
                    
                    if progress_callback:
                        progress = (index + 1) / results["total"] * 100
                        progress_callback(progress, f"已完成: {progress_name}")
                        
                except Exception as e:
                    results["failed"] += 1
                    # 安全获取姓名用于错误信息
                    try:
                        error_name = safe_name if 'safe_name' in locals() and safe_name else f"第{index + 1}个"
                    except:
                        error_name = f"第{index + 1}个"
                    
                    error_msg = f"{error_name}: {str(e)}"
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            if progress_callback:
                progress_callback(100, "所有报告生成完成")
                
        except Exception as e:
            error_msg = f"批量生成失败: {str(e)}"
            results["errors"].append(error_msg)
            self.logger.error(error_msg)
        
        return results
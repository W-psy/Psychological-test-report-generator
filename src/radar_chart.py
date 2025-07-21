"""
心理测试反馈报告生成器 - 雷达图生成模块
集成雷达图生成功能，支持动态变量数量和自定义样式
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import io
from typing import List, Tuple, Optional, Dict, Any
import logging

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)


class RadarChartGenerator:
    """雷达图生成器"""
    
    def __init__(self, 
                 figure_size: Tuple[int, int] = (8, 8),
                 dpi: int = 300,  # 提高DPI到300，大幅提升清晰度
                 baseline_score: float = 100.0,
                 chart_shape: str = 'circle'):
        """
        初始化雷达图生成器
        
        Args:
            figure_size: 图形尺寸 (宽, 高)
            dpi: 图像分辨率
            baseline_score: 基准线分数
            chart_shape: 图表形状 (固定为圆形)
        """
        self.figure_size = figure_size
        self.dpi = dpi
        self.baseline_score = baseline_score
        self.chart_shape = 'circle'  # 固定为圆形
        
        # 默认变量列表（可动态调整）
        self.default_variables = []
        
        # 样式配置 - 增强颜色饱和度和对比度
        self.style_config = {
            'line_color': '#1E3A8A',        # 更深的蓝色，增强对比度
            'line_width': 3.5,              # 稍微加粗线条
            'marker_size': 12,              # 增大标记点
            'marker_face_color': '#FFFFFF', # 纯白色标记
            'marker_edge_width': 2,         # 加粗标记边框
            'fill_color': '#3B82F6',        # 更鲜艳的蓝色填充
            'fill_alpha': 0.15,             # 稍微增加填充透明度
            'baseline_color': '#DC2626',    # 鲜艳的红色基准线
            'baseline_style': '--',         # 改为虚线
            'baseline_width': 2,            # 加粗基准线
            'baseline_alpha': 0.9,          # 增加基准线不透明度
            'grid_color': '#6B7280',        # 更深的灰色网格
            'grid_style': '-',
            'grid_alpha': 0.5,              # 增加网格可见度
            'outer_border_color': '#9CA3AF', # 更深的外边框颜色
            'outer_border_style': '--',      # 最外圈边界改为虚线
            'outer_border_alpha': 0.7,       # 增加外边框可见度
            'text_color': '#1F2937',         # 更深的文字颜色，增强对比度
            'title_font_size': 16,           # 任务名称字体大小
            'label_font_size': 14            # 标签字体大小
        }
    
    def _calculate_safe_baseline_angle(self, num_vars: int, var_angles: np.ndarray) -> float:
        """
        计算基准线标注的安全角度位置，避开变量标签
        
        Args:
            num_vars: 变量数量
            var_angles: 变量角度数组
            
        Returns:
            安全的角度位置（弧度）
        """
        # 将变量角度转换为0-2π范围
        var_angles_normalized = var_angles % (2 * np.pi)
        
        # 生成候选角度（每15度一个候选位置）
        candidate_angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)  # 24个候选位置
        
        # 计算每个候选角度与所有变量角度的最小距离
        min_distances = []
        for candidate in candidate_angles:
            distances = []
            for var_angle in var_angles_normalized:
                # 计算圆周上的最短距离
                diff = abs(candidate - var_angle)
                circular_distance = min(diff, 2 * np.pi - diff)
                distances.append(circular_distance)
            min_distances.append(min(distances))
        
        # 选择距离变量标签最远的角度
        best_angle_idx = np.argmax(min_distances)
        safe_angle = candidate_angles[best_angle_idx]
        
        # 确保最小距离至少为30度（π/6弧度）
        if min_distances[best_angle_idx] < np.pi / 6:
            # 如果所有候选位置都太近，选择一个相对安全的默认位置
            # 根据变量数量选择不同的默认角度
            if num_vars <= 4:
                safe_angle = np.pi / 8  # 22.5度
            elif num_vars <= 6:
                safe_angle = np.pi / 12  # 15度
            else:
                safe_angle = np.pi / 16  # 11.25度
        
        return safe_angle

    def _get_shape_angles(self, num_vars: int) -> np.ndarray:
        """
        计算圆形角度分布
        
        Args:
            num_vars: 变量数量
            
        Returns:
            角度数组
        """
        # 固定使用圆形：均匀分布
        return np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    def calculate_smart_range(self, scores: np.ndarray) -> Tuple[float, float]:
        """
        动态计算雷达图范围，边界为最高成绩往上最接近的5的倍数
        
        Args:
            scores: 分数数组
            
        Returns:
            (最小值, 最大值)
        """
        data_min = np.min(scores)
        data_max = np.max(scores)
        
        # 计算上界：取最高成绩往上最接近的5的倍数
        if data_max % 5 == 0:
            # 如果最高分已经是5的倍数，直接使用
            upper_bound = data_max
        else:
            # 否则向上取到最接近的5的倍数
            upper_bound = np.ceil(data_max / 5) * 5
        
        # 计算下界：按20分步长向下取整，最小不低于0
        lower_bound = max(np.floor(data_min / 20) * 20, 0)
        
        # 确保基准线在显示范围内
        if self.baseline_score > upper_bound:
            # 如果基准线超出上界，调整上界为基准线往上最接近的5的倍数
            if self.baseline_score % 5 == 0:
                upper_bound = self.baseline_score
            else:
                upper_bound = np.ceil(self.baseline_score / 5) * 5
        if self.baseline_score < lower_bound:
            lower_bound = np.floor(self.baseline_score / 20) * 20
        
        # 保证最小显示范围为60分，但不改变基于数据的上界
        if upper_bound - lower_bound < 60:
            # 优先向下调整下界，保持上界不变
            lower_bound = max(upper_bound - 60, 0)
            # 如果向下调整后仍不足60分，才向上调整上界
            if upper_bound - lower_bound < 60:
                needed_range = 60 - (upper_bound - lower_bound)
                upper_bound = upper_bound + needed_range
                # 调整后确保上界仍是5的倍数
                if upper_bound % 5 != 0:
                    upper_bound = np.ceil(upper_bound / 5) * 5
        
        return lower_bound, upper_bound
    
    def filter_valid_data(self, row: pd.Series, variables: List[str] = None) -> Tuple[List[str], np.ndarray]:
        """
        过滤有效数据
        
        Args:
            row: 数据行
            variables: 变量列表，如果为None则从第7列开始动态读取
            
        Returns:
            (有效变量列表, 有效分数数组)
        """
        if variables is None:
            # 动态从第7列开始读取变量名（索引从0开始，所以第7列是索引6）
            all_columns = list(row.index)
            if len(all_columns) > 6:
                variables = all_columns[6:]  # 从第7列开始
                logger.info(f"动态读取变量列表（从第7列开始）: {variables}")
            else:
                # 如果列数不足7列，使用默认变量列表
                variables = self.default_variables
                logger.warning(f"列数不足7列，使用默认变量列表: {variables}")
        
        # 添加调试信息
        logger.info(f"处理数据行 - ID: {row.get('ID', '未知')}")
        logger.info(f"期望的变量列表: {variables}")
        logger.info(f"Excel文件中的所有列: {list(row.index)}")
        logger.info(f"当前行的数据: {dict(row)}")
        
        # 过滤有效数据
        valid_data = []
        for var in variables:
            if var in row and pd.notna(row[var]):
                try:
                    # 先尝试直接转换
                    score = float(row[var])
                    valid_data.append((var, score))
                    logger.info(f"成功识别数值: {var} = {score}")
                except (ValueError, TypeError):
                    # 如果直接转换失败，尝试处理文本格式的数值
                    try:
                        # 去除空格和特殊字符，尝试转换
                        cleaned_value = str(row[var]).strip()
                        # 移除可能的非数字字符（保留数字、小数点、负号）
                        import re
                        numeric_value = re.sub(r'[^\d.-]', '', cleaned_value)
                        if numeric_value:
                            score = float(numeric_value)
                            valid_data.append((var, score))
                            logger.info(f"成功转换文本格式数值: {var} = '{row[var]}' -> {score}")
                        else:
                            logger.warning(f"无法从文本中提取数值: {var} = '{row[var]}'")
                            continue
                    except (ValueError, TypeError):
                        logger.warning(f"无法转换变量 {var} 的值: {row[var]}")
                        continue
            else:
                if var not in row:
                    logger.warning(f"变量 '{var}' 在Excel文件中不存在")
                elif pd.isna(row[var]):
                    logger.warning(f"变量 '{var}' 的值为空: {row[var]}")
        
        logger.info(f"最终有效数据点: {len(valid_data)} 个")
        for var, score in valid_data:
            logger.info(f"  - {var}: {score}")
        
        if len(valid_data) < 3:
            raise ValueError(f"有效数据点不足3个，无法生成雷达图。当前有效数据: {len(valid_data)}")
        
        valid_vars, valid_scores = zip(*valid_data)
        return list(valid_vars), np.array(valid_scores, dtype=float)
    
    def generate_radar_chart(self, 
                           row: pd.Series, 
                           variables: List[str] = None,
                           title: str = None,
                           save_path: Optional[str] = None) -> Optional[bytes]:
        """
        生成雷达图
        
        Args:
            row: 数据行
            variables: 变量列表
            title: 图表标题
            save_path: 保存路径，如果为None则返回字节数据
            
        Returns:
            如果save_path为None，返回图像字节数据；否则返回None
        """
        try:
            # 设置matplotlib高质量渲染参数
            plt.rcParams['figure.dpi'] = self.dpi
            plt.rcParams['savefig.dpi'] = self.dpi
            plt.rcParams['font.size'] = 12
            plt.rcParams['axes.linewidth'] = 1.2
            plt.rcParams['lines.linewidth'] = 2
            plt.rcParams['patch.linewidth'] = 1
            plt.rcParams['xtick.major.width'] = 1
            plt.rcParams['ytick.major.width'] = 1
            plt.rcParams['text.antialiased'] = True
            plt.rcParams['figure.facecolor'] = 'white'
            plt.rcParams['axes.facecolor'] = 'white'
            
            # 过滤有效数据
            valid_vars, valid_scores = self.filter_valid_data(row, variables)
            
            # 计算极坐标角度 - 使用形状特定的角度分布
            num_vars = len(valid_vars)
            angles = self._get_shape_angles(num_vars)
            angles = np.concatenate([angles, [angles[0]]])
            scores = np.concatenate([valid_scores, [valid_scores[0]]])
            
            # 计算智能范围
            range_min, range_max = self.calculate_smart_range(valid_scores)
            
            # 创建画布 - 确保正方形比例
            fig = plt.figure(figsize=self.figure_size)
            ax = fig.add_subplot(111, polar=True)
            
            # 确保图形为正方形比例
            ax.set_aspect('equal')
            
            # 绘制主图形
            ax.plot(angles, scores, 'o-', 
                   color=self.style_config['line_color'],
                   linewidth=self.style_config['line_width'],
                   markersize=self.style_config['marker_size'],
                   markerfacecolor=self.style_config['marker_face_color'],
                   markeredgewidth=self.style_config['marker_edge_width'])
            
            # 填充区域
            ax.fill(angles, scores, 
                   color=self.style_config['fill_color'],
                   alpha=self.style_config['fill_alpha'])
            
            # 设置坐标系统
            ax.set_ylim(range_min, range_max)
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            
            # 绘制基准线（深灰色虚线，正常粗细）
            ax.axhline(self.baseline_score, 
                      color=self.style_config['baseline_color'],
                      linestyle=self.style_config['baseline_style'],
                      linewidth=self.style_config['baseline_width'],
                      alpha=self.style_config['baseline_alpha'])
            
            # 设置网格样式
            ax.grid(True, 
                   color=self.style_config['grid_color'],
                   linestyle=self.style_config['grid_style'],
                   alpha=self.style_config['grid_alpha'])
            
            # 动态刻度标签
            yticks = list(np.arange(range_min, range_max + 1, 20))
            if self.baseline_score not in yticks:
                yticks.append(self.baseline_score)
            
            # 确保range_max在刻度中，这样最外圈虚线就有对应的刻度
            if range_max not in yticks:
                yticks.append(range_max)
            
            yticks = sorted(list(set(yticks)))
            
            # 设置最外界边界为减淡的虚线，使用更稀疏的虚线样式
            # 完全移除默认边界
            ax.spines['polar'].set_visible(False)
            
            # 手动绘制外圈虚线边界 - 使用最大的刻度值
            theta = np.linspace(0, 2*np.pi, 100)
            outer_radius = max(yticks)  # 使用最大刻度值而不是range_max
            ax.plot(theta, [outer_radius]*len(theta), 
                   color=self.style_config['outer_border_color'],
                   linestyle=(0, (12, 8)),  # 更稀疏的虚线：12个点线段，8个点间隔
                   linewidth=1.5,
                   alpha=self.style_config['outer_border_alpha'])
            
            # 设置所有刻度（包括基准线），但基准线标签特殊处理
            ax.set_yticks(yticks)
            ax.set_yticklabels([f"{int(y)}" if y != self.baseline_score else ""
                               for y in yticks], 
                              color=self.style_config['text_color'],
                              fontsize=self.style_config['label_font_size'])
            
            # 智能计算基准线标注位置，避开变量标签
            if self.baseline_score >= range_min and self.baseline_score <= range_max:
                # 计算安全的角度位置
                safe_angle = self._calculate_safe_baseline_angle(num_vars, angles[:-1])
                # 直接在基准线上显示标注，不向外偏移
                label_radius = self.baseline_score
                
                ax.text(safe_angle, label_radius, f"{int(self.baseline_score)}\n(基准)", 
                       ha='center', va='center',
                       color=self.style_config['text_color'],
                       fontsize=self.style_config['label_font_size'],
                       bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor='white', 
                                edgecolor=self.style_config['baseline_color'],
                                alpha=0.9))
            
            # 设置角度刻度 - 增大任务名称字体
            ax.set_thetagrids(np.degrees(angles[:-1]), valid_vars, 
                             fontsize=self.style_config['title_font_size'])
            
            # 设置标题
            if title:
                ax.set_title(title, 
                           color=self.style_config['text_color'],
                           fontsize=self.style_config['title_font_size'],
                           pad=20)
            
            # 确保图形比例正确，防止压缩
            plt.tight_layout()
            fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            
            # 保存或返回字节数据
            if save_path:
                plt.savefig(save_path, 
                           dpi=self.dpi, 
                           bbox_inches='tight',
                           facecolor='white',      # 设置背景为白色
                           edgecolor='none',       # 无边框
                           format='png',           # 明确指定PNG格式
                           pil_kwargs={'optimize': True, 'quality': 95})  # 高质量PNG
                plt.close()
                return None
            else:
                # 返回字节数据
                buffer = io.BytesIO()
                plt.savefig(buffer, 
                           format='png', 
                           dpi=self.dpi, 
                           bbox_inches='tight',
                           facecolor='white',      # 设置背景为白色
                           edgecolor='none',       # 无边框
                           pil_kwargs={'optimize': True, 'quality': 95})  # 高质量PNG
                buffer.seek(0)
                image_bytes = buffer.getvalue()
                buffer.close()
                plt.close()
                return image_bytes
                
        except Exception as e:
            logger.error(f"生成雷达图失败 - ID: {row.get('ID', '未知')}, 错误: {str(e)}")
            plt.close('all')  # 确保清理资源
            raise
    
    def batch_generate_radar_charts(self, 
                                  data: pd.DataFrame,
                                  variables: List[str] = None,
                                  output_dir: str = None,
                                  progress_callback=None) -> Dict[str, Any]:
        """
        批量生成雷达图
        
        Args:
            data: 数据DataFrame
            variables: 变量列表
            output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            生成结果统计
        """
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)
        
        results = {
            'total': len(data),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for idx, (_, row) in enumerate(data.iterrows()):
            try:
                if output_dir:
                    save_path = output_path / f"{row['ID']}.png"
                    self.generate_radar_chart(row, variables, save_path=str(save_path))
                else:
                    self.generate_radar_chart(row, variables)
                
                results['success'] += 1
                
            except Exception as e:
                results['failed'] += 1
                error_msg = f"ID: {row.get('ID', '未知')} - {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"批量生成雷达图失败: {error_msg}")
            
            # 更新进度
            if progress_callback:
                progress = (idx + 1) / len(data) * 100
                progress_callback(progress, f"处理 {row.get('ID', '未知')}")
        
        return results
    
    def get_supported_variables(self, data: pd.DataFrame) -> List[str]:
        """
        获取数据中支持的变量列表
        
        Args:
            data: 数据DataFrame
            
        Returns:
            支持的变量列表
        """
        supported_vars = []
        for var in self.default_variables:
            if var in data.columns:
                # 检查是否有有效数据
                valid_count = data[var].notna().sum()
                if valid_count > 0:
                    supported_vars.append(var)
        
        return supported_vars
    
    def update_style_config(self, **kwargs):
        """
        更新样式配置
        
        Args:
            **kwargs: 样式参数
        """
        self.style_config.update(kwargs)
    
    def set_variables(self, variables: List[str]):
        """
        设置默认变量列表
        
        Args:
            variables: 变量列表
        """
        self.default_variables = variables


# 便捷函数
def create_radar_chart(row: pd.Series, 
                      variables: List[str] = None,
                      output_path: str = None,
                      chart_shape: str = 'circle',
                      **kwargs) -> Optional[bytes]:
    """
    便捷函数：创建单个雷达图
    
    Args:
        row: 数据行
        variables: 变量列表
        output_path: 输出路径
        chart_shape: 图表形状 ('circle', 'triangle', 'diamond', 'pentagon', 'hexagon')
        **kwargs: 其他参数
        
    Returns:
        如果output_path为None，返回图像字节数据
    """
    generator = RadarChartGenerator(chart_shape=chart_shape, **kwargs)
    return generator.generate_radar_chart(row, variables, save_path=output_path)


def batch_create_radar_charts(data: pd.DataFrame,
                            variables: List[str] = None,
                            output_dir: str = None,
                            progress_callback=None,
                            chart_shape: str = 'circle',
                            **kwargs) -> Dict[str, Any]:
    """
    便捷函数：批量创建雷达图
    
    Args:
        data: 数据DataFrame
        variables: 变量列表
        output_dir: 输出目录
        progress_callback: 进度回调函数
        chart_shape: 图表形状 ('circle', 'triangle', 'diamond', 'pentagon', 'hexagon')
        **kwargs: 其他参数
        
    Returns:
        生成结果统计
    """
    generator = RadarChartGenerator(chart_shape=chart_shape, **kwargs)
    return generator.batch_generate_radar_charts(data, variables, output_dir, progress_callback)
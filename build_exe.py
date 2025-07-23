#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心理测试反馈报告生成器 - PyInstaller打包脚本
适用于Python 3.12环境

项目信息:
- 项目名称: 心理测试反馈报告生成器
- 版本: 1.0.2
- 发布日期: 2025-07-23
- Python版本要求: >=3.12（推荐使用Python 3.12.7）
- 主要功能: 专业的心理测评数据分析工具，自动生成包含高质量雷达图的个性化PDF报告

打包后目录结构:
dist/
└── PsychTestReportGenerator1.0.2/
    ├── PsychTestReportGenerator1.0.2.exe    # 主程序可执行文件
    ├── README.md                             # 详细使用说明（Markdown格式）
    ├── README.txt                            # 简要使用说明（文本格式）
    ├── config.json                           # 应用配置文件
    ├── logs/                                 # 日志目录
    │   └── app_20250722.log                 # 应用日志文件
    ├── templates/                            # Excel模板文件目录
    │   ├── config_template_2_tiers.xlsx     # 2档评分模板
    │   ├── config_template_3_tiers.xlsx     # 3档评分模板
    │   ├── config_template_4_tiers.xlsx     # 4档评分模板
    │   ├── config_template_5_tiers.xlsx     # 5档评分模板
    │   ├── config_template_6_tiers.xlsx     # 6档评分模板
    │   ├── config_template_7_tiers.xlsx     # 7档评分模板
    │   └── test_data.xlsx                   # 测试数据文件
    └── 快速使用指南.md                       # 中文快速使用指南

使用方法:
1. 确保已安装Python 3.12环境并激活pyinstaller_env_py312环境
2. 运行此脚本进行自动打包
3. 打包完成后，整个PsychTestReportGenerator1.0.2文件夹即为完整的分发包

作者: AI Assistant
版本: 1.0.2
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime

class PyInstallerBuilder:
    """PyInstaller打包器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.dist_dir = self.project_root / "dist"
        self.temp_dir = self.project_root / "temp"
        self.build_dir = self.project_root / "build"
        
        # 确保目录存在
        self.dist_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # 读取版本信息
        self.version_info = self._load_version_info()
        
    def _load_version_info(self):
        """加载版本信息"""
        version_file = self.project_root / "version.json"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0.2", "name": "心理测试反馈报告生成器"}
    
    def check_environment(self):
        """检查环境"""
        print("🔍 检查环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major != 3 or python_version.minor != 12:
            print(f"❌ 错误: 当前Python版本为 {python_version.major}.{python_version.minor}, 需要Python 3.12")
            print("请激活pyinstaller_env_py312环境: conda activate pyinstaller_env_py312")
            return False
        else:
            print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
            print("✅ 版本兼容性: 完美匹配Python 3.12要求")
        
        # 检查必要文件
        required_files = [
            self.src_dir / "main.py",
            self.project_root / "requirements.txt",
            self.project_root / "icon.png"
        ]
        
        for file_path in required_files:
            if file_path.exists():
                print(f"✅ 找到文件: {file_path.name}")
            else:
                print(f"❌ 缺少文件: {file_path}")
                return False
        
        return True
    
    def create_conda_env(self):
        """创建conda虚拟环境"""
        env_name = "pyinstaller_env_py312"
        print(f"🐍 检查conda虚拟环境: {env_name}")
        
        try:
            # 检查环境是否已存在
            result = subprocess.run(
                ["conda", "env", "list", "--json"],
                capture_output=True, text=True, check=True
            )
            envs = json.loads(result.stdout)
            env_exists = any(env_name in env for env in envs["envs"])
            
            if env_exists:
                print(f"📦 环境 {env_name} 已存在")
            else:
                # 创建新环境
                subprocess.run([
                    "conda", "create", "-n", env_name, 
                    "python=3.12", "-y"
                ], check=True)
                print(f"✅ 成功创建环境: {env_name}")
            
            return env_name
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 创建conda环境失败: {e}")
            return None
        except FileNotFoundError:
            print("❌ 未找到conda命令，请确保已安装Anaconda或Miniconda")
            return None
    
    def install_dependencies(self, env_name):
        """安装依赖"""
        print("📦 安装依赖包...")
        
        try:
            # 获取conda环境的Python路径
            result = subprocess.run(
                ["conda", "info", "--envs", "--json"],
                capture_output=True, text=True, check=True
            )
            envs_info = json.loads(result.stdout)
            
            # 找到目标环境路径
            env_path = None
            for env in envs_info["envs"]:
                if env_name in env:
                    env_path = env
                    break
            
            if not env_path:
                print(f"❌ 未找到环境: {env_name}")
                return False
            
            # 使用环境中的pip直接安装
            if os.name == 'nt':  # Windows
                pip_path = os.path.join(env_path, "Scripts", "pip.exe")
                python_path = os.path.join(env_path, "python.exe")
            else:  # Linux/Mac
                pip_path = os.path.join(env_path, "bin", "pip")
                python_path = os.path.join(env_path, "bin", "python")
            
            # 检查pip是否存在
            if not os.path.exists(pip_path):
                print(f"❌ 未找到pip: {pip_path}")
                return False
            
            # 安装依赖
            subprocess.run([
                pip_path, "install", "-r", "requirements.txt"
            ], check=True, cwd=self.project_root)
            
            print("✅ 依赖安装完成")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ 解析conda环境信息失败: {e}")
            return False
    
    def create_spec_file(self):
        """创建PyInstaller spec文件"""
        print("📝 创建PyInstaller spec文件...")
        
        app_name = self.version_info.get("name", "心理测试反馈报告生成器")
        app_version = self.version_info.get("version", "1.0.2")
        
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件配置
added_files = [
    ('templates', 'templates'),
    ('assets', 'assets'),
    ('config.json', '.'),
    ('icon.png', '.'),
    ('version.json', '.'),
]

# 隐藏导入模块
hiddenimports = [
    # src目录下的模块
    'config',
    'utils',
    'report_generator',
    'config_manager',
    'radar_chart',
    # 第三方库
    'pandas',
    'numpy',
    'matplotlib',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_tkagg',
    'reportlab',
    'reportlab.pdfbase',
    'reportlab.pdfbase.ttfonts',
    'reportlab.lib.fonts',
    'reportlab.platypus',
    'openpyxl',
    'openpyxl.cell._writer',
    'PIL',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'psutil',
    'pathlib',
    'datetime',
    'logging',
    'threading',
    'json',
    'io',
    'typing',
]

# 排除的模块
excludedimports = [
    'tkinter.test',
    'test',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],  # 添加src目录到Python路径
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludedimports,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}_v{app_version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩，避免杀毒软件误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',  # 设置图标
)
'''
        
        spec_file = self.project_root / "app.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ Spec文件已创建: {spec_file}")
        return spec_file
    
    def build_executable(self, env_name, spec_file):
        """构建可执行文件"""
        print("🔨 开始构建可执行文件...")
        
        try:
            # 清理之前的构建
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            
            # 获取conda环境的Python路径
            result = subprocess.run(
                ["conda", "info", "--envs", "--json"],
                capture_output=True, text=True, check=True
            )
            envs_info = json.loads(result.stdout)
            
            # 找到目标环境路径
            env_path = None
            for env in envs_info["envs"]:
                if env_name in env:
                    env_path = env
                    break
            
            if not env_path:
                print(f"❌ 未找到环境: {env_name}")
                return False
            
            # 使用环境中的pyinstaller
            if os.name == 'nt':  # Windows
                pyinstaller_path = os.path.join(env_path, "Scripts", "pyinstaller.exe")
            else:  # Linux/Mac
                pyinstaller_path = os.path.join(env_path, "bin", "pyinstaller")
            
            # 检查pyinstaller是否存在
            if not os.path.exists(pyinstaller_path):
                print(f"❌ 未找到pyinstaller: {pyinstaller_path}")
                return False
            
            # 构建命令
            subprocess.run([
                pyinstaller_path, "--clean", "--noconfirm", str(spec_file)
            ], check=True, cwd=self.project_root)
            
            print("✅ 构建完成")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ 解析conda环境信息失败: {e}")
            return False
    
    def post_build_cleanup(self):
        """构建后清理并组织目录结构"""
        print("🧹 清理临时文件并组织目录结构...")
        
        # 创建版本化的目标目录
        version = self.version_info.get("version", "1.0.2")
        target_dir = self.dist_dir / f"PsychTestReportGenerator{version}"
        target_dir.mkdir(exist_ok=True)
        
        # 查找生成的exe文件
        build_dist = self.project_root / "dist"
        exe_found = False
        
        if build_dist.exists():
            # 查找生成的exe文件
            exe_files = list(build_dist.glob("*.exe"))
            if exe_files:
                exe_file = exe_files[0]
                # 重命名exe文件以包含版本信息
                new_exe_name = f"PsychTestReportGenerator{version}.exe"
                final_exe_path = target_dir / new_exe_name
                try:
                    shutil.copy2(str(exe_file), str(final_exe_path))
                    print(f"✅ 可执行文件已复制到: {final_exe_path}")
                    exe_found = True
                except Exception as e:
                    print(f"⚠️  复制exe文件时出错: {e}")
        
        # 如果没有找到exe文件，检查是否直接在项目根目录
        if not exe_found:
            exe_files = list(self.project_root.glob("*.exe"))
            if exe_files:
                exe_file = exe_files[0]
                new_exe_name = f"PsychTestReportGenerator{version}.exe"
                final_exe_path = target_dir / new_exe_name
                try:
                    shutil.copy2(str(exe_file), str(final_exe_path))
                    print(f"✅ 可执行文件已复制到: {final_exe_path}")
                    # 删除原文件
                    exe_file.unlink()
                    exe_found = True
                except Exception as e:
                    print(f"⚠️  复制exe文件时出错: {e}")
        
        if not exe_found:
            print("⚠️  未找到生成的exe文件")
        
        # 复制必要的资源文件到目标目录
        resources_to_copy = [
            ("config.json", "config.json"),
            ("templates", "templates"),
            ("快速使用指南.md", "快速使用指南.md")
        ]
        
        for src_name, dst_name in resources_to_copy:
            src_path = self.project_root / src_name
            dst_path = target_dir / dst_name
            
            if src_path.exists():
                try:
                    if src_path.is_dir():
                        if dst_path.exists():
                            shutil.rmtree(dst_path)
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                    print(f"✅ 已复制资源: {src_name} -> {dst_name}")
                except Exception as e:
                    print(f"⚠️  复制资源 {src_name} 时出错: {e}")
            else:
                print(f"⚠️  未找到资源文件: {src_name}")
        
        # 创建logs目录
        logs_dir = target_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # 如果存在日志文件，复制过去
        src_logs = self.project_root / "src" / "logs"
        if src_logs.exists():
            try:
                for log_file in src_logs.glob("*.log"):
                    shutil.copy2(log_file, logs_dir)
                print("✅ 已复制日志文件")
            except Exception as e:
                print(f"⚠️  复制日志文件时出错: {e}")
        
        # 清理临时文件
        cleanup_dirs = [self.build_dir, self.project_root / "dist"]
        for dir_path in cleanup_dirs:
            if dir_path.exists() and dir_path != self.dist_dir:
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"⚠️  清理目录 {dir_path} 时出错: {e}")
        
        # 清理spec文件
        spec_file = self.project_root / "app.spec"
        if spec_file.exists():
            try:
                spec_file.unlink()
            except Exception as e:
                print(f"⚠️  删除spec文件时出错: {e}")
        
        print(f"✅ 清理完成，打包目录: {target_dir}")
    
    def create_readme(self):
        """创建打包说明文件"""
        version = self.version_info.get("version", "1.0.2")
        target_dir = self.dist_dir / f"PsychTestReportGenerator{version}"
        
        # 创建简要说明文件 (README.txt)
        readme_txt_content = f'''{self.version_info.get("name", "心理测试反馈报告生成器")} v{version}
========================================

使用说明：
1. 双击运行 "PsychTestReportGenerator{version}.exe"
2. 选择包含测试数据的Excel文件
3. 选择输出目录（生成的报告将保存在此处）
4. 可选：选择雷达图目录（如果有预制的雷达图）
5. 点击"开始生成"按钮

系统要求：
- Windows 7/8/10/11 (64位)
- 无需安装Python环境

注意事项：
- Excel文件格式请参考templates目录中的模板文件
- 确保有足够的磁盘空间用于生成报告
- 生成过程中请勿关闭程序
- 首次运行可能被杀毒软件拦截，请添加信任

版本信息：v{version}
构建时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Python版本：{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
'''
        
        # 创建详细说明文件 (README.md)
        readme_md_content = f'''# {self.version_info.get("name", "心理测试反馈报告生成器")} v{version}

## 项目简介

{self.version_info.get("description", "专业的心理测评数据分析工具，自动生成包含高质量雷达图的个性化PDF报告")}

## 版本信息

- **版本号**: {version}
- **发布日期**: {self.version_info.get("release_date", "2025-07-22")}
- **构建时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Python版本**: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
- **Python要求**: {self.version_info.get("python_version", ">=3.7")}

## 主要功能

'''
        
        # 添加功能列表
        features = self.version_info.get("features", [])
        for feature in features:
            readme_md_content += f"- {feature}\n"
        
        readme_md_content += f'''

## 使用说明

### 快速开始

1. 双击运行 `PsychTestReportGenerator{version}.exe`
2. 在界面中选择包含测试数据的Excel文件
3. 选择输出目录（生成的报告将保存在此处）
4. 可选：选择雷达图目录（如果有预制的雷达图）
5. 点击"开始生成"按钮

### Excel文件格式

请参考 `templates/` 目录中的模板文件：
- `config_template_2_tiers.xlsx` - 2档评分模式
- `config_template_3_tiers.xlsx` - 3档评分模式
- `config_template_4_tiers.xlsx` - 4档评分模式
- `config_template_5_tiers.xlsx` - 5档评分模式
- `config_template_6_tiers.xlsx` - 6档评分模式
- `config_template_7_tiers.xlsx` - 7档评分模式
- `test_data.xlsx` - 测试数据示例

## 系统要求

- **操作系统**: Windows 7/8/10/11 (64位)
- **内存**: 建议4GB以上
- **磁盘空间**: 至少500MB可用空间
- **其他**: 无需安装Python环境

## 注意事项

- 确保有足够的磁盘空间用于生成报告
- 生成过程中请勿关闭程序
- 首次运行可能被杀毒软件拦截，请添加信任
- 如遇问题，请查看 `logs/` 目录中的日志文件

## 更新日志

### v{version}
'''
        
        # 添加更新日志
        changelog = self.version_info.get("changelog", {})
        if version in changelog:
            for change in changelog[version]:
                readme_md_content += f"- {change}\n"
        
        readme_md_content += '''

## 技术支持

如遇问题，请：
1. 查看日志文件（`logs/` 目录）
2. 参考快速使用指南
3. 联系开发者或查看项目文档

---

*本软件为免费开源项目，仅供学习和研究使用。*
'''
        
        # 写入文件
        readme_txt_file = target_dir / "README.txt"
        readme_md_file = target_dir / "README.md"
        
        with open(readme_txt_file, 'w', encoding='utf-8') as f:
            f.write(readme_txt_content)
        
        with open(readme_md_file, 'w', encoding='utf-8') as f:
            f.write(readme_md_content)
        
        print(f"✅ 说明文件已创建: {readme_txt_file}")
        print(f"✅ 详细说明已创建: {readme_md_file}")
    
    def build(self):
        """执行完整的打包流程"""
        print("🚀 开始打包流程...")
        print("=" * 50)
        
        # 1. 检查环境
        if not self.check_environment():
            print("❌ 环境检查失败，请修复后重试")
            return False
        
        # 2. 创建conda环境
        env_name = self.create_conda_env()
        if not env_name:
            print("❌ 环境创建失败")
            return False
        
        # 3. 安装依赖
        if not self.install_dependencies(env_name):
            print("❌ 依赖安装失败")
            return False
        
        # 4. 创建spec文件
        spec_file = self.create_spec_file()
        
        # 5. 构建可执行文件
        if not self.build_executable(env_name, spec_file):
            print("❌ 构建失败")
            return False
        
        # 6. 后处理
        self.post_build_cleanup()
        self.create_readme()
        
        print("=" * 50)
        print("🎉 打包完成！")
        print(f"📁 输出目录: {self.dist_dir}")
        return True

def main():
    """主函数"""
    print("心理测试反馈报告生成器 - PyInstaller打包工具")
    print("=" * 50)
    
    builder = PyInstallerBuilder()
    success = builder.build()
    
    if success:
        print("\n✅ 打包成功完成！")
        print(f"可执行文件位于: {builder.dist_dir}")
    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
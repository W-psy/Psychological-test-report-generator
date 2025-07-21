#!/usr/bin/env python3
"""
版本管理工具脚本
用于自动化版本更新、标签创建和发布流程
"""

import json
import os
import sys
import subprocess
import datetime
from pathlib import Path

def load_version():
    """加载当前版本信息"""
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 错误：找不到 version.json 文件")
        sys.exit(1)

def save_version(version_data):
    """保存版本信息"""
    with open('version.json', 'w', encoding='utf-8') as f:
        json.dump(version_data, f, ensure_ascii=False, indent=2)

def update_version(new_version, description=""):
    """更新版本号"""
    version_data = load_version()
    old_version = version_data['version']
    
    # 更新版本信息
    version_data['version'] = new_version
    version_data['release_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 添加到更新日志
    if 'changelog' not in version_data:
        version_data['changelog'] = []
    
    changelog_entry = {
        'version': new_version,
        'date': version_data['release_date'],
        'description': description or f"版本 {new_version} 发布"
    }
    version_data['changelog'].insert(0, changelog_entry)
    
    save_version(version_data)
    print(f"✅ 版本已更新：{old_version} → {new_version}")
    return version_data

def run_command(command, check=True):
    """运行命令"""
    print(f"🔄 执行命令：{command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败：{e}")
        if e.stderr:
            print(f"错误信息：{e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_git():
    """检查Git是否可用"""
    result = run_command("git --version", check=False)
    if result.returncode != 0:
        print("❌ 错误：Git 未安装或不可用")
        print("请先安装 Git：https://git-scm.com/download/win")
        sys.exit(1)
    print("✅ Git 可用")

def check_clean_working_tree():
    """检查工作树是否干净"""
    result = run_command("git status --porcelain", check=False)
    if result.returncode == 0 and result.stdout.strip():
        print("❌ 错误：工作目录有未提交的更改")
        print("请先提交或暂存所有更改")
        sys.exit(1)
    print("✅ 工作目录干净")

def create_tag(version, message=""):
    """创建Git标签"""
    tag_name = f"v{version}"
    tag_message = message or f"Release version {version}"
    
    # 创建标签
    run_command(f'git tag -a {tag_name} -m "{tag_message}"')
    print(f"✅ 已创建标签：{tag_name}")
    
    # 推送标签
    run_command(f"git push origin {tag_name}")
    print(f"✅ 已推送标签到远程仓库")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # 检查是否安装了 pyinstaller
    result = run_command("pyinstaller --version", check=False)
    if result.returncode != 0:
        print("📦 安装 PyInstaller...")
        run_command("pip install pyinstaller")
    
    # 构建
    build_command = "pyinstaller --onefile --windowed --name=心理测试报告生成器 src/main.py"
    run_command(build_command)
    print("✅ 可执行文件构建完成")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python scripts/version_manager.py <命令> [参数]")
        print("")
        print("命令：")
        print("  update <版本号> [描述]  - 更新版本号")
        print("  tag <版本号> [消息]     - 创建Git标签")
        print("  release <版本号> [描述] - 完整发布流程")
        print("  build                  - 构建可执行文件")
        print("  status                 - 显示当前状态")
        print("")
        print("示例：")
        print("  python scripts/version_manager.py update 1.1.0 '添加新功能'")
        print("  python scripts/version_manager.py release 1.1.0 '重要更新'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        version_data = load_version()
        print(f"📋 当前版本：{version_data['version']}")
        print(f"📅 发布日期：{version_data['release_date']}")
        print(f"📝 描述：{version_data['description']}")
        
    elif command == "update":
        if len(sys.argv) < 3:
            print("❌ 错误：请提供版本号")
            sys.exit(1)
        
        new_version = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        update_version(new_version, description)
        
    elif command == "tag":
        if len(sys.argv) < 3:
            print("❌ 错误：请提供版本号")
            sys.exit(1)
        
        check_git()
        check_clean_working_tree()
        
        version = sys.argv[2]
        message = sys.argv[3] if len(sys.argv) > 3 else ""
        create_tag(version, message)
        
    elif command == "build":
        build_executable()
        
    elif command == "release":
        if len(sys.argv) < 3:
            print("❌ 错误：请提供版本号")
            sys.exit(1)
        
        check_git()
        check_clean_working_tree()
        
        new_version = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        
        print(f"🚀 开始发布流程：版本 {new_version}")
        
        # 1. 更新版本
        update_version(new_version, description)
        
        # 2. 提交版本更新
        run_command("git add version.json")
        run_command(f'git commit -m "chore: 准备发布 v{new_version}"')
        
        # 3. 创建标签
        create_tag(new_version, description)
        
        # 4. 构建可执行文件
        build_executable()
        
        print(f"✅ 发布完成！版本 {new_version}")
        print("📝 下一步：")
        print("  1. 在 GitHub 上创建 Release")
        print("  2. 上传构建的可执行文件")
        print("  3. 添加发布说明")
        
    else:
        print(f"❌ 错误：未知命令 '{command}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
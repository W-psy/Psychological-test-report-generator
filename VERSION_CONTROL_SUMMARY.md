# 版本管理和 GitHub 管理流程总结

## 🎯 已完成的版本管理设置

我已经为您的项目创建了完整的版本管理和 GitHub 管理流程，包括以下文件和配置：

### 📁 版本控制文件
- **`.gitignore`** - Git忽略文件配置
- **`LICENSE`** - MIT开源许可证
- **`CHANGELOG.md`** - 版本更新日志
- **`CONTRIBUTING.md`** - 贡献指南

### 📁 GitHub 配置
- **`.github/ISSUE_TEMPLATE/`** - Issue模板
  - `bug_report.yml` - Bug报告模板
  - `feature_request.yml` - 功能请求模板
- **`.github/workflows/ci.yml`** - CI/CD自动化流程

### 📁 文档
- **`README_GITHUB.md`** - GitHub项目说明文档
- **`docs/GIT_GITHUB_SETUP.md`** - Git和GitHub详细设置指南
- **`docs/VERSION_MANAGEMENT.md`** - 版本管理指南

### 📁 自动化工具
- **`scripts/version_manager.py`** - Python版本管理脚本
- **`scripts/version_manager.bat`** - Windows批处理版本管理工具

## 🚀 下一步操作指南

### 第一步：安装 Git
```bash
# 1. 下载并安装 Git
# 访问：https://git-scm.com/download/win

# 2. 配置 Git
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱"
```

### 第二步：创建 GitHub 仓库
1. 登录 [GitHub](https://github.com)
2. 创建新仓库：`psychological-test-report-generator`
3. 选择 Public 或 Private
4. 不要添加 README、.gitignore 或 LICENSE（我们已经有了）

### 第三步：初始化本地仓库
```bash
# 在项目目录中运行
git init
git remote add origin https://github.com/您的用户名/psychological-test-report-generator.git
git add .
git commit -m "feat: 初始版本发布"
git branch -M main
git push -u origin main
```

### 第四步：使用版本管理工具

#### 方式一：使用批处理工具（推荐）
```bash
# 双击运行
scripts\version_manager.bat
```

#### 方式二：使用Python脚本
```bash
# 查看当前状态
python scripts\version_manager.py status

# 更新版本
python scripts\version_manager.py update 1.1.0 "添加新功能"

# 完整发布流程
python scripts\version_manager.py release 1.1.0 "重要更新"
```

## 📋 版本管理工作流程

### 日常开发
```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发代码
# ... 编写代码 ...

# 3. 提交更改
git add .
git commit -m "feat: 添加新功能"

# 4. 推送并创建 Pull Request
git push origin feature/new-feature
```

### 发布新版本
```bash
# 使用自动化工具
python scripts\version_manager.py release 1.1.0 "版本描述"

# 或手动执行
git checkout main
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main --tags
```

## 🔧 GitHub 功能配置

### Issues 管理
- ✅ Bug报告模板
- ✅ 功能请求模板
- ✅ 标签分类系统

### Pull Requests
- ✅ 代码审查流程
- ✅ 自动化测试检查
- ✅ 分支保护规则

### CI/CD 自动化
- ✅ 多Python版本测试
- ✅ 代码质量检查
- ✅ 自动构建可执行文件
- ✅ 自动发布到 GitHub Releases

### 项目管理
- ✅ Milestones 版本规划
- ✅ Projects 看板管理
- ✅ 自动化工作流

## 📊 版本号规范

使用语义化版本：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增  
- **修订号**：向下兼容的问题修正

## 🎯 推荐的发布节奏

- **修订版本**：随时发布（bug修复）
- **次版本**：每月1-2次（新功能）
- **主版本**：每年1-2次（重大更新）

## 📝 提交信息规范

```
type(scope): description

类型：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动
```

## 🛠️ 故障排除

### 常见问题
1. **Git未安装** - 下载安装 Git for Windows
2. **权限问题** - 检查 GitHub 访问权限
3. **合并冲突** - 使用 `git pull --rebase` 解决
4. **推送失败** - 检查远程仓库地址和权限

### 获取帮助
- 查看 `docs/GIT_GITHUB_SETUP.md` 详细指南
- 查看 `docs/VERSION_MANAGEMENT.md` 版本管理说明
- 使用 `scripts/version_manager.bat` 图形化工具

---

**现在您的项目已经具备了完整的版本管理和 GitHub 管理能力！** 🎉

只需要安装 Git 并创建 GitHub 仓库，就可以开始使用专业的版本控制流程了。
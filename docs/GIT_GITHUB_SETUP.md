# Git 和 GitHub 设置指南

本指南将帮助您设置完整的版本管理环境。

## 第一步：安装 Git

### Windows 系统安装 Git

1. **下载 Git**
   - 访问 [Git官网](https://git-scm.com/download/win)
   - 下载最新版本的 Git for Windows

2. **安装 Git**
   - 运行下载的安装程序
   - 推荐设置：
     - ✅ Use Git from the Windows Command Prompt
     - ✅ Checkout Windows-style, commit Unix-style line endings
     - ✅ Use Windows' default console window

3. **验证安装**
   ```bash
   git --version
   ```

### 配置 Git

```bash
# 设置用户名和邮箱
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱@example.com"

# 设置默认分支名
git config --global init.defaultBranch main

# 设置编辑器（可选）
git config --global core.editor "notepad"
```

## 第二步：创建 GitHub 仓库

### 在 GitHub 上创建仓库

1. **登录 GitHub**
   - 访问 [github.com](https://github.com)
   - 登录您的账户

2. **创建新仓库**
   - 点击右上角的 "+" 按钮
   - 选择 "New repository"
   - 填写仓库信息：
     ```
     Repository name: psychological-test-report-generator
     Description: 心理测试反馈报告自动生成工具
     ✅ Public (或 Private，根据需要)
     ❌ Add a README file (我们已经有了)
     ❌ Add .gitignore (我们已经创建了)
     ✅ Choose a license: MIT License
     ```

3. **获取仓库地址**
   - 创建后会显示仓库的 HTTPS 地址
   - 例如：`https://github.com/username/psychological-test-report-generator.git`

## 第三步：初始化本地仓库

在项目目录中运行以下命令：

```bash
# 初始化 Git 仓库
git init

# 添加远程仓库
git remote add origin https://github.com/username/psychological-test-report-generator.git

# 添加所有文件
git add .

# 创建初始提交
git commit -m "feat: 初始版本 - 心理测试反馈报告生成工具

- ✅ Excel数据读取功能
- ✅ 智能雷达图生成
- ✅ PDF报告自动生成
- ✅ 中文字体支持
- ✅ 批量处理能力
- ✅ 用户友好界面"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 第四步：设置分支保护规则

在 GitHub 仓库中设置分支保护：

1. **进入仓库设置**
   - 点击仓库的 "Settings" 标签
   - 在左侧菜单中选择 "Branches"

2. **添加规则**
   - 点击 "Add rule"
   - Branch name pattern: `main`
   - 启用以下选项：
     - ✅ Require pull request reviews before merging
     - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date before merging
     - ✅ Include administrators

## 第五步：设置 GitHub Actions

我们已经创建了 CI/CD 配置文件，它会自动：
- 在多个 Python 版本上运行测试
- 进行代码质量检查
- 构建可执行文件
- 自动发布版本

## 第六步：日常开发工作流

### 开发新功能

```bash
# 1. 切换到 develop 分支
git checkout -b develop

# 2. 创建功能分支
git checkout -b feature/new-feature

# 3. 开发代码...
# 编辑文件，添加新功能

# 4. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 5. 推送分支
git push origin feature/new-feature

# 6. 在 GitHub 上创建 Pull Request
# 从 feature/new-feature 到 develop
```

### 发布新版本

```bash
# 1. 更新版本信息
# 编辑 version.json，更新版本号
# 编辑 CHANGELOG.md，添加更新记录

# 2. 创建发布分支
git checkout develop
git checkout -b release/1.1.0

# 3. 提交版本更新
git add version.json CHANGELOG.md
git commit -m "chore: 准备发布 v1.1.0"

# 4. 合并到 main
git checkout main
git merge release/1.1.0

# 5. 创建标签
git tag -a v1.1.0 -m "Release version 1.1.0"

# 6. 推送
git push origin main --tags

# 7. 合并回 develop
git checkout develop
git merge release/1.1.0
git push origin develop
```

### 修复紧急问题

```bash
# 1. 从 main 创建热修复分支
git checkout main
git checkout -b hotfix/critical-fix

# 2. 修复问题
# 编辑代码...

# 3. 提交修复
git add .
git commit -m "fix: 修复关键问题描述"

# 4. 合并到 main
git checkout main
git merge hotfix/critical-fix

# 5. 创建补丁版本标签
git tag -a v1.0.1 -m "Hotfix version 1.0.1"

# 6. 推送
git push origin main --tags

# 7. 合并回 develop
git checkout develop
git merge hotfix/critical-fix
git push origin develop
```

## 第七步：GitHub 功能使用

### Issues 管理
- 使用我们创建的 Issue 模板报告 bug 和请求功能
- 为 Issues 添加标签进行分类
- 使用 Milestones 规划版本

### Pull Requests
- 所有代码更改都通过 PR 进行
- 要求代码审查
- 自动运行 CI 检查

### Releases
- 每个版本都创建 GitHub Release
- 上传构建的可执行文件
- 包含详细的更新说明

### Projects (可选)
- 创建项目看板管理任务
- 跟踪开发进度

## 常用 Git 命令速查

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 查看分支
git branch -a

# 切换分支
git checkout branch-name

# 创建并切换分支
git checkout -b new-branch

# 合并分支
git merge branch-name

# 拉取最新代码
git pull origin main

# 推送代码
git push origin branch-name

# 查看差异
git diff

# 撤销更改
git checkout -- filename

# 重置到某个提交
git reset --hard commit-hash
```

## 故障排除

### 常见问题

1. **推送被拒绝**
   ```bash
   git pull origin main --rebase
   git push origin main
   ```

2. **合并冲突**
   ```bash
   # 手动解决冲突后
   git add .
   git commit -m "resolve merge conflict"
   ```

3. **忘记添加文件**
   ```bash
   git add forgotten-file
   git commit --amend --no-edit
   ```

## 下一步

1. **安装 Git** - 按照上述步骤安装 Git
2. **创建 GitHub 仓库** - 在 GitHub 上创建项目仓库
3. **初始化项目** - 运行初始化命令
4. **开始开发** - 使用分支工作流进行开发

---

*如需帮助，请查看 [Git 官方文档](https://git-scm.com/doc) 或 [GitHub 帮助文档](https://docs.github.com/)*
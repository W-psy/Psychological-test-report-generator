# 版本管理指南

本文档介绍如何进行项目的版本管理和发布流程。

## 版本号规范

我们使用 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

```
主版本号.次版本号.修订号 (MAJOR.MINOR.PATCH)
```

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## Git 工作流程

### 1. 分支策略

```
main        # 主分支，稳定版本
├── develop # 开发分支，集成新功能
├── feature/xxx # 功能分支
├── hotfix/xxx  # 热修复分支
└── release/x.x.x # 发布分支
```

### 2. 开发流程

#### 新功能开发
```bash
# 从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 开发完成后合并回develop
git checkout develop
git merge feature/new-feature
git push origin develop
```

#### 发布流程
```bash
# 创建发布分支
git checkout develop
git checkout -b release/1.1.0

# 更新版本信息
# 编辑 version.json
# 更新 CHANGELOG.md

# 合并到main并打标签
git checkout main
git merge release/1.1.0
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main --tags

# 合并回develop
git checkout develop
git merge release/1.1.0
```

#### 热修复流程
```bash
# 从main创建热修复分支
git checkout main
git checkout -b hotfix/1.0.1

# 修复完成后合并到main和develop
git checkout main
git merge hotfix/1.0.1
git tag -a v1.0.1 -m "Hotfix version 1.0.1"
git push origin main --tags

git checkout develop
git merge hotfix/1.0.1
git push origin develop
```

## 版本发布检查清单

### 发布前检查
- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档更新完成
- [ ] CHANGELOG.md 更新
- [ ] version.json 版本号更新
- [ ] 依赖项检查和更新

### 发布步骤
1. **创建发布分支**
   ```bash
   git checkout -b release/x.x.x
   ```

2. **更新版本信息**
   - 更新 `version.json` 中的版本号和发布日期
   - 更新 `CHANGELOG.md` 添加新版本记录

3. **测试验证**
   ```bash
   # 运行所有测试
   python -m pytest
   
   # 构建测试
   pyinstaller --onefile src/main.py
   ```

4. **创建标签和发布**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin main --tags
   ```

5. **GitHub发布**
   - 在GitHub上创建Release
   - 上传构建的可执行文件
   - 添加发布说明

## 自动化工具

### GitHub Actions
项目配置了自动化CI/CD流程：
- 自动测试（多Python版本，多操作系统）
- 代码质量检查
- 自动构建可执行文件
- 自动发布到GitHub Releases

### 本地工具脚本

#### 版本更新脚本
```bash
# 创建 scripts/update_version.py
python scripts/update_version.py 1.1.0
```

#### 构建脚本
```bash
# 创建 scripts/build.py
python scripts/build.py
```

## 版本管理最佳实践

### 1. 提交信息规范
```
type(scope): description

feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建过程或辅助工具的变动
```

### 2. 发布节奏
- **主版本**：每年1-2次重大更新
- **次版本**：每月1-2次功能更新
- **修订版本**：根据需要随时发布

### 3. 向后兼容性
- 主版本可以破坏兼容性
- 次版本必须保持向后兼容
- 修订版本只能修复bug

### 4. 文档维护
- 每次发布都要更新CHANGELOG
- API变更要更新文档
- 重要变更要提供迁移指南

## 紧急发布流程

当需要紧急修复关键bug时：

1. **评估影响**
   - 确定bug的严重程度
   - 评估影响范围

2. **快速修复**
   ```bash
   git checkout main
   git checkout -b hotfix/critical-fix
   # 进行最小化修复
   ```

3. **快速测试**
   - 针对性测试修复的问题
   - 回归测试核心功能

4. **紧急发布**
   ```bash
   git checkout main
   git merge hotfix/critical-fix
   git tag -a v1.0.1 -m "Critical hotfix"
   git push origin main --tags
   ```

## 工具和资源

- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [Git Flow工作流](https://nvie.com/posts/a-successful-git-branching-model/)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

*更多信息请参考项目的 CONTRIBUTING.md 文件*
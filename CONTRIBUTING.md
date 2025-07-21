# 贡献指南

感谢您对心理测试反馈报告生成器项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了bug或有功能建议：

1. 首先搜索 [Issues](https://github.com/your-username/psychological-test-report-generator/issues) 确认问题未被报告
2. 创建新的Issue，请包含：
   - 清晰的问题描述
   - 重现步骤
   - 期望的行为
   - 实际的行为
   - 系统环境信息（Python版本、操作系统等）
   - 相关的错误日志

### 提交代码

1. **Fork 项目**
   ```bash
   # 在GitHub上点击Fork按钮
   git clone https://github.com/your-username/psychological-test-report-generator.git
   cd psychological-test-report-generator
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或者
   git checkout -b bugfix/your-bugfix-name
   ```

3. **开发和测试**
   - 遵循现有的代码风格
   - 添加必要的测试
   - 确保所有测试通过
   - 更新相关文档

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或者
   git commit -m "fix: 修复bug描述"
   ```

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request**
   - 在GitHub上创建Pull Request
   - 填写详细的PR描述
   - 等待代码审查

## 📝 代码规范

### Python代码风格

- 遵循 PEP 8 规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 保持函数简洁，单一职责

### 提交信息规范

使用语义化的提交信息：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: 添加雷达图颜色自定义功能
fix: 修复PDF生成时的字体加载问题
docs: 更新安装说明文档
```

## 🧪 测试

在提交代码前，请确保：

1. 所有现有功能正常工作
2. 新功能有适当的测试覆盖
3. 代码通过基本的质量检查

## 📋 开发环境设置

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/psychological-test-report-generator.git
   cd psychological-test-report-generator
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python src/main.py
   ```

## 🎯 优先级任务

当前我们特别欢迎以下方面的贡献：

- 🐛 Bug修复
- 📚 文档改进
- 🌐 国际化支持
- 🎨 UI/UX改进
- ⚡ 性能优化
- 🧪 测试覆盖率提升

## 💬 交流讨论

- 通过 [Issues](https://github.com/your-username/psychological-test-report-generator/issues) 讨论功能和问题
- 在 [Discussions](https://github.com/your-username/psychological-test-report-generator/discussions) 中进行一般性讨论

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [MIT License](LICENSE) 下授权。

---

再次感谢您的贡献！🎉
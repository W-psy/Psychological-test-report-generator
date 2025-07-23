# 心理测试反馈报告生成器

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.2-orange.svg)](version.json)

专业的心理测评数据分析工具，自动生成包含高质量雷达图的个性化PDF报告。

## ✨ 主要特性

- 🎯 **智能雷达图生成** - 自动生成专业的多维度雷达图
- 📊 **专业PDF报告** - 高质量的个性化测评报告
- 🖼️ **300 DPI高清输出** - 确保打印质量
- 🔄 **批量处理支持** - 一次处理多个测评数据
- 🎨 **中文字体支持** - 完美支持中文显示
- ⚡ **智能数据处理** - 自动识别和处理各种数据格式

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows 10/11 (推荐)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/psychological-test-report-generator.git
   cd psychological-test-report-generator
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动程序**
   
   选择适合的启动方式：
   - **推荐分发版**：双击 `启动程序(完整版-推荐分发).bat`
   - **基本版**：双击 `启动程序(基本版-解决编码问题).bat`
   - **开发环境**：双击 `启动程序(简化版-开发环境).bat`

## 📖 使用说明

详细使用说明请参考 [快速使用指南.md](快速使用指南.md)

### 数据格式要求

数据文件必须包含以下6个基本信息列（顺序可调整）：
- 姓名
- 性别  
- 生日
- 年龄
- 测试日期
- ID

第7列开始为测评项目数据，可自由定义项目名称。

## 📁 项目结构

```
psychological-test-report-generator/
├── src/                          # 源代码
│   ├── main.py                   # 主程序入口
│   ├── report_generator.py       # 报告生成器
│   ├── radar_chart.py           # 雷达图生成
│   └── utils.py                 # 工具函数
├── templates/                    # 模板文件
├── assets/                       # 资源文件
├── logs/                         # 日志文件
├── reports/                      # 生成的报告
├── requirements.txt              # 依赖包列表
├── config.json                   # 配置文件
└── version.json                  # 版本信息
```

## 🔧 配置说明

程序支持通过 `config.json` 进行个性化配置：

- 雷达图样式设置
- 字体配置
- 输出格式设置
- 数据处理参数

## 📝 更新日志

### v1.0.2 (2025-07-23)
- ✅ **自定义文件名功能** - 支持ID号和姓名两种命名模式
- ✅ **灵活命名配置** - 用户可自定义文件名中间部分内容
- ✅ **智能文件名生成** - 自动处理特殊字符和文件名冲突
- ✅ **增强用户界面** - 新增文件命名设置区域
- 📝 **文档更新** - 针对GUI软件使用方式更新所有文档

### v1.0.1 (2025-07-22)
- ✅ **扩展评分模式** - 新增6档和7档评分模式支持
- ✅ **多列配置支持** - 支持12列（6档）和14列（7档）Excel配置
- ✅ **自定义结果说明** - 支持用户自定义结果声明文本
- 📝 **完善文档** - 更新支持2-7档评分模式说明

### v1.0.0 (2025-07-21)
- 🎉 初始版本发布
- ✅ 支持Excel数据读取
- ✅ 高质量雷达图生成
- ✅ PDF报告自动生成
- ✅ 智能基准线定位
- ✅ 300 DPI高清输出
- ✅ 中文字体完美支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 技术支持

如果您在使用过程中遇到问题，请：

1. 查看 [常见问题](README.md#常见问题)
2. 检查 [Issues](https://github.com/your-username/psychological-test-report-generator/issues)
3. 提交新的 Issue

## 📊 统计信息

![GitHub stars](https://img.shields.io/github/stars/your-username/psychological-test-report-generator?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/psychological-test-report-generator?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/psychological-test-report-generator)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
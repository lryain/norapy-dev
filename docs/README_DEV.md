# OpenVoiceOS 开发模式 - 完整指南索引

## 📋 概述

这套完整的开发模式指南包含了从零启动 OpenVoiceOS 系统所需的所有资源。无需运行冗长的安装脚本，只需要按照指南逐步启动各个组件。

## 📁 文档结构

```
/home/pi/dev/norapy-dev/
├── docs/
│   ├── QUICKSTART.md          ← 📌 从这里开始！快速参考卡片
│   ├── DEVELOPMENT.md         ← 详细的开发指南
│   ├── ARCHITECTURE.md        ← 系统架构深度分析
│   └── README_DEV.md          ← 本文档
├── bin/
│   └── ovos-dev               ← 自动化启动脚本
└── engine/
    ├── engine-core/
    │   ├── ovos-core/         ← OVOS 主程序入口
    │   ├── ovos-messagebus/   ← 消息总线
    │   ├── ovos-config/       ← 配置系统
    │   ├── ovos-plugin-manager/
    │   ├── ovos-audio/
    │   └── ovos-workshop/
    └── ...其他组件
```

## 🚀 快速开始 (3 步，5 分钟)

### 步骤 1: 阅读快速参考
```bash
cat docs/QUICKSTART.md
```

### 步骤 2: 设置开发环境
```bash
cd engine
python3 -m venv venv
source venv/bin/activate
pip install -e ./engine-core/{ovos-core,ovos-messagebus,ovos-config,ovos-plugin-manager}
```

### 步骤 3: 启动 OVOS
```bash
# 方式 A: 自动启动（推荐）
./bin/ovos-dev

# 方式 B: 手动启动
python3 -m ovos_messagebus.service &  # 终端 1
ovos-core                              # 终端 2
```

## 📚 文档内容详解

### 1. **QUICKSTART.md** (快速参考卡片)
**适合**: 已了解 OVOS 或需要快速参考的开发者

包含:
- ✅ 30 秒快速启动命令
- ✅ 核心组件位置和依赖关系
- ✅ 常用命令速查表
- ✅ 常见问题 FAQ
- ✅ 开发 vs 生产环境对比

**何时查看**: 
- 第一次快速设置
- 忘记命令时
- 快速参考检查表

### 2. **DEVELOPMENT.md** (完整开发指南)
**适合**: 全新开始或需要详细步骤的开发者

包含:
- ✅ 架构概述和核心组件说明
- ✅ 分步环境搭建指南
- ✅ 最小化配置说明
- ✅ 启动流程的详细解释
- ✅ 完整启动脚本示例
- ✅ 开发工作流程 (技能/插件开发)
- ✅ 调试模式配置
- ✅ 完整故障排查指南

**何时查看**:
- 第一次详细了解 OVOS
- 需要理解各组件功能
- 遇到问题需要深入调试
- 学习如何开发新技能/插件

### 3. **ARCHITECTURE.md** (架构深度分析)
**适合**: 想要深入理解系统设计的开发者

包含:
- ✅ 完整的系统架构图
- ✅ 启动序列流程图
- ✅ 进程模型说明
- ✅ 核心模块职责详解
- ✅ 配置系统层级
- ✅ 技能生命周期详细步骤
- ✅ 意图识别完整流程
- ✅ 代码入口点位置
- ✅ 扩展点和自定义方法

**何时查看**:
- 想要深入理解系统工作原理
- 开发复杂的定制功能
- 贡献代码到核心项目
- 性能优化和调试

## 🛠️ 启动脚本 (bin/ovos-dev)

**目的**: 自动化完整的环境设置和服务启动

### 功能特性
- ✅ 自动创建虚拟环境
- ✅ 自动安装依赖
- ✅ 自动生成配置文件
- ✅ 自动启动消息总线
- ✅ 自动启动 OVOS 核心
- ✅ 多语言支持
- ✅ 调试模式支持
- ✅ 进程清理工具

### 使用方法

```bash
# 基本使用（启动所有服务）
./bin/ovos-dev

# 仅设置环境，不启动服务
./bin/ovos-dev --setup-only

# 启动中文版本
./bin/ovos-dev --language zh-cn

# 调试模式（详细日志）
./bin/ovos-dev --verbose

# 清理缓存后启动
./bin/ovos-dev --clean

# 杀死所有 OVOS 进程
./bin/ovos-dev --kill

# 显示帮助
./bin/ovos-dev --help
```

## 🏗️ 入口程序分析

### 问题：engine/engine-core/ovos-core 可以作为入口程序吗？

**答案**: ✅ **YES**，它是 OVOS 的主程序入口。

### 进程启动链

```
用户命令: ovos-core
    ↓
setup.py entry_points:
    'console_scripts': 'ovos-core=ovos_core.__main__:main'
    ↓
执行: ovos_core/__main__.py::main()
    ├─ 初始化日志系统
    ├─ 设置国际化
    ├─ 连接消息总线
    ├─ 启动 SkillManager
    │   ├─ 发现技能
    │   ├─ 加载插件
    │   ├─ 启动意图服务
    │   └─ 进入监听循环
    └─ 等待退出信号
```

### 依赖组件

OVOS 启动需要:
1. **消息总线** (独立进程)
   - 命令: `python3 -m ovos_messagebus.service`
   - 端口: 8181
   - 用途: 所有组件间的通信

2. **配置文件**
   - 位置: `~/.config/mycroft/mycroft.conf`
   - 格式: JSON
   - 必需: 最小化字段 (language, stt, tts)

3. **插件** (可选)
   - STT: 语音识别
   - TTS: 语音合成
   - VAD: 语音活动检测
   - 唤醒词: 热词检测

## 🎯 生产 vs 开发对比

### 生产环境 (使用 ovos-installer)

```bash
# 长时间运行安装脚本
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/OpenVoiceOS/ovos-installer/main/installer.sh)"

特点:
- ✓ 使用 Ansible 自动化安装
- ✓ 配置 systemd 服务
- ✓ 完整系统集成
- ✓ 自动依赖处理
- ✓ 支持多种硬件
- ✓ 自动更新机制
```

### 开发环境 (本指南)

```bash
# 快速启动脚本
./bin/ovos-dev

特点:
- ✓ 快速设置 (< 5分钟)
- ✓ 完全可编辑的代码 (pip -e)
- ✓ 手动进程管理 (易于调试)
- ✓ 最小化依赖
- ✓ 快速迭代开发
- ✗ 不包含系统集成
- ✗ 无自动重启机制
```

## 💡 推荐工作流程

### 开发新技能

```bash
# 1. 查看快速参考
cat docs/QUICKSTART.md

# 2. 启动 OVOS
./bin/ovos-dev

# 3. 创建技能骨架
ovos-create-skill

# 4. 复制到技能目录
cp -r my-skill ~/.local/share/mycroft/skills/

# 5. 自动加载并测试
# OVOS 会自动加载技能

# 6. 修改代码，重启 OVOS
./bin/ovos-dev --kill
./bin/ovos-dev
```

### 开发新插件

```bash
# 1. 查看架构文档了解扩展点
cat docs/ARCHITECTURE.md | grep "扩展点"

# 2. 启动 OVOS
./bin/ovos-dev

# 3. 开发插件代码
# engine/engine-plugins/my-plugin/

# 4. 安装插件（开发模式）
cd engine
pip install -e ./engine-plugins/my-plugin

# 5. 配置插件
# 编辑 ~/.config/mycroft/mycroft.conf

# 6. 重启 OVOS
./bin/ovos-dev --kill && ./bin/ovos-dev
```

### 调试问题

```bash
# 1. 启用调试模式
./bin/ovos-dev --verbose

# 2. 查看详细日志
tail -f ~/.local/share/mycroft/logs/skills.log

# 3. 查看消息总线流量
export OVOS_LOG_LEVEL=DEBUG

# 4. 参考故障排查
cat docs/DEVELOPMENT.md | grep -A 20 "故障排查"
```

## 📖 学习路径

### 初级开发者
1. ✅ 阅读 QUICKSTART.md (5 min)
2. ✅ 运行 `./bin/ovos-dev` (2 min)
3. ✅ 验证系统运行 (2 min)
4. ✅ 开始开发技能

### 中级开发者
1. ✅ 阅读 DEVELOPMENT.md (20 min)
2. ✅ 理解配置系统
3. ✅ 开发插件
4. ✅ 理解消息总线通信

### 高级开发者
1. ✅ 研究 ARCHITECTURE.md (30 min)
2. ✅ 分析核心代码流程
3. ✅ 贡献到 OVOS 核心
4. ✅ 优化性能和扩展能力

## 🔗 相关资源

### 项目结构
- 主仓库: `/home/pi/dev/norapy-dev/`
- 引擎目录: `engine/`
- 文档目录: `docs/`
- 启动脚本: `bin/ovos-dev`

### OVOS 官方
- 官方文档: https://openvoiceos.github.io/
- GitHub 组织: https://github.com/OpenVoiceOS/
- 社区论坛: https://community.openconversational.ai/
- 安装程序: https://github.com/OpenVoiceOS/ovos-installer

### 核心组件
- ovos-core: 技能管理和意图服务
- ovos-messagebus: 消息总线和 IPC
- ovos-config: 配置管理系统
- ovos-plugin-manager: 插件系统

## ✅ 验证清单

启动前检查列表:
- [ ] Python 3.9+ 已安装
- [ ] Git 已安装
- [ ] 虚拟环境已创建 (或让脚本自动创建)
- [ ] 配置文件已准备 (或让脚本自动生成)
- [ ] 消息总线端口 (8181) 未被占用
- [ ] 有足够的磁盘空间 (~500MB)

## 🆘 获取帮助

### 快速问题
查看 docs/QUICKSTART.md 的 FAQ 部分

### 常见问题
参考 docs/DEVELOPMENT.md 的故障排查部分

### 深度问题
研究 docs/ARCHITECTURE.md 了解系统工作原理

### 官方支持
访问 OVOS 社区论坛或 GitHub Issues

## 📝 文档维护

这些文档是根据 OVOS 项目结构和开发实践编写的。

如需更新：
1. 修改对应的 .md 文件
2. 测试更改流程
3. 提交 PR 到项目

---

**最后更新**: 2025-10-18  
**版本**: 1.0  
**维护者**: OVOS 开发团队

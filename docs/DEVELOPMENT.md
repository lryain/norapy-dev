# OpenVoiceOS 开发模式快速启动指南

本文档提供在开发模式下快速启动和运行 OpenVoiceOS (OVOS) 的最精简方案，适合开发者进行本地开发和测试。

## 架构概述

OVOS 系统采用模块化架构，核心组件包括：

```
┌─────────────────────────────────────────────────────┐
│         OpenVoiceOS 核心架构                          │
├─────────────────────────────────────────────────────┤
│  [消息总线]  ←→  [技能管理]  ←→  [意图服务]          │
│  (Message    (Skill         (Intent                  │
│   Bus)       Manager)       Services)                │
│    ↓             ↓               ↓                   │
│ [插件系统]   [配置管理]      [STT/TTS/VAD]           │
│ (OPM)       (Config)        (Pipeline Plugins)       │
└─────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 路径 | 功能 |
|------|------|------|
| **ovos-core** | `engine/engine-core/ovos-core` | 技能管理、意图服务、消息总线连接 |
| **ovos-messagebus** | `engine/engine-core/ovos-messagebus` | 核心消息总线（进程间通信） |
| **ovos-plugin-manager** | `engine/engine-core/ovos-plugin-manager` | 插件系统 (OPM) |
| **ovos-config** | `engine/engine-core/ovos-config` | 配置管理系统 |
| **ovos-audio** | `engine/engine-core/ovos-audio` | 音频播放和录制 |
| **ovos-workshop** | `engine/engine-core/ovos-workshop` | 技能开发框架 |

### 入口程序分析

**主入口**: `ovos-core/__main__.py::main()`

```python
# 核心流程
1. 初始化日志系统 → init_service_logger("skills")
2. 设置国际化配置 → setup_locale()
3. 连接消息总线 → MessageBusClient()
4. 启动技能管理器 → SkillManager()
5. 等待退出信号 → wait_for_exit_signal()
6. 清理资源 → skill_manager.shutdown()
```

**Console 入口点** (setup.py 中定义):
- `ovos-core` → `ovos_core.__main__:main` (主程序)
- `ovos-intent-service` → `ovos_core.intent_services.service:launch_standalone` (独立意图服务)
- `ovos-skill-installer` → `ovos_core.skill_installer:launch_standalone` (技能安装器)

## 开发模式快速启动

### 前置需求

```bash
# Python 3.9 或更高版本
python3 --version

# 系统依赖（Ubuntu/Debian）
sudo apt-get install -y \
    build-essential \
    python3-dev \
    portaudio19-dev \
    pulseaudio \
    git
```

### 1. 环境搭建 (5分钟)

```bash
cd /home/pi/dev/norapy-dev/engine

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级包管理工具
pip install --upgrade pip setuptools wheel

# 安装核心组件（开发模式）
pip install -e ./engine-core/ovos-core
pip install -e ./engine-core/ovos-messagebus
pip install -e ./engine-core/ovos-config
pip install -e ./engine-core/ovos-plugin-manager
pip install -e ./engine-core/ovos-audio
pip install -e ./engine-core/ovos-workshop

# 可选：安装基础技能和插件
pip install -e ./engine-plugins/ovos-ww-plugin-precise-lite
pip install -e ./engine-plugins/ovos-vad-plugin-silero
```

### 2. 配置OVOS (3分钟)

创建最小化配置文件 `~/.config/mycroft/mycroft.conf`:

```json
{
  "language": "en-us",
  "locale": "en-US",
  "system_unit": "metric",
  "time_format": "full",
  "date_format": "full",
  
  "server": {
    "metrics": false,
    "metrics_port": 13579,
    "port": 8181
  },
  
  "audio": {
    "default-backend": "mpv",
    "backends": {
      "mpv": {
        "active": true
      }
    }
  },
  
  "skills": {
    "auto_update": false,
    "installer": "pip"
  },
  
  "stt": {
    "module": "ovos-stt-plugin-chromium"
  },
  
  "tts": {
    "module": "ovos-tts-plugin-piper",
    "ovos-tts-plugin-piper": {
      "voice": "en_US-ljspeech-medium"
    }
  }
}
```

### 3. 启动消息总线 (1分钟)

OVOS 需要一个运行中的消息总线：

**终端 1 - 启动消息总线**:
```bash
source venv/bin/activate

# 启动消息总线服务
python3 -m ovos_messagebus.service
# 应该看到: "Bus service loaded successfully"
```

### 4. 启动 OVOS (1分钟)

**终端 2 - 启动 OVOS 技能管理器**:
```bash
cd /home/pi/dev/norapy-dev/engine
source venv/bin/activate

# 启动 OVOS 核心
ovos-core

# 或使用 Python 模块方式
python3 -m ovos_core

# 可选参数
ovos-core --disable-intent-service      # 禁用意图服务
ovos-core --disable-skill-api           # 禁用技能 API
ovos-core --disable-file-watcher        # 禁用文件监视
```

### 5. 加载技能 (可选)

**终端 3 - 安装/测试技能**:
```bash
source venv/bin/activate

# 安装技能（通过技能管理器 API）
ovos-skill-installer /path/to/skill

# 或手动复制技能到技能目录
# ~/.local/share/mycroft/skills/
```

## 完整启动脚本

创建 `start_dev.sh`:

```bash
#!/bin/bash

# 开发模式启动脚本
set -e

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="$PROJECT_ROOT/engine/venv"
LOG_DIR="$PROJECT_ROOT/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  OpenVoiceOS Development Mode - Startup Script${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"

# 1. 检查虚拟环境
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd "$PROJECT_ROOT/engine"
    python3 -m venv venv
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip setuptools wheel
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✓ Virtual environment loaded${NC}"
fi

# 2. 启动消息总线
echo -e "${YELLOW}Starting message bus...${NC}"
cd "$PROJECT_ROOT/engine"
python3 -m ovos_messagebus.service > "$LOG_DIR/messagebus.log" 2>&1 &
MB_PID=$!
echo -e "${GREEN}✓ Message bus started (PID: $MB_PID)${NC}"

sleep 2

# 3. 检查消息总线连接
if ! nc -z localhost 8181 2>/dev/null; then
    echo -e "${RED}✗ Message bus failed to start${NC}"
    kill $MB_PID 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✓ Message bus is listening on port 8181${NC}"

# 4. 启动 OVOS 核心
echo -e "${YELLOW}Starting OVOS core...${NC}"
cd "$PROJECT_ROOT/engine"
ovos-core > "$LOG_DIR/ovos-core.log" 2>&1 &
CORE_PID=$!
echo -e "${GREEN}✓ OVOS core started (PID: $CORE_PID)${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  OpenVoiceOS is running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Process IDs:"
echo "  - Message Bus: $MB_PID"
echo "  - OVOS Core:   $CORE_PID"
echo ""
echo "Logs:"
echo "  - $LOG_DIR/messagebus.log"
echo "  - $LOG_DIR/ovos-core.log"
echo ""
echo "To stop, press Ctrl+C or run:"
echo "  kill $MB_PID $CORE_PID"
echo ""

# 等待 Ctrl+C
trap "kill $MB_PID $CORE_PID 2>/dev/null; echo 'OVOS stopped.'" INT TERM

wait
```

使用方法:
```bash
chmod +x start_dev.sh
./start_dev.sh
```

## 最小化配置要点

| 配置项 | 说明 | 开发建议 |
|------|------|---------|
| **language** | 系统语言 | `zh-cn` 或 `en-us` |
| **auto_update** | 自动更新技能 | `false` (开发模式) |
| **metrics** | 性能指标 | `false` (开发阶段) |
| **STT/TTS** | 语音识别/合成 | 选择轻量级本地模块 |

## 开发工作流程

### 开发新技能

```bash
# 1. 使用框架创建技能结构
ovos-create-skill

# 2. 放到技能目录
mkdir -p ~/.local/share/mycroft/skills/
cp -r my-skill ~/.local/share/mycroft/skills/

# 3. OVOS 会自动检测并加载
# 查看日志: tail -f ~/.local/share/mycroft/logs/skills.log
```

### 开发新插件

```bash
# 1. 在 engine 中创建插件
pip install -e ./engine-plugins/my-plugin

# 2. 配置插件
# 编辑 ~/.config/mycroft/mycroft.conf 添加插件配置

# 3. 重启 OVOS
```

### 调试模式

```bash
# 启用详细日志
export OVOS_LOG_LEVEL=DEBUG

# 启用特定组件日志
export OVOS_LOG_COMPONENTS=core,skills,intent

# 重启 OVOS
ovos-core
```

## 故障排查

### 消息总线无法连接
```bash
# 检查端口是否被占用
lsof -i :8181

# 清除旧的消息总线进程
pkill -f ovos_messagebus

# 重启消息总线
python3 -m ovos_messagebus.service
```

### 技能无法加载
```bash
# 检查技能目录
ls -la ~/.local/share/mycroft/skills/

# 查看技能日志
tail -f ~/.local/share/mycroft/logs/skills.log

# 验证技能的 setup.py
python3 setup.py develop
```

### 配置文件问题
```bash
# 验证配置文件语法
python3 -c "import json; json.load(open('~/.config/mycroft/mycroft.conf'))"

# 重置为默认配置
rm ~/.config/mycroft/mycroft.conf
# OVOS 会生成默认配置
```

## 与生产环境的区别

| 方面 | 开发模式 | 生产环境 (installer) |
|------|---------|-------------------| 
| **安装方式** | `pip install -e` (可编辑) | Ansible + 虚拟环境 |
| **服务管理** | 手动启动 | systemd 单元文件 |
| **更新策略** | 手动 `git pull` | 自动检查更新 |
| **系统集成** | 无 | 完整的系统集成 |
| **配置位置** | `~/.config/mycroft/` | `/etc/ovos/` 或用户目录 |

## 下一步

- 📚 查看 [OVOS 技能开发文档](https://openvoiceos.github.io/community-docs/)
- 🔌 了解 [插件系统架构](https://openvoiceos.github.io/community-docs/plugins/)
- 💬 加入 [OVOS 社区论坛](https://community.openconversational.ai/)

## 参考资源

- **官方文档**: https://openvoiceos.github.io/
- **GitHub 仓库**: https://github.com/OpenVoiceOS/
- **社区论坛**: https://community.openconversational.ai/

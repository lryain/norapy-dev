# OpenVoiceOS 开发模式 - 快速参考卡片

## 🚀 30 秒快速启动

```bash
# 前置准备（仅首次）
cd /home/pi/dev/norapy-dev/engine
python3 -m venv venv
source venv/bin/activate
pip install -e ./engine-core/{ovos-core,ovos-messagebus,ovos-config,ovos-plugin-manager}

# 启动（每次使用）
source venv/bin/activate
python3 -m ovos_messagebus.service &  # 终端1
sleep 2
ovos-core                              # 终端2
```

## 核心组件位置

```
engine/
├── engine-core/
│   ├── ovos-core/               ← 技能管理器（主程序入口）
│   ├── ovos-messagebus/         ← 消息总线（进程间通信）
│   ├── ovos-config/             ← 配置管理
│   ├── ovos-plugin-manager/     ← 插件系统
│   ├── ovos-audio/              ← 音频播放/录制
│   └── ovos-workshop/           ← 技能开发框架
├── engine-plugins/              ← 插件（STT/TTS/VAD/唤醒词）
├── engine-skills/               ← 内置技能
├── engine-utils/                ← 工具库
└── engine-servers/              ← 服务（可选）
```

## 入口程序

| 命令 | 来源 | 功能 |
|------|------|------|
| `ovos-core` | `ovos_core/__main__.py` | **主程序** - 技能管理器 |
| `ovos-intent-service` | `ovos_core/intent_services/service.py` | 独立意图服务 |
| `ovos-skill-installer` | `ovos_core/skill_installer.py` | 技能安装器 |

## 必需的依赖组件

```bash
# 最小化安装（仅核心功能）
pip install -e ./engine-core/ovos-core
pip install -e ./engine-core/ovos-messagebus
pip install -e ./engine-core/ovos-config
pip install -e ./engine-core/ovos-plugin-manager

# 推荐安装（完整体验）
pip install -e ./engine-core/ovos-audio        # 音频支持
pip install -e ./engine-core/ovos-workshop     # 技能框架
pip install -e ./engine-plugins/ovos-ww-plugin-precise-lite  # 唤醒词
pip install -e ./engine-plugins/ovos-vad-plugin-silero       # 语音活动检测
```

## 启动顺序

```
Step 1: 消息总线 (Message Bus)
  ↓
  python3 -m ovos_messagebus.service
  端口: 8181
  
Step 2: OVOS 核心 (OVOS Core)
  ↓
  ovos-core
  
Optional: 技能/插件
  ↓
  自动加载或手动安装
```

## 配置最小化需求

```json
{
  "language": "zh-cn",
  "stt": {"module": "ovos-stt-plugin-chromium"},
  "tts": {"module": "ovos-tts-plugin-piper"},
  "audio": {"default-backend": "mpv"},
  "skills": {"auto_update": false}
}
```

## 常用命令

```bash
# 检查消息总线
nc -z localhost 8181 && echo "✓ 运行中" || echo "✗ 未运行"

# 查看日志
tail -f ~/.local/share/mycroft/logs/skills.log

# 清理缓存
rm -rf ~/.local/share/mycroft/cache/*

# 调试模式
export OVOS_LOG_LEVEL=DEBUG && ovos-core

# 停止所有进程
pkill -f ovos
pkill -f messagebus
```

## 开发模式 vs 生产环境

| 特性 | 开发模式 | 生产环境 |
|------|---------|---------|
| 安装 | 可编辑 (`-e`) | 固定版本 |
| 服务管理 | 手动 | systemd |
| 自动更新 | ❌ | ✓ |
| 快速迭代 | ✓ | - |

## 文件位置

```
~/.config/mycroft/mycroft.conf      ← 全局配置
~/.local/share/mycroft/skills/       ← 技能目录
~/.local/share/mycroft/logs/         ← 日志目录
~/.local/share/mycroft/cache/        ← 缓存目录
```

## 常见问题

### Q: 消息总线连接失败？
```bash
pkill -f messagebus
python3 -m ovos_messagebus.service
```

### Q: 技能无法加载？
```bash
# 检查技能目录
ls -la ~/.local/share/mycroft/skills/
# 查看错误日志
tail -f ~/.local/share/mycroft/logs/skills.log
```

### Q: 修改代码后如何重新加载？
```bash
# 重启 OVOS
pkill -f ovos-core
ovos-core
```

### Q: 如何切换语言？
编辑 `~/.config/mycroft/mycroft.conf`:
```json
{"language": "zh-cn"}
```
重启 OVOS

## 相关文档

- 详细指南: [DEVELOPMENT.md](./DEVELOPMENT.md)
- OVOS 官方文档: https://openvoiceos.github.io/
- GitHub 仓库: https://github.com/OpenVoiceOS/

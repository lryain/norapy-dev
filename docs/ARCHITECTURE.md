# OpenVoiceOS 架构与启动流程

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input Layer                          │
│  [语音]  [文本]  [按钮]  [Web UI]  [CLI]                     │
└────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Message Bus (ovos-messagebus)                   │
│              Port 8181 (WebSocket based)                     │
│                                                               │
│  统一的进程间通信(IPC)层 - 所有组件通过消息通信              │
└────────────────────────────────────────────────────────────┘
         ↓                 ↓                 ↓
    ┌────────┐        ┌─────────┐      ┌──────────┐
    │ Skill  │        │ Intent  │      │ Plugin   │
    │Manager │        │ Service │      │ Manager  │
    │        │        │         │      │          │
    └────────┘        └─────────┘      └──────────┘
         ↓                 ↓                 ↓
    技能加载/执行  意图识别/匹配  插件(STT/TTS/VAD等)
```

## 启动序列图

```
Time  Component              Action
─────────────────────────────────────────────────────────
  T0  Message Bus            启动 (Port 8181)
      │
      ├─→ EventBus          初始化事件系统
      ├─→ Configuration      加载配置
      └─→ ServiceBus        准备服务层
      
  T1  OVOS Core             启动技能管理器
      │
      ├─→ Connect to Bus    连接到消息总线
      ├─→ Intent Service    启动意图服务
      ├─→ Skill Manager     初始化技能管理器
      ├─→ Plugin System     加载插件
      └─→ Ready Signal      发送 'system.ready' 信号
      
  T2  Skills                自动加载技能
      │
      ├─→ Discover          扫描技能目录
      ├─→ Initialize        初始化每个技能
      ├─→ Register          向意图服务注册意图
      └─→ Ready Callback    执行 skill_ready() 方法
      
  T3  System Stable         系统就绪，等待用户输入
```

## 进程模型

### 核心进程

```
┌─────────────────────────────────────────┐
│     Message Bus Process                  │
│  (ovos-messagebus-service)              │
│  ├─ EventBus                            │
│  └─ ServiceBus                          │
└─────────────────────────────────────────┘
           ↑  ↓  ↑  ↓
┌──────────────────────────────────────────┐
│   OVOS Core Process                       │
│   (ovos-core / SkillManager)             │
│   ├─ Intent Service                      │
│   ├─ Skill Manager                       │
│   ├─ Configuration                       │
│   └─ Plugin Manager                      │
└──────────────────────────────────────────┘
           ↑  ↓  ↑  ↓
   ┌───────┴──┴──┴──┴──────┐
   │  Loaded Skills/Plugins  │
   │  (可选单独进程)         │
   └───────────────────────┘
```

## 核心模块职责

### 1. Message Bus (消息总线)
- **职责**: 所有组件间的异步消息通信
- **技术**: WebSocket 服务器
- **端口**: 8181 (默认)
- **消息类型**: 
  - `mycroft.` - 系统事件
  - `skill.` - 技能事件
  - `plugin.` - 插件事件

### 2. Skill Manager (技能管理器)
- **职责**: 
  - 发现和加载技能
  - 管理技能生命周期
  - 处理意图和触发技能
  - 提供 Skill API
- **关键类**: `SkillManager` (在 `skill_manager.py`)
- **启动函数**: `main()` (在 `__main__.py`)

### 3. Intent Service (意图服务)
- **职责**:
  - 协调意图识别管道
  - 管理多个意图识别器 (adapt, padatious 等)
  - 处理 STT 输出
  - 调度意图到相应技能
- **管道插件**: 
  - Adapt (Keyword matching)
  - Padatious (Machine learning)
  - Fallback (最后尝试)

### 4. Plugin Manager (插件管理器)
- **职责**:
  - 发现和加载插件
  - 管理插件配置
  - 提供 OPM (OVOS Plugin Manager) 接口
- **插件类型**:
  - STT (Speech-to-Text)
  - TTS (Text-to-Speech)
  - VAD (Voice Activity Detection)
  - Wake Word
  - Audio Backend

## 配置系统

```
ovos-config (ovos_core.config)
│
├─ Config Source Hierarchy:
│  1. Command Line Arguments (最高优先级)
│  2. Environment Variables
│  3. ~/.config/mycroft/mycroft.conf
│  4. /etc/mycroft/mycroft.conf
│  5. Hardcoded Defaults (最低)
│
└─ Configuration Sections:
   ├─ language & locale
   ├─ audio (playback backend)
   ├─ stt (speech recognition)
   ├─ tts (speech synthesis)
   ├─ skills (skill system config)
   ├─ plugins (plugin config)
   └─ server (web service config)
```

## 技能生命周期

```
┌─────────────────────────────────────────────────┐
│ 1. Discovery (发现)                             │
│    - 扫描 ~/.local/share/mycroft/skills/        │
│    - 识别有效的技能目录 (包含 __init__.py)      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 2. Initialization (初始化)                       │
│    - 导入技能模块                                │
│    - 创建技能类实例                              │
│    - 设置事件监听器                              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 3. Registration (注册)                           │
│    - 向意图服务注册意图                          │
│    - 添加 intent handlers 到总线                 │
│    - 标记为 "loaded"                            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 4. Active (活跃)                                 │
│    - 监听总线事件                                │
│    - 响应用户意图                                │
│    - 动态加载新代码 (可选文件监视)              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 5. Shutdown (关闭)                               │
│    - 调用 skill.shutdown()                       │
│    - 清理资源                                    │
│    - 反注册意图处理程序                          │
└─────────────────────────────────────────────────┘
```

## 意图识别流程

```
Voice Input / Text Input
        ↓
    [STT Plugin]  (如果是语音)
        ↓
   Parsed Text
        ↓
  ┌─────────────────────────────┐
  │ Intent Pipeline             │
  │                             │
  │ ┌───────────────────────┐   │
  │ │ Adapt Matcher         │   │  关键字匹配
  │ │ (keyword, regex)      │   │
  │ └───────────────────────┘   │
  │           ↓ (if no match)   │
  │ ┌───────────────────────┐   │
  │ │ Padatious Classifier  │   │  ML-based
  │ │ (neural network)      │   │
  │ └───────────────────────┘   │
  │           ↓ (if no match)   │
  │ ┌───────────────────────┐   │
  │ │ Fallback Handlers     │   │  最后尝试
  │ │                       │   │
  │ └───────────────────────┘   │
  └─────────────────────────────┘
        ↓
  Matched Intent
        ↓
  [Invoke Skill Handler]
        ↓
  Response Text
        ↓
  [TTS Plugin]  (text-to-speech)
        ↓
  Spoken Response
```

## 开发模式关键差异

### vs. 生产环境

| 方面 | 开发模式 | 生产环境 |
|------|---------|---------|
| **组件来源** | 本地源码 (`pip -e`) | 打包版本 (PyPI) |
| **进程管理** | 手动启动 | systemd 服务 |
| **代码更新** | 立即有效 | 需重装 |
| **日志级别** | 可设 DEBUG | 通常 INFO |
| **单点故障** | 手动恢复 | 自动重启 |
| **访问权限** | 用户级别 | 混合 (用户+root) |

## 启动命令映射

| 用户命令 | Entry Point | 源代码位置 | 功能 |
|---------|------------|----------|------|
| `ovos-core` | `console_scripts` | `setup.py` | 主程序 |
|  | ↓ | ↓ | ↓ |
|  | `ovos_core.__main__:main` | `ovos_core/__main__.py` | 技能管理 |
|  | ↓ | ↓ | ↓ |
|  | `SkillManager()` | `ovos_core/skill_manager.py` | 核心类 |
|  | ↓ | ↓ | ↓ |
|  | `.start()` | 异步启动流程 | 初始化系统 |

## 调试入口点

### 添加调试代码

```python
# 在 ovos_core/__main__.py 中
from ovos_core.skill_manager import SkillManager

def main(...):
    # 这里添加 breakpoint 或日志
    
    import pdb; pdb.set_trace()  # 调试断点
    
    skill_manager = SkillManager(bus, ...)
    skill_manager.start()
```

### 跟踪消息流

```bash
# 在不同终端查看消息总线流量
export OVOS_LOG_LEVEL=DEBUG
python3 -m ovos_messagebus.service
```

## 扩展点

### 1. 自定义技能
```python
# 继承 OVOSSkill 框架
class MySkill(OVOSSkill):
    def initialize(self):
        self.add_event_listener('mycroft.ready', self.on_ready)
    
    def on_ready(self):
        self.add_event_listener('recognizer_loop:utterance', self.handle_utterance)
    
    def handle_utterance(self, message):
        # 处理用户输入
        pass
```

### 2. 自定义插件
```python
# 实现 STT/TTS/VAD 插件接口
class MySTTPlugin:
    def execute(self, audio_data, language):
        # 执行 STT
        return text
```

### 3. 自定义意图
```python
# 添加到技能中
@skill_instance.intent_handler('play music')
def handle_play_music(self, message):
    # 处理 "play music" 意图
    pass
```

## 相关文件

- **主程序**: `engine/engine-core/ovos-core/ovos_core/__main__.py`
- **技能管理**: `engine/engine-core/ovos-core/ovos_core/skill_manager.py`
- **意图服务**: `engine/engine-core/ovos-core/ovos_core/intent_services/service.py`
- **配置系统**: `engine/engine-core/ovos-config/`
- **消息总线**: `engine/engine-core/ovos-messagebus/`
- **插件系统**: `engine/engine-core/ovos-plugin-manager/`

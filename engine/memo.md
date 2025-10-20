# 库备注

## 核心
- ovos-core - OpenVoiceOS Core, the FOSS Artificial Intelligence platform. 
- ovos-gui - ovos-core metapackage for gui daemon 
- ovos_PHAL - Plugin based Hardware Abstraction Layer
- ovos-audio - OpenVoiceOS audio output daemon
- ovos-messagebus - ovos-core bus daemon 
- ovos-dinkum-listener - ovos-listener based on the voice loop from mycroft-dinkum 
## 核心库依赖
- ovos-workshop - frameworks, templates and patches for the OpenVoiceOS universe 
- ovos-plugin-manager - OPM can be used to load and create plugins for the OpenVoiceOS ecosystem!
- ovos-config - OVOS configuration manager library
- ovos_utils - collection of simple utilities for use across the mycroft ecosystem
- ovos-bus-client
- ovos-m2v-pipeline - An intent matching(classification) pipeline for OpenVoiceOS 位于：TigreGotico库中

## 服务 核心概念：
    Media Service
    OCP Skills
    OCP Pipeline
- ovos-media - Media playback service for OpenVoiceOS

## 插件
- ovos-openai-plugin - OpenAI API plugin for OpenVoiceOS
- ovos-solver-failure-plugin - OVOS Failure Solver Plugin
- ovos-utterance-corrections-plugin - 此插件提供了用于纠正或调整语音转文本（STT）输出的工具，以实现更好的意图匹配或改善用户体验。
- ovos-utterance-plugin-cancel - 插件来查看转录短语的尾端，如果它以“nevermind that”或“cancel it”或“ignore that”结束，则忽略该话语。
- ovos-bidirectional-translation-plugin/ovos-utterance-translation-plugin - This package includes a UtteranceTransformer plugin and a DialogTransformer plugin, they work together to allow OVOS to speak in ANY language
- ovos-translate-server-plugin - 该插件在更广泛的背景下用于按需翻译话语/文本（例如，从solvers和ovos-bidirectional-explanation-plugin）
- ovos-adapt-parser/ovos-adapt-pipeline-plugin - Adapt Intent Parser是一个灵活且可扩展的意图定义和确定框架。它旨在将自然语言文本解析为结构化意图，然后可以以编程方式调用。包含了一个已经不存在的mycroft-adapt的分支

### 音频
# VAD plugins
- ovos-vad-plugin-noise - 旧的 ovos-listener 中提取的简单 VAD 插件。只能用作后备选项（未下载）
- precise-lite-trainer - 用于训练 Precise-Lite 唤醒词模型的工具包（未下载）
- ovos-vad-plugin-webrtcvad - 使用 webrtcvad 进行语音活动检测的 ovos 插件
- ovos-vad-plugin-silero - 基于 Silero VAD 的 OVOS VAD 插件
# Wake Word plugins Note: tflite_runtime also need to be installed
- ovos-ww-plugin-precise-lite - Precision-lite 的唤醒词插件
- ovos-ww-plugin-vosk - Vosk 的唤醒词插件
- ovos-ww-plugin-openwakeword - OpenWakeWord 的唤醒词插件
# Microphone plugins
- ovos-microphone-plugin-sounddevice - 打开 python-sounddevice 库的 Voice OS 麦克风插件。使用 PortAudio 作为音频库来与音频组件交互。
- ovos-microphone-plugin-alsa - Microphone plugin for OpenVoiceOS using ALSA

# TTS Plugins
- ovos-tts-plugin-server/ovos-stt-server-plugin - TTS 服务器插件/ovos-tts-plugin-mimic3-server的替代
- ovos-tts-plugin-piper - 基于Piper的文本转语音插件
- ovos-stt-plugin-chromium - Chromium 的 STT 插件
# Media Playback plugins
- ovos_audio_plugin_simple - 简单音频插件/过时了，使用ovos-media
- ovos-audio-plugin-mpv - MPV OVOS 插件将 MPV 媒体播放器功能与(OVOS) 生态系统集成，提供用于播放各种媒体格式的音频后端。
- ovos-media-plugin-spotify - Spotify 媒体插件 （暂未下载）
- ovos-media-plugin-chromecast - Chromecast 媒体插件（暂未下载）
- ovos_plugin_common_play[extractors]/ovos-ocp-audio-plugin - 公共播放插件（暂未找到）
# gui
- ovos-gui-plugin-shell-companion - Shell companion 提供与ovos-shell集成的各种总线API
# PHAL plugins
- ovos-PHAL-plugin-alsa - ALSA 插件
- ovos-PHAL-plugin-system - 向 OVOS 提供系统特定命令。该插件的 dbus 接口尚未建立。
- ovos-PHAL-plugin-network-manager - NetworkManager plugin for PHAL
- ovos-PHAL-plugin-ipgeo - IP地理位置插件
- ovos-PHAL-plugin-connectivity-events - 连接性事件插件
- ovos-PHAL-plugin-oauth - OAuth 插件
- ovos-PHAL-plugin-wifi-setup - Central Wifi Setup Plugin for PHAL
- ovos-PHAL-plugin-hotkeys - map key presses to OVOS bus events
- ovos-PHAL-plugin-mk2-fan-control - ovos-PHAL-plugin-mk2-v6-fan-control
# workshop
- ovos-solver-yes-no-plugin - 一个简单的工具，用于指示用户对是/否提示回答“是”还是“否”。
### pipeline 插件
- ovos-common-query-pipeline-plugin - OVOS通用查询框架旨在通过从多个技能中收集答案并选择最佳技能来回答问题
- ovos_ocp_pipeline_plugin - OVOS插件用于专门的媒体处理
- ovos-persona - PersonaPipeline为OpenVoiceOS带来了多角色管理，实现了与虚拟助手的交互式对话。
- padacioso - 一个轻量级、非常简单的意图解析器
- ovos-padatious-pipeline-plugin - 由fann提供支持的高效敏捷的神经网络意图解析器。包含了一个已经不存在的mycroft-padatious的分支，在mycroft中式核心库

# 服务器
- ovos-persona-server - Persona Server
- ovos-stt-http-server - Turn any OVOS STT plugin into a micro service!
- ovos-tts-server - simple flask server to host OpenVoiceOS tts plugins as a service
- ovos-translate-server - Turn any OVOS Language plugin into a micro service!

# 客户端
ovos-bus-client/ovos_bus_client - messagebus client for the OVOS ecosystem 

# 工具
- ovos-shell - OVOS Shell is meant for devices without a desktop environment
- ovos-utterance-normalizer - 在意图解析之前规范化话语
- ovos-number-parser - 一个工具，用于从多种语言的文本中提取、发音和检测数字，支持数字口语化、文本数字提取和识别分数及序数。
- ovos-date-parser - 一个多语言日期和时间解析库，处理人类可读的日期、时间和持续时间表达式。

# 多媒体
- ovos-media- Media playback service for OpenVoiceOS
- ovos-ocp-audio-plugin - 需要重新克隆

# 技能
## 音频相关
- ovos-skill-boot-finished - 当一切开始并准备就绪时发出通知的技能
- ovos-skill-audio-recording - control recording mode in ovos-dinkum-listener, requires ovos-dinkum-listener
- ovos-skill-dictation - 持续转录用户语音到文本文件，而启用，为ovos-dinkum-listener 所必需
- ovos-skill-audio-recording - Record audio to file, 为ovos-dinkum-listener 所必需
- ovos-skill-volume - Control the volume of your system
- ovos-skill-naptime - 当你不想被打扰的时候，让助手睡觉。
## skills providing catalan specific functionality
- ovos-skill-fuster-quotes - 琼·福斯特引用技巧
- ovos-skill-word-of-the-day - 每日一句
- ovos-skill-days-in-history - 告诉你关于某个日历日的历史花絮
## skills-essential providing core functionality (offline)
- ovos-skill-fallback-unknown - 在没有Intent与语句匹配时使用
- ovos-skill-alerts - 一种管理闹钟、定时器、提醒、事件和待办事项的技能，并可选择将其与CalDAV服务同步。
- ovos-skill-personal - 官方人格技能-回答OVOS的基本人格问题
- ovos-skill-date-time - 日期和时间技能，提供世界各地城市的当前时间，日期和星期几。
- ovos-skill-hello-world - 一个简单的技能，用于了解OpenVoiceOS Skills如何工作。
- ovos-skill-spelling - 帮你拼单词
- ovos-skill-diagnostics - 检索系统信息，例如中央处理器、存储器和语言设置。
- ovos-skill-parrot - 一个模仿用户说话的技能
- ovos-skill-count - 可以从 1 数到任何用户指定的数字，甚至无限数，并大声说出每个数字。
- ovos-skill-randomness - OVOS 技能适用于各种机会 - 做出选择、掷骰子、掷硬币、在两个选择之间进行选择等。
## skills-extra providing non essential functionality
- ovos-skill-wordnet - 使用 Wordnet 回答类似字典的问题
- ovos-skill-laugh - 让你的语音助手笑得像个疯子
- ovos-skill-number-facts - 有关数字、数学、年份和日期的事实，来自 http://numbersapi.com 需要重新检出
- ovos-skill-iss-location - 追踪国际空间站的位置
- ovos-skill-cmd - 用于运行 shell 脚本和其他命令的简单 OVOS 技能。这些命令安静地执行，无需 OVOS 确认。
- ovos-skill-moviemaster - 提供电影相关信息的技能
- ovos-skill-confucius-quotes - 提供孔子名言的技能
- ovos-skill-icanhazdadjokes - 让 OVOS 用一点幽默点亮你的一天
- ovos-skill-camera - OpenVoiceOS 的摄像头技能，需要配套插件 ovos-PHAL-plugin-camera 或 ovos-PHAL-plugin-termux
## gui
- ovos-skill-homescreen - 主页
- ovos-skill-screenshot - 截屏技能
- ovos-skill-color-picker - 颜色选择器技能

## tools
- ovos-skill-application-launcher - launch applications by voice 


## skills-internet that require internet connectivity, should not be installed in offline devices
- ovos-skill-weather - OpenVoiceOS 官方天气技能，提供天气状况和预报。
- ovos-skill-ddg - DuckDuckGo 技能
- ovos-skill-wolfie - 使用 Wolfram Alpha 解决一般知识问题
- ovos-skill-wikipedia - Wikipedia 查询技能
- ovos-skill-wikihow - How to do nearly everything.
- ovos-skill-speedtest - 网络速度测试技能
- ovos-skill-ip - IP 地址查询技能
## skills-media for OCP, require audio playback plugins (usually mpv)
- ovos-skill-somafm - SomaFM 电台技能
- ovos-skill-news - 新闻播报技能
- ovos-skill-pyradios - PyRadios 电台技能
- ovos-skill-local-media - 本地媒体播放技能
- ovos-skill-youtube-music - search Youtube Music by voice!


# 不进行维护
- ovos-gui-plugin-shell-companion - provides various bus APIs that integrate with ovos-shell


source /home/pi/dev/norapy-dev/engine/venv/bin/activate

# 要启动的服务
ovos.service
ovos-messagebus.service
ovos-phal.service
ovos-listener.service
PartOf=ovos.service
Requires=ovos.service ovos-messagebus.service ovos-phal.service
ovos-dinkum-listener


# 查看正在运行的 ovos_messagebus 进程
ps aux | egrep 'ovos_messagebus | sed -n '1,200p'
tail -f /home/pi/dev/norapy-dev/logs/messagebus.log
tail -f ~/.local/share/mycroft/logs/skills.log

pip install -e .[extras] -c constraints.txt

pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-microphone-plugin-alsa
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-padatious-pipeline-plugin
scripts/install_fann.sh
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-vad-plugin-silero

# 如果你需要热词（wake-word）功能，请安装至少一个 wakeword 插件
source /home/pi/dev/norapy-dev/engine/venv/bin/activate
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-ww-plugin-precise-lite
# 或者
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-ww-plugin-vosk

pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-bidirectional-translation-plugin
#// define utterance fixes via fuzzy match ~/.local/share/mycroft/corrections.json
#// define unconditional replacements at word level ~/.local/share/mycroft/word_corrections.json

pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-utterance-plugin-cancel
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-utterance-plugin-cancel
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-utterance-plugin-cancel

pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-adapt-pipeline-plugin
pip install -e /home/pi/dev/norapy-dev/engine/engine-plugins/ovos-common-query-pipeline-plugin
# 模型太大，暂时不安装
pip install -e /home/pi/dev/norapy-dev/engine/engine-core/ovos-m2v-pipeline
# 下载模型
https://huggingface.co/OpenVoiceOS/ovos-model2vec-intents-LaBSE
https://huggingface.co/Jarbas/ovos-model2vec-intents-potion-4M
2025-10-19 19:37:04.111 - skills - ovos_persona:load_personas:198 - INFO - Found persona (provided via plugin): Remote Llama
2025-10-19 19:37:04.249 - skills - ovos_solver_openai_persona.engines:__init__:129 - ERROR - system prompt not set in config! defaulting to 'You are a helpful assistant.'
"intents": {
    "persona": {
        "default_persona": "OpenAI Persona",
        "persona_blacklist": ["Remote Llama"]
    },

Could not find resource file skill.json
engine/engine-core/ovos-workshop/ovos_workshop/resource_files.py @318

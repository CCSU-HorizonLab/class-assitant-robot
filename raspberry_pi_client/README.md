# 树莓派端客户端 (Raspberry Pi Client Architecture)

嵌入式 AI 课堂助手树莓派端核心代码库，采用分层化、模块化的软件架构，支持语音唤醒、多模态音视频采集、本地/云端 ASR/TTS 调度及设备保活监控。

---

## 📁 目录架构说明

```
raspberry_pi_client/
├── server.py                        # [入口] Web 控制台管理服务 (Flask 运行在 5000 端口)
├── config.py                        # [配置] 动态运行时参数控制器
├── const_config.py                  # [配置] 系统常量与能力开关矩阵
├── app_config.py                    # [配置] 硬件设备与路径配置
├── README.md                        # [文档] 架构与模块说明文档
│
├── core/                            # 核心业务逻辑层 (Core Domain)
│   ├── assistant.py                 # 语音唤醒监听、交互与大模型对话主循环
│   ├── capture_engine.py            # FFmpeg + OpenCV 双路音视频流并发采集引擎
│   ├── capture_session.py           # 课堂录制 Session 状态控制器与 CLI
│   ├── video_standardizer.py        # H.264 mp4 视频转码器 (支持转码后自动清除原始 mp4)
│   ├── teacher_questions.py         # Vosk 离线 ASR 教师提问事件检测引擎
│   └── transcript_delivery.py       # 课堂音频转录与 JSON 结构化元数据交付器
│
├── services/                        # AI 服务集成与网络通讯层 (Services Layer)
│   ├── heartbeat_reporter.py        # IoT 设备保活心跳上报服务 (自动上报 CPU/RAM/温度)
│   ├── prompt_deal.py               # 大模型 Prompt 构建与多轮对话上下文处理
│   ├── voice_solution.py            # 多源 ASR/TTS 方案路由与统一接口
│   ├── models/                      # 大模型 API 接入封装 (SiliconFlow / Doubao / OpenAI)
│   ├── asr_tts/                     # 语音识别与合成集成 (Azure / Doubao / Local TTS)
│   └── wake_words/                  # 离线语音唤醒词引擎 (Snowboy)
│
├── hardware/                        # 硬件与音频 I/O 驱动层 (Hardware Driver)
│   ├── recorder.py                  # 麦克风音频采集与收音驱动
│   └── player.py                    # 喇叭音频播放与音效驱动
│
└── templates/                       # Web 控制台前端 UI 模板
```

---

## 🚀 核心服务启动指南

### 1. 启动 Web 控制台与主程序 (推荐)
```bash
python3 server.py
```
* **运行端口**：`http://<树莓派IP>:5000`
* **伴随线程**：自动启动语音唤醒对话大循环 + 设备保活心跳上报。

### 2. 命令行手工触发录像控制
```bash
python3 core/capture_session.py start --classroom-id "301教室"
python3 core/capture_session.py stop
```

---

## ⚙️ 核心架构分层理念

1. **解耦硬件与业务**：`hardware/` 仅负责声卡录音与音频输出，不包含任何业务规则。
2. **AI 能力插件化**：`services/` 屏蔽了不同供应商 API 的差异，支持在 `const_config.py` 中自由切换 Azure / 豆包 / DeepSeek。
3. **数据安全与自动清理**：`core/video_standardizer.py` 内置转码去重机制，生成标准 H.264 mp4 视频后自动释放原始视频，保障 SD 卡空间。

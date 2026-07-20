# 智能课堂行为分析与教学反馈平台

## 项目概述
- 树莓派采集课堂视频 → 本地YOLO分析 → 云端FastAPI展示
- 面向计算机设计大赛，教师端课堂分析详情页是展示核心
- 用户角色：教师（看课堂分析）+ 管理员（管平台）

## 核心链路
```
Pi录制 → CIFS→Windows captures_local_delivery/ → 守护进程(15s轮询) → YOLO分析 → FastAPI(8011) → PostgreSQL
```

## 关键服务

| 组件 | 地址 | 认证 |
|------|------|------|
| Pi SSH | 192.168.31.124:22 | zwgk / 123456 |
| Pi Flask | http://192.168.31.124:5000 | - |
| 本地FastAPI | http://127.0.0.1:8011 | admin / teacher:teacher123 |
| PostgreSQL | localhost:5432 | postgres:root_password / classroom_cloud |

## 项目结构
- `raspberry_pi_client/` — Pi端代码（server.py是主入口）
- `local_analysis_client/` — 本地分析（守护进程 run_local_pipeline_daemon.ps1）
- `cloud_backend/` — FastAPI云端
- `captures_local_delivery/` — Pi录制的视频投递目录（CIFS挂载）
- `config.yaml` — 本地分析配置

## Pi 语音系统
- 助手名：晓晓，唤醒词引擎：Snowboy
- STT/TTS：Azure，LLM：SiliconFlow DeepSeek-V3
- 录像指令：开始录像 / 停止录像（本地硬编码匹配，不走LLM）
- 配置：const_config.py（含API key，不要覆盖）

## 开发约束
- 不修改 raw JSON 结构，不重构上传链路
- 先读 行为规则.md 了解产品定位和模块规划
- 比赛展示优先做教师端课堂分析详情页

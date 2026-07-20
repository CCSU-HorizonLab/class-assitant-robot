# 课堂交互分析系统云端接收服务

## 目标

该服务负责接收本地高性能电脑推送的 20 秒课堂交互统计 JSON，并进行：
- 基本校验
- 日志记录
- 原始结果落盘
- 为后续数据库入库与仪表盘接口预留扩展点

## 推荐目录

```text
/root/video_project/
├─ app.py
├─ deploy.sh
├─ cloud_backend/
│  ├─ main.py
│  ├─ config.py
│  ├─ schemas.py
│  ├─ storage.py
│  ├─ requirements.txt
│  ├─ .env.example
│  └─ data/
│     └─ raw/
└─ scripts/
   ├─ deploy_cloud_backend.sh
   └─ test_cloud_backend.sh
```

## 启动命令

```bash
cd /root/video_project
source /root/venv/bin/activate
pip install -r cloud_backend/requirements.txt
uvicorn cloud_backend.main:app --host 0.0.0.0 --port 8010
```

## systemd 建议

服务名建议：`classroom-cloud-backend.service`

启动命令建议：

```bash
/root/venv/bin/uvicorn cloud_backend.main:app --host 0.0.0.0 --port 8010
```

工作目录建议：

```bash
/root/video_project
```

## 数据库存储建议

当前版本先采用 JSON 文件落盘，确保本地端可以立即推送成功。

后续迁移数据库时建议：
- PostgreSQL：适合做教室维度聚合、时间序列统计、仪表盘查询
- MongoDB：适合先快速存储结构灵活的原始 JSON

如果毕业设计后续重点是聚合统计与查询，优先建议 PostgreSQL。




  总结已生成：session_2026_07_11_summary.md                                                                                                                                                                                                      
  ──────                                                                                                                                                                                                                                         
  ## 今日成果速览                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                 
  ### 做了什么                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                 
  1. 项目全面回顾 — 梳理了三端架构、数据流、开发边界、行为规则                                                                                                                                                                                   
  2. 诊断视频不能播放的根因 — 剥了三层：URL路由 → uploads链路 → 文件编码格式                                                                                                                                                                     
  3. 修复视频播放 — 两处代码改动 + 一次 FFmpeg 转码，视频现在可正常在 Dashboard 播放                                                                                                                                                             
                                                                                                                                                                                                                                                 
  ### 关键结论                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                 
  │ 树莓派  picamera  默认录制 MPEG-4 Part 2，后缀是  .mp4  但浏览器播不了。后续所有视频上传前都需要先用 FFmpeg 转码为 H.264 Baseline + faststart。                                                                                              
                                                                                                                                                                                                                                                 
  ### 明日可继续的方向（提示词里有选项 A/B/C）                                                                                                                                                                                                   
                                                                                                                                                                                                                                                 
  • A 完善教师端 Dashboard 视觉表现力（比赛加分项）                                                                                                                                                                                              
  • B 打通本地端视频上传链路（包含自动转码）                                                                                                                                                                                                     
  • C IoT 设备心跳状态管理                    

                                                                                                                                                                                                                                                 
  休息好，明天见！   


  好的，今天的工作就到这里。我已经为您生成了专门的明日 Agent 提升与续行指引文件：                                                                             
                                                                                                                                                              
  📄 tomorrow_agent_prompt.md                                                                                                                                 
                                                                                                                                                              
  在该提示词中，我详细记录了：                                                                                                                                
                                                                                                                                                              
  1. 当前运行环境：本地分析监听守护进程的后台启动状态和云端服务的运行端口；                                                                                   
  2. 今日开发资产：视频自动转码与多部分上传功能、仪表盘视觉改版，以及试点成功的 Jinja2 模板化重构（包含  login.html  等）；                                   
  3. 架构避坑说明：提醒后续 Agent 本地端配置目录（ configs/ ）和输出缓存目录（ processed_results/                                                             
  ）中存在的硬编码依赖，确保下一次迭代不会破坏本地分析与上传机制；                                                                                            
  4. 后续任务规划：云端视图（如  dashboard_v11.py  等）的继续模板化，以及本地端配置文件的双向路径兼容重构。                                                   
                                                                                                                                                              
  您可以将此提示词直接发送给明天接手的 Agent 伙伴，他将能够一秒接入上下文并继续开发！祝您今晚休息愉快！                                                       
                                                                                                            
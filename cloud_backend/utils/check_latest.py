import json
from pathlib import Path
from cloud_backend.config.settings import settings

raw_dir = Path("cloud_backend/data/raw")
files = sorted(raw_dir.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
latest = files[0]
data = json.loads(latest.read_text())
video = data.get("video") or {}
source = data.get("source") or {}

print(f"最新记录: {latest.parent.name}/{latest.name}")
print()

explicit_url = video.get("video_url") or data.get("video_url") or source.get("video_url") or ""
analysis_id = data.get("analysis_id", "")
vid_check = (video.get("video_id") or data.get("video_id", "")).lower()
is_demo = bool(analysis_id.lower().startswith("demo_") or vid_check.startswith("demo_"))

captures_root = settings.video_local_captures_dir
raw_path = video.get("raw_video_path") or data.get("raw_video_path") or source.get("source_path") or ""

if not explicit_url and is_demo:
    demo = Path("cloud_backend/uploads/video.mp4")
    if demo.exists():
        explicit_url = "/uploads/video.mp4"

if not explicit_url and raw_path:
    lp = Path(raw_path)
    try:
        if lp.resolve().is_file() and str(lp.resolve()).startswith(str(captures_root.resolve())):
            rel = str(lp.resolve().relative_to(captures_root.resolve())).replace("\\", "/")
            explicit_url = f"/captures/{rel}"
    except Exception:
        pass

status = "playable" if explicit_url else "pending"
print(f"  播放状态: {status}")
print(f"  播放地址: {explicit_url or '(无)'}")
print(f"  raw_video_path: {raw_path}")
print(f"  is_demo: {is_demo}")

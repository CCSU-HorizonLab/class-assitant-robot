"""本地离线 TTS，直接调用 espeak 命令行。"""
import subprocess
from loguru import logger


ESPEAK_VOICE = "zh"
ESPEAK_RATE = 180


def wav(text: str, filename: str) -> None:
    """将文本合成为 WAV 文件。"""
    try:
        subprocess.run(
            ["espeak", "-v", ESPEAK_VOICE, "-s", str(ESPEAK_RATE), "-w", filename, text],
            check=True,
            capture_output=True,
        )
        logger.info(f"local_tts: wav saved -> {filename}")
    except Exception as exc:
        logger.error(f"local_tts wav failed: {exc}")

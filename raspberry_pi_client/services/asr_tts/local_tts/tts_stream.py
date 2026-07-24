"""本地离线流式 TTS，直接调用 espeak 命令行。"""
import subprocess
import threading
from queue import Queue, Empty
import time
from loguru import logger


ESPEAK_VOICE = "zh"
ESPEAK_RATE = 180


class _FakeFuture:
    """模拟 Azure tts_task，espeak 同步说完即为完成。"""
    def get(self):
        return True


class TTSManager:
    def __init__(self, response_queue: Queue):
        self.stop_event = threading.Event()
        self.response_queue = response_queue
        self.tts_task = _FakeFuture()

    def stop_tts(self):
        logger.debug("Stopping local TTS")
        self.stop_event.set()
        self.stop_event.clear()

    def start_tts(self):
        logger.info("本地流式 TTS 启动 (espeak)")
        while True:
            if self.response_queue.empty():
                time.sleep(0.1)
                continue

            if self.stop_event.is_set():
                break

            # 收集文本块
            full_text: list[str] = []
            while not self.stop_event.is_set():
                try:
                    chunk = self.response_queue.get(timeout=0.5)
                    if chunk == "[END]":
                        break
                    full_text.append(chunk)
                except Empty:
                    break

            if full_text:
                text = "".join(full_text).strip()
                if text:
                    logger.info(f"TTS speaking: {text[:60]}...")
                    try:
                        subprocess.run(
                            ["espeak", "-v", ESPEAK_VOICE, "-s", str(ESPEAK_RATE), text],
                            check=True,
                            capture_output=True,
                        )
                    except Exception as exc:
                        logger.error(f"TTS error: {exc}")


response_queue: Queue = Queue()
tts_manager = TTSManager(response_queue)
tts_thread = threading.Thread(target=tts_manager.start_tts, daemon=True)
tts_thread.start()

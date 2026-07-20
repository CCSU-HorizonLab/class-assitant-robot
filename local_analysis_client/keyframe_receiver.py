# ==============================================================================
# ⚠️ WARNING: BACKWARD COMPATIBILITY WRAPPER / 向后兼容包装文件
# ==============================================================================
# 本文件仅作为向后兼容的动态导入包装层，供历史脚本和命令行入口直接调用。
# 请勿在此处修改任何实际业务逻辑或算法代码！
#
# 真实业务逻辑及核心代码请移步至以下路径修改：
# - local-processor/api/keyframe_receiver.py
# ==============================================================================

from __future__ import annotations


import importlib.util
from pathlib import Path
import sys


def _load_relocated_module():
    module_path = Path(__file__).resolve().parent / "local-processor" / "api" / "keyframe_receiver.py"
    spec = importlib.util.spec_from_file_location("local_processor_api_keyframe_receiver", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载归位后的接收器模块: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_MODULE = _load_relocated_module()

app = _MODULE.app
health = _MODULE.health
receive_keyframes = _MODULE.receive_keyframes
main = _MODULE.main


if __name__ == "__main__":
    main()

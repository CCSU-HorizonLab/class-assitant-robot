from const_config import voice_solution,chat_or_standard

# 根据配置动态导入对应语音方案的三个核心模块：tts、reco、tts_stream
if voice_solution == "azure":
    # 导入azure方案的tts、reco、tts_stream
    from services.asr_tts.Azure_solution import tts, reco
    if chat_or_standard == True:
        from services.asr_tts.Azure_solution import tts_stream
        from services.asr_tts.Azure_solution.tts_stream import response_queue, tts_manager
else:
    raise NotImplementedError(f"Unsupported or legacy voice_solution: {voice_solution}. Please use 'azure'.")

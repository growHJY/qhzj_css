import edge_tts


async def convert_text2audio_save(text, save_path):
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save(save_path)

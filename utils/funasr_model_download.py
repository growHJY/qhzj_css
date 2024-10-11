import os
from modelscope import snapshot_download

model_path = os.path.join(os.path.dirname(os.getcwd()), "model")

if not os.path.exists(model_path):
    os.mkdir(model_path)

model_dir = snapshot_download('iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
                              cache_dir=model_path)

# 文件下载路由

from flask import Blueprint, jsonify, request, send_file, current_app
from src.utils.jwt_util import get_user_from_token
from src.pojo.response import Response as R

import os

download_blueprint = Blueprint("download", __name__, url_prefix="/api/download")

STATIC_AUDIO_PATH = os.path.join(os.getcwd(), "resources", "audio")


@download_blueprint.route("/get_audio", methods=["GET"])
def get_audio():
    token = request.headers.get("Authorization")
    user = get_user_from_token(token, current_app.config["TOKEN_SECRET"])
    file_name = request.args.get("audio_code")
    # 用于分辨是从文字聊天还是从语音聊天发送的请求
    # 0: 语音 1: 文字
    get_type = request.args.get("type")
    file = None
    try:
        if get_type == "0":
            file = send_file(os.path.join(STATIC_AUDIO_PATH, "uploads", "file_" + user.uphone, file_name + ".mp3"),
                             as_attachment=True)
        elif get_type == "1":
            file = send_file(
                os.path.join(STATIC_AUDIO_PATH, "text2audio", "file_" + user.uphone, file_name + ".mp3"),
                as_attachment=True)

    except FileNotFoundError:
        pass
        return jsonify(R(404, "未找到文件", None).to_dict())
    return file

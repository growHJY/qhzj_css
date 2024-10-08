# 大模型对话路由
from datetime import datetime
from flask import request, current_app, jsonify, Blueprint

from src.enum_tool.question_type_enum import QuestionTypeEnum
from src.utils.jwt_util import get_user_from_token
from src.utils.ollama_talk import talk_to_ollama
from src.utils.audio_util import convert_text2audio_save
from src.utils.mysql_operation import MysqlOperation
from src.pojo.chats_record import ChatsRecord
from src.pojo.response import Response as R
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

import asyncio
import os

talk_blueprint = Blueprint('talk', __name__, url_prefix='/api/talk')

STATIC_AUDIO_PATH = os.path.join(os.getcwd(), "resources", "audio")


@talk_blueprint.route("", methods=["GET"])  # 文本对话
def talk_text():
    token = request.headers.get("Authorization")
    talk_id = request.args.get("talk_id")

    user = get_user_from_token(token, current_app.config["TOKEN_SECRET"])

    text = request.args.get("text")
    audio_code = "t_" + str(int(datetime.now().timestamp() * 1000))
    audio_path = os.path.join(STATIC_AUDIO_PATH, "text2audio", "file_" + user.uphone, audio_code + ".mp3")
    audio_folder_path = os.path.join(STATIC_AUDIO_PATH, "text2audio", "file_" + user.uphone)
    if not os.path.exists(audio_folder_path):
        os.makedirs(os.path.join(STATIC_AUDIO_PATH, "text2audio", "file_" + user.uphone))

    ollama_answer = talk_to_ollama(text)
    asyncio.run(convert_text2audio_save(ollama_answer, audio_path))

    audio_url = f"{current_app.config['SERVER_HOST']}/api/get_audio?audio_code={audio_code}&type={1}"
    # 聊天内容添加到数据库
    operation = MysqlOperation()
    conn = operation.connect()
    try:
        with conn.cursor() as cursor:
            sql = (
                f"INSERT INTO chats_record(uid, talk_id, chat_type, question_type, content_txt, audio_url,generate_time) "
                f"VALUE(%s,%s,%s,%s,%s,%s,%s)")

            user_chat_record = ChatsRecord(user.uid, talk_id, QuestionTypeEnum.TEXT.value, QuestionTypeEnum.TEXT.value,
                                           text,
                                           str(int(datetime.now().timestamp() * 1000)))
            cursor.execute(sql, (
                user_chat_record.uid, user_chat_record.talk_id, user_chat_record.chat_type,
                user_chat_record.question_type,
                user_chat_record.content_txt, user_chat_record.audio_url, user_chat_record.generate_time))

            ollama_chat_record = ChatsRecord(user.uid, talk_id, QuestionTypeEnum.AUDIO.value,
                                             QuestionTypeEnum.TEXT.value,
                                             ollama_answer,
                                             str(int(datetime.now().timestamp() * 1000)), audio_url)
            cursor.execute(sql, (ollama_chat_record.uid, ollama_chat_record.talk_id, ollama_chat_record.chat_type,
                                 ollama_chat_record.question_type, ollama_chat_record.content_txt,
                                 ollama_chat_record.audio_url, ollama_chat_record.generate_time))

            conn.commit()
    except Exception as e:
        return jsonify(R(500, str(e), None).to_dict())
    finally:
        operation.disconnect()

    return jsonify({
        "text": ollama_answer,
        "audio_url": audio_url
    })


@talk_blueprint.route("", methods=["POST"])  # 音频对话
def talk_audio():  # 音频聊天
    token = request.headers.get("Authorization")
    talk_id = request.form.get("talk_id")
    user = get_user_from_token(token, current_app.config["TOKEN_SECRET"])

    file = request.files["file"]
    ts = str(int(datetime.now().timestamp() * 1000))
    filename = "question_" + ts
    upload_path = os.path.join(STATIC_AUDIO_PATH, "uploads", "file_" + user.uphone)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    file.save(os.path.join(upload_path, filename + ".mp3"))

    model_dir = "model/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"

    model = AutoModel(
        model=model_dir,
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cuda:0",
    )

    res = model.generate(
        input=f"{os.path.join(upload_path, filename + '.mp3')}",
        cache={},
        language="zn",  # "zn", "en", "yue", "ja", "ko", "no_speech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )

    # 回答
    text = rich_transcription_postprocess(res[0]["text"]).replace(" ", "")  # 用户文本识别
    answer_ollama = talk_to_ollama(text)

    answer_mp3_path = "answer_" + ts
    question_mp3_path = "question_" + ts
    user_question_path = upload_path + "/" + answer_mp3_path + ".mp3"
    user_question_url = f"{current_app.config['SERVER_HOST']}/api/get_audio?audio_code={question_mp3_path}&type={0}"  # 用户上传的音频url
    audio_url = f"{current_app.config['SERVER_HOST']}/api/get_audio?audio_code={answer_mp3_path}&type={0}"  # ai回答的音频url
    asyncio.run(convert_text2audio_save(answer_ollama, user_question_path))

    # 记录添加到数据库
    operation = MysqlOperation()
    conn = operation.connect()

    try:
        with conn.cursor() as cursor:
            sql = (
                f"INSERT INTO chats_record(uid, talk_id, chat_type, question_type, content_txt, audio_url,generate_time) "
                f"VALUE(%s,%s,%s,%s,%s,%s,%s)")
            user_chat_record = ChatsRecord(user.uid, talk_id, QuestionTypeEnum.TEXT.value, QuestionTypeEnum.AUDIO.value,
                                           text,
                                           str(int(datetime.now().timestamp() * 1000)), user_question_url)

            cursor.execute(sql, (
                user_chat_record.uid, user_chat_record.talk_id, user_chat_record.chat_type,
                user_chat_record.question_type,
                user_chat_record.content_txt, user_chat_record.audio_url, user_chat_record.generate_time))

            ollama_chat_record = ChatsRecord(user.uid, talk_id, QuestionTypeEnum.AUDIO.value,
                                             QuestionTypeEnum.TEXT.value,
                                             answer_ollama,
                                             str(int(datetime.now().timestamp() * 1000)), audio_url)

            cursor.execute(sql, (ollama_chat_record.uid, ollama_chat_record.talk_id, ollama_chat_record.chat_type,
                                 ollama_chat_record.question_type, ollama_chat_record.content_txt,
                                 ollama_chat_record.audio_url, ollama_chat_record.generate_time))
            conn.commit()
    except Exception as e:
        print(e)
        return jsonify(R(500, str(e), None).to_dict())
    finally:
        operation.disconnect()

    return jsonify(R(200, "转换成功", {
        "prompt": text,
        "text": answer_ollama,
        "audio_url": audio_url
    }).to_dict())


@talk_blueprint.route("/new_dialogue", methods=["GET"])  # 新会话
def new_dialogue():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify(
            R(500, "请求失败", None).to_dict()
        )
    user = get_user_from_token(token, current_app.config["TOKEN_SECRET"])
    operation = MysqlOperation()
    conn = operation.connect()
    sql = f"SELECT * FROM chats_record WHERE uid = %s ORDER BY talk_id DESC;"
    cursor = conn.cursor()
    cursor.execute(sql, (user.uid,))
    cursor.close()
    result = cursor.fetchone()
    chat_record = ChatsRecord(result[1], result[2], result[3], result[4], result[5], result[7], result[6])
    operation.disconnect()
    return jsonify(R(200, "None", {
        "talk_id": chat_record.talk_id + 1
    }).to_dict())


@talk_blueprint.route("/history", methods=["GET"])  # 历史数据
def history():
    token = request.headers.get("Authorization")
    talk_id = request.args.get("talk_id")
    if not (token or talk_id):
        return jsonify(R(500, "请检查参数", None).to_dict())

    user = get_user_from_token(token, current_app.config["TOKEN_SECRET"])
    operation = MysqlOperation()
    conn = operation.connect()
    try:
        with conn.cursor() as cursor:
            sql = f"SELECT * FROM chats_record WHERE uid = %s AND talk_id = %s ORDER BY CAST(generate_time AS UNSIGNED);"
            cursor.execute(sql, (user.uid, talk_id))
            result = cursor.fetchall()
            chats = []
            for r in result:
                c = ChatsRecord(r[1], r[2], r[3], r[4], r[5], r[7], r[6])
                c.cid = r[0]  # cid
                chats.append(c.to_dict())

            return jsonify(R(200, "历史消息列表获取成功", chats).to_dict())
    except Exception as e:
        return jsonify(R(500, str(e), None).to_dict())
    finally:
        operation.disconnect()

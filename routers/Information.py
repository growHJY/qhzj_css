# 资讯模块
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from src.utils.jwt_util import get_user_from_token
from src.pojo.information import Information
from src.utils.mysql_operation import MysqlOperation

import os

information_blueprint = Blueprint('information', __name__, url_prefix="/api/information")


@information_blueprint.route('/information_list', methods=['GET'])  # 资讯列表
def new_information():
    return jsonify({'message': 'Hello World!'})


@information_blueprint.route("/cover_img_upload", methods=["POST"])  # 文章封面上传
def cover_img_upload():
    image_file = request.files['image']

    cover_image_path = os.path.join(os.getcwd(), "resources", "article_image")
    if not os.path.exists(cover_image_path):
        os.mkdir(cover_image_path)

    operation = MysqlOperation()
    conn = operation.connect()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM information ORDER BY aid DESC LIMIT 1;"
            cursor.execute(sql)
            res = cursor.fetchone()

            if res is None:
                image_file.save(os.path.join(cover_image_path, "1.jpg"))
            else:
                image_file.save(os.path.join(cover_image_path, str(res[0] + 1) + ".jpg"))

    except Exception as e:
        print(str(e))
    finally:
        operation.disconnect()

    return jsonify({"message": "success"})


@information_blueprint.route("/add_information", methods=['POST'])  # 添加资讯
def add_information():
    token = request.headers.get("Authorization")
    user = get_user_from_token(token, current_app.config['TOKEN_SECRET'])
    category = request.form.get("category")
    title = request.form.get('title')
    cover_img = request.form.get('cover_img')
    content = request.form.get('content')
    publish_time = str(int(datetime.now().timestamp() * 1000))
    inf = Information(None, user.uid, category, title, cover_img, content, publish_time, 0)
    return jsonify({'message': '添加资讯'})


@information_blueprint.route("/update_information", methods=['POST'])  # 更新资讯
def update_information():
    pass


@information_blueprint.route("/view", methods=["GET"])  # 查看资讯详情
def view_information():
    pass


@information_blueprint.route("/delete_information", methods=["GET"])  # 删除资讯
def delete_information():
    pass

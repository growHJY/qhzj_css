# 资讯模块
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from src.utils.jwt_util import get_user_from_token
from src.pojo.information import Information
from src.utils.mysql_operation import MysqlOperation
from src.pojo.response import Response as R

import os

information_blueprint = Blueprint('information', __name__, url_prefix="/api/information")


@information_blueprint.route('/information_list', methods=['GET'])  # 资讯列表
def new_information():
    category = request.args.get("category")
    inf_list = []
    try:
        operation = MysqlOperation()
        conn = operation.connect()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM information WHERE category = %s"
            cursor.execute(sql, (category,))
            res_list = cursor.fetchall()
            for r in res_list:
                inf = Information(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
                inf_list.append(inf.to_dict())
    except Exception as e:
        return jsonify(R(500, str(e), None).to_dict())
    finally:
        operation.disconnect()
    return jsonify(R(200, "获取成功", inf_list).to_dict())


@information_blueprint.route("/cover_img_upload", methods=["POST"])  # 文章封面上传
def cover_img_upload():
    image_file = request.files['image']

    cover_image_path = os.path.join(os.getcwd(), "resources", "article_image")
    if not os.path.exists(cover_image_path):
        os.mkdir(cover_image_path)

    operation = MysqlOperation()
    conn = operation.connect()
    image_url_path = None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM information ORDER BY aid DESC LIMIT 1;"
            cursor.execute(sql)
            res = cursor.fetchone()

            if res is None:
                image_file.save(os.path.join(cover_image_path, "1.jpg"))
                image_url_path = current_app.config["SERVER_HOST"] + "/api/download?file_type=0&filename=1.jpg"
            else:
                image_file.save(os.path.join(cover_image_path, str(res[0] + 1) + ".jpg"))
                image_url_path = current_app.config["SERVER_HOST"] + "/api/download?file_type=0&filename=" + str(
                    res[0] + 1) + ".jpg"

    except Exception as e:
        print(str(e))
    finally:
        operation.disconnect()

    return jsonify(R(200, "获取成功", {
        "image_url": image_url_path
    }).to_dict())


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
    operation = MysqlOperation()
    conn = operation.connect()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO information(uid, category, title, cover_img, content, publish_time, views) VALUE(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,
                           (user.uid, inf.category, inf.title, inf.cover_img, inf.content, inf.publish_time, inf.views))
            conn.commit()
    except Exception as e:
        print(str(e))
    finally:
        operation.disconnect()

    return jsonify(R(200, "发布成功", None).to_dict())


@information_blueprint.route("/update_information", methods=['POST'])  # 更新资讯
def update_information():
    pass


@information_blueprint.route("/view", methods=["GET"])  # 查看资讯详情
def view_information():
    pass


@information_blueprint.route("/delete_information", methods=["GET"])  # 删除资讯
def delete_information():
    pass

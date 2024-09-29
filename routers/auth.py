# 用户登录注册模块
from flask import Blueprint, request, jsonify, current_app
from src.pojo.user import User
from src.pojo.response import Response as R
from src.utils.mysql_operation import MysqlOperation
from src.utils.jwt_util import generate_token

import bcrypt

user_blueprint = Blueprint('auth', __name__, url_prefix='/api/user')


@user_blueprint.route('/login', methods=['POST'])  # 登录
def login():
    uphone = request.args.get("uphone")
    pwd = request.args.get("pwd").encode('utf-8')  # 将密码编码为字节

    mysql = MysqlOperation()
    connect = mysql.connect()
    cursor = connect.cursor()
    user = None
    json_str = None
    try:
        sql = "SELECT uid, uname, sname, uphone, pwd FROM users WHERE uphone = %s"
        cursor.execute(sql, (uphone,))
        result = cursor.fetchone()
        cursor.close()

        if result is not None:
            # 用户存在，验证密码
            stored_hash = result[4].encode('utf-8')
            user = User(result[0], result[1], result[2], result[3], None)
            if bcrypt.checkpw(pwd, stored_hash):  # 验证通过
                # token生成
                token = generate_token(user.to_dict(), current_app.config["TOKEN_SECRET"], 864000)  # todo 测试token 时效10天
                json_str = jsonify(R(200, "登录成功", {
                    "token": token,
                    "user": user.to_dict()
                }).to_dict())
            else:
                json_str = jsonify(R(200, "帐号或密码错误", None).to_dict())
        else:
            json_str = jsonify(R(200, "手机号未注册", None).to_dict())

    except Exception as e:
        return jsonify(R(500, str(e), user.to_dict()).to_dict())
    finally:
        mysql.disconnect()

    return json_str


@user_blueprint.route('/register', methods=['POST'])  # 注册
def register():
    uname = request.args.get("uname")
    sname = request.args.get("sname")
    pwd = request.args.get("pwd")
    uphone = request.args.get("uphone")

    mysql = MysqlOperation()
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = f"SELECT uid, uname, sname, pwd, uphone FROM users WHERE uphone = {uphone}"
    cursor.execute(sql)
    result = cursor.fetchone()
    db_user = None
    if result is not None:
        db_user = User(result[0], result[1], result[2], result[4], result[3])

    json_str = None
    try:
        if db_user is None or not db_user.uphone == uphone:  # 用户不存在
            sql = f"INSERT INTO users(uname, sname, pwd, uphone) VALUES (%s, %s, %s, %s)"

            # 生成盐并散列密码
            password_bytes = pwd.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(password_bytes, salt)

            cursor.execute(sql, (uname, sname, hashed_pwd, uphone))
            connect.commit()
            cursor.close()
            json_str = jsonify(R(200, "注册成功", None).to_dict())
        else:
            json_str = jsonify(R(500, "手机号已存在", None).to_dict())
    except Exception as e:
        json_str = jsonify(R(500, str(e), None).to_dict())
    finally:
        mysql.disconnect()

    return json_str

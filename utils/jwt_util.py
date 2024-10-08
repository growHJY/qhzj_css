from datetime import datetime, timedelta
from src.pojo.response import Response as R
from src.pojo.user import User

import jwt


def generate_token(payload: object, secret_key: str, expires_in=86400) -> str:
    now_time = datetime.utcnow()
    p = {
        'exp': now_time + timedelta(seconds=expires_in),
        'iat': now_time,
        'sub': payload
    }
    return jwt.encode(p, secret_key, algorithm='HS256')


def verify_token(token: str, secret_key: str) -> R:
    try:
        payload = R(200, "验证成功", {
            "token": jwt.decode(token, secret_key, algorithms="HS256"),
            "adopt": True
        })
    except jwt.ExpiredSignatureError as e:
        payload = R(403, "token过期", {
            "token": None,
            "adopt": False
        })
    except jwt.exceptions.DecodeError as e:
        payload = R(403, "token错误", {
            "token": None,
            "adopt": False
        })
    return payload


def get_user_from_token(token: str, secret_key: str) -> User:
    token_payload = verify_token(token, secret_key)
    if token_payload.param and token_payload.param['adopt'] is False:
        raise Exception("token解析失败")
    user = token_payload.param['token']['sub']
    user = User(user['uid'], user['uname'], user['sname'], user['uphone'], user['pwd'])
    return user

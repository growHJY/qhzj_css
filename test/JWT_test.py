from datetime import datetime, timedelta

import jwt

jwt_key = "qhzj_token"


def generate_token():
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=1, seconds=10),
        "iat": datetime.utcnow(),
        "sub": {"name": "<NAME>", "email": "<EMAIL>"}
    }
    return jwt.encode(payload=payload, key=jwt_key, algorithm="HS256")


def verify_token(token):
    payload = ""
    try:
        payload = jwt.decode(token, jwt_key, algorithms="HS256")
    except jwt.ExpiredSignatureError as e:  # token失效
        print("失效")
        return False
    except jwt.exceptions.InvalidSignatureError as e:  # token错误
        return False
    except jwt.exceptions.DecodeError as e:  # 编码错误
        return False
    return payload


if __name__ == '__main__':
    token = generate_token()
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjYzODY2MjQsImlhdCI6MTcyNjMwMDIyNCwic3ViIjp7InVpZCI6MTEsInVuYW1lIjoiaGgiLCJzbmFtZSI6ImhoIHN0b3JlIiwicHdkIjpudWxsLCJ1cGhvbmUiOiIxMSJ9fQ.sAra5v4hDW80O1-uAiw_HUlQsnVCt18AifBX0XN_5_c"
    print(token)
    print(verify_token(token))

# 权限验证装饰器
from flask import jsonify, Request
from functools import wraps
from src.utils.jwt_util import verify_token


def login_authorization_decorator(request: Request, token_key: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            token_result = verify_token(token, token_key)

            if not token or len(token) == 0:
                return jsonify({"message": "Not authorized"})
            if token_result.param.get("adopt"):  # 验证通过
                return f(*args, **kwargs)
            else:  # 验证未通过
                return token_result.to_dict()

        return wrapper

    return decorator

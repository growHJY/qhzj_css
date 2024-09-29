from flask import Flask, request, jsonify, abort
from functools import wraps

app = Flask(__name__)


# 定义一个装饰器来验证权限
def check_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != "mysecrettoken":  # 示例验证逻辑
            # abort(403)  # 没有权限，返回403
            return jsonify({'message': 'not authorized'})
        return f(*args, **kwargs)

    return decorated_function


@app.route('/test_permission', methods=['GET'])
@check_permission
def secure_data():
    return jsonify({"message": "This is protected data!"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

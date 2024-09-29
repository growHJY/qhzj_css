# 资讯模块

from flask import Blueprint, jsonify

information_blueprint = Blueprint('information', __name__, url_prefix="/api/information")


@information_blueprint.route('/new_information', methods=['GET'])
def new_information():
    return jsonify({'message': 'Hello World!'})

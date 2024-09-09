from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from app.models import Admin, Student


login_bp = Blueprint('login_bp', __name__)

# 验证管理员登录
@login_bp.route('/api/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "请输入用户名或密码"}), 400

    admin = Admin.query.filter_by(username=username).first()

    if not admin:
        return jsonify({"error": "用户不存在"}), 404

    if admin.password == password:
        access_token = create_access_token(identity={"username": username, "role": "admin"})
        return jsonify({"message": "登录成功!", "token": access_token}), 200
    else:
        return jsonify({"error": "密码错误"}), 401



# 验证学生登录
@login_bp.route('/api/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "请输入用户名或密码"}), 400

    student = Student.query.filter_by(name=username).first()
    userID = student.rid # 获取用户ID

    if not student:
        return jsonify({"error": "用户不存在"}), 404

    if student.password == password:
        access_token = create_access_token(identity={"username": username, "role": 'student'})
        return jsonify({"message": "登录成功!", "user": {"username": username,"userID": userID},"token": access_token}), 200
    else:
        return jsonify({"error": "密码错误"}), 401


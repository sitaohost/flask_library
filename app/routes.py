from flask import Blueprint, request, jsonify
from .models import Admin, Student, db, Book
import os

bp = Blueprint('main', __name__)

@bp.route('/', )
def index():
    return 'Welcome to the Flask Library !'


# 验证管理员登录
@bp.route('/admin_login', methods=['POST'])
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
        return jsonify({"message": "登录成功!", "user": {"username": username}}), 200
    else:
        return jsonify({"error": "密码错误"}), 401

# 验证学生登录
@bp.route('/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    student = Student.query.filter_by(name=username).first()
    
    if not student:
        return jsonify({"error": "用户不存在"}), 404

    if student.password == password:
        return jsonify({"message": "登录成功!", "user": {"username": username}}), 200
    else:
        return jsonify({"error": "密码错误"}), 401


# 获取所有图书
@bp.route('/books/all', methods=['GET'])
def get_books_all():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# 根据图书 ID 获取图书
@bp.route('/books/get/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({"error": "Book not found"}), 404

# 新增图书
UPLOAD_FOLDER = '/Users/sitao/flask/flask_library/static'  # 定义图书封面保存路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/books/add', methods=['POST'])
def add_book():
    data = request.form.to_dict()
    file = request.files.get('picture')

    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        data['picture'] = os.path.join(UPLOAD_FOLDER, filename)  # 保存图片路径
    else:
        data['picture'] = None

    new_book = Book(
        title=data.get('title'),
        author=data.get('author'),
        publisher=data.get('publisher'),
        pages=data.get('pages'),
        price=data.get('price'),
        quantity=data.get('quantity'),
        originalquantity=data.get('quantity'),
        description=data.get('description'),
        picture=data.get('picture')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201

# @bp.route('/books/<int:book_id>', methods=['PUT'])
# def update_book(book_id):
#     book = Book.query.filter_by(bid=book_id).first()
#     if book:
#         data = request.get_json()
#         book.title = data.get('title', book.title)
#         book.author = data.get('author', book.author)
#         book.publisher = data.get('publisher', book.publisher)
#         book.pages = data.get('pages', book.pages)
#         book.price = data.get('price', book.price)
#         book.quantity = data.get('quantity', book.quantity)
#         book.originalquantity = data.get('originalquantity', book.originalquantity)
#         book.description = data.get('description', book.description)
#         book.picture = data.get('picture', book.picture)
#         db.session.commit()
#         return jsonify(book.to_dict()), 200
#     return jsonify({"error": "Book not found"}), 404

@bp.route('/books/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.filter_by(bid=book_id).first() # 查找对应的图书
    if book:
        db.session.delete(book)  # 删除图书
        db.session.commit()  # 提交更改
        return jsonify({"success": True}), 200
        return jsonify({"success": False, "error": "Book not found"}), 404
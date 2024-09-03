from flask import Blueprint, request, jsonify
from .models import Admin, Student, db, Book
from werkzeug.security import check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/', )
def index():
    return 'Welcome to the Flask Library !'


# 验证用户登录
@bp.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    admin = Admin.query.filter_by(username=username).first()

    if admin and check_password_hash(admin.password, password):
        return jsonify({"message": "登录成功!", "user": {"username": username}}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@bp.route('/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    student = Student.query.filter_by(name=username).first()

    if student and check_password_hash(student.password, password):
        return jsonify({"message": "登录成功!", "user": {"name": username}}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401




@bp.route('/books/all', methods=['GET'])
def get_books_all():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

@bp.route('/books/get/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({"error": "Book not found"}), 404

# @bp.route('/books', methods=['POST'])
# def add_book():
#     data = request.get_json()
#     new_book = Book(
#         title=data.get('title'),
#         author=data.get('author'),
#         publisher=data.get('publisher'),
#         pages=data.get('pages'),
#         price=data.get('price'),
#         quantity=data.get('quantity'),
#         originalquantity=data.get('originalquantity'),
#         description=data.get('description'),
#         picture=data.get('picture')
#     )
#     db.session.add(new_book)
#     db.session.commit()
#     return jsonify(new_book.to_dict()), 201

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

# @bp.route('/books/<int:book_id>', methods=['DELETE'])
# def delete_book(book_id):
#     book = Book.query.filter_by(bid=book_id).first()
#     if book:
#         db.session.delete(book)
#         db.session.commit()
#         return jsonify(book.to_dict()), 200
#     return jsonify({"error": "Book not found"}), 404
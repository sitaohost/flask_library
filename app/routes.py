from flask import Blueprint, redirect, request, jsonify
from .models import Admin, Student, db, Book, Bar
import os

bp = Blueprint('main', __name__)

@bp.route('/', )
def index():
    return redirect('/static/admin_login.html')


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
        data['picture'] = filename
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

#更新图书
@bp.route('/books/update/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.form.to_dict()
    file = request.files.get('picture')

    # 更新图书信息
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.publisher = data.get('publisher', book.publisher)
    book.pages = data.get('pages', book.pages)
    book.price = data.get('price', book.price)
    book.quantity = data.get('quantity', book.quantity)
    book.originalquantity = data.get('originalquantity', book.originalquantity)
    book.description = data.get('description', book.description)

    # 处理图片上传
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        book.picture = filename  # 更新图片

    db.session.commit()
    return jsonify(book.to_dict()), 200

#删除图书
@bp.route('/books/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify(book.to_dict()), 200
    return jsonify({"error": "Book not found"}), 404

# 搜索图书
@bp.route('/books/search/<string:keyword>', methods=['GET'])
def search_books(keyword):
    # 根据书名搜索
    books_by_title = Book.query.filter(Book.title.like(f'%{keyword}%')).all()
    if books_by_title:
        # 如果根据书名找到了书籍，直接返回结果
        return jsonify([book.to_dict() for book in books_by_title]), 200
    
    # 如果根据书名没有找到书籍，尝试根据作者搜索
    books_by_author = Book.query.filter(Book.author.like(f'%{keyword}%')).all()
    
    if books_by_author:
        # 如果根据作者找到了书籍，返回结果
        return jsonify([book.to_dict() for book in books_by_author]), 200
    
    # 如果既没有根据书名也没有根据作者找到书籍，返回 404 Not Found
    return jsonify({"message": "No books found matching the keyword."}), 404

# 展示所有学生的借阅记录
@bp.route('/books/show_borrow_records', methods=['GET'])
def show_borrow_records():
    # 查询所有借阅记录
    borrow_records = Bar.query.all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200

@bp.route('/books/delete_borrow_record/<int:bar_id>', methods=['DELETE'])
def delete_borrow_record(bar_id):
    record = Bar.query.filter_by(borrow_id=bar_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify(record.to_dict()), 200
    return jsonify({"error": "Record not found"}), 404


@bp.route('/books/show_borrow_records_by_student_id/<int:student_id>', methods=['GET'])
def show_borrow_records_by_student_id(student_id):
    # 查询指定学生编号的借阅记录
    borrow_records = Bar.query.filter_by(user_id=student_id).all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200


# 获取所有学生信息
@bp.route('/students/all', methods=['GET'])
def get_students_all():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students]), 200


# 根据学生 ID 获取学生信息
@bp.route('/students/get/<int:student_id>', methods=['GET'])
def get_student_by_id(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if student:
        return jsonify(student.to_dict()), 200
    return jsonify({"error": "Student not found"}), 404

# 新增学生
@bp.route('/students/add', methods=['POST'])
def add_student():
    data = request.form.to_dict()

    new_student = Student(
        name=data.get('name'),
        sex=data.get('sex'),
        age=data.get('age'),
        address=data.get('address'),
        phone=data.get('phone'),
        password=data.get('password')
    )

    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201


# 更新学生信息
@bp.route('/students/update/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.form.to_dict()

    # 更新学生信息
    student.name = data.get('name', student.name)
    student.sex = data.get('sex', student.sex)
    student.age = data.get('age', student.age)
    student.address = data.get('address', student.address)
    student.phone = data.get('phone', student.phone)
    student.password = data.get('password', student.password)

    db.session.commit()
    return jsonify(student.to_dict()), 200


# 删除学生
@bp.route('/students/delete/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify(student.to_dict()), 200
    return jsonify({"error": "Student not found"}), 404


# 搜索学生
@bp.route('/students/search/<string:keyword>', methods=['GET'])
def search_students(keyword):
    # 根据姓名搜索
    students_by_name = Student.query.filter(Student.name.like(f'%{keyword}%')).all()
    if students_by_name:
        return jsonify([student.to_dict() for student in students_by_name]), 200

    # 如果没有根据姓名找到学生，返回 404
    return jsonify({"message": "No students found matching the keyword."}), 404

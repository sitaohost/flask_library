import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import db, Book, Bar, Student

admin_bp = Blueprint('admin_bp', __name__)


# 根据图书 ID 获取图书
@admin_bp.route('/api/books/get/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book_by_id(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        return jsonify(book.to_dict()), 200
    return jsonify({"error": "Book not found"}), 404

# 新增图书
UPLOAD_FOLDER = '/Users/sitao/flask/flask_library/static/images'  # 定义图书封面保存路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/api/books/add', methods=['POST'])
@jwt_required()
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
@admin_bp.route('/api/books/update/<int:book_id>', methods=['PUT'])
@jwt_required()
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
@admin_bp.route('/api/books/delete/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify(book.to_dict()), 200
    return jsonify({"error": "Book not found"}), 404



# 搜索图书
@admin_bp.route('/api/books/search/<string:keyword>', methods=['GET'])
@jwt_required()
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
@admin_bp.route('/api/books/show_borrow_records', methods=['GET'])
@jwt_required()
def show_borrow_records():
    # 查询所有借阅记录
    borrow_records = Bar.query.all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200

# 删除借阅记录
@admin_bp.route('/api/books/delete_borrow_record/<int:bar_id>', methods=['DELETE'])
@jwt_required()
def delete_borrow_record(bar_id):
    record = Bar.query.filter_by(borrow_id=bar_id).first()

    if record:
        # 检查是否存在归还日期
        if record.return_date:
            db.session.delete(record)
            db.session.commit()
            return jsonify(record.to_dict()), 200
        else:
            return jsonify({"error": "无法删除未归还的借阅记录"}), 400

    return jsonify({"error": "记录未找到"}), 404

# 根据学生 ID 获取借阅记录
@admin_bp.route('/api/books/show_borrow_records_by_student_id/<int:student_id>', methods=['GET'])
@jwt_required()
def show_borrow_records_by_student_id(student_id):
    # 查询指定学生编号的借阅记录
    borrow_records = Bar.query.filter_by(user_id=student_id).all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200


# 获取所有学生信息
@admin_bp.route('/api/students/all', methods=['GET'])
def get_students_all():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students]), 200


# 根据学生 ID 获取学生信息
@admin_bp.route('/api/students/get/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_by_id(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if student:
        return jsonify(student.to_dict()), 200
    return jsonify({"error": "Student not found"}), 404


# 新增学生
@admin_bp.route('/api/students/add', methods=['POST'])
@jwt_required()
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
@admin_bp.route('/api/students/update/<int:student_id>', methods=['PUT'])
@jwt_required()
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
@admin_bp.route('/api/students/delete/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify(student.to_dict()), 200
    return jsonify({"error": "Student not found"}), 404


# 搜索学生
@admin_bp.route('/api/students/search/<string:keyword>', methods=['GET'])
@jwt_required()
def search_students(keyword):
    # 根据姓名搜索
    students_by_name = Student.query.filter(Student.name.like(f'%{keyword}%')).all()
    if students_by_name:
        return jsonify([student.to_dict() for student in students_by_name]), 200

    # 如果没有根据姓名找到学生，返回 404
    return jsonify({"message": "No students found matching the keyword."}), 404

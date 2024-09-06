from flask import Blueprint, redirect, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from .models import Admin, Student, db, Book, Bar
import os
import datetime

bp = Blueprint('main', __name__,static_folder="../static", static_url_path='')

# 本地部署时，访问根目录时重定向到 index.html，以便前端路由正常工作
# 在服务器中，可以通过 Nginx 配置实现同样的效果
@bp.route('/')
def index():
    return redirect('/pages/index.html')


# 验证管理员登录
@bp.route('/api/admin_login', methods=['POST'])
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
@bp.route('/api/student_login', methods=['POST'])
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


# 获取所有图书 [开放性接口]
@bp.route('/api/books/all', methods=['GET'])
def get_books_all():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# 根据图书 ID 获取图书
@bp.route('/api/books/get/<int:book_id>', methods=['GET'])
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

@bp.route('/api/books/add', methods=['POST'])
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
@bp.route('/api/books/update/<int:book_id>', methods=['PUT'])
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
@bp.route('/api/books/delete/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify(book.to_dict()), 200
    return jsonify({"error": "Book not found"}), 404



# 搜索图书
@bp.route('/api/books/search/<string:keyword>', methods=['GET'])
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
@bp.route('/api/books/show_borrow_records', methods=['GET'])
@jwt_required()
def show_borrow_records():
    # 查询所有借阅记录
    borrow_records = Bar.query.all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200

@bp.route('/api/books/delete_borrow_record/<int:bar_id>', methods=['DELETE'])
@jwt_required()
def delete_borrow_record(bar_id):
    record = Bar.query.filter_by(borrow_id=bar_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify(record.to_dict()), 200
    return jsonify({"error": "Record not found"}), 404


@bp.route('/api/books/show_borrow_records_by_student_id/<int:student_id>', methods=['GET'])
@jwt_required()
def show_borrow_records_by_student_id(student_id):
    # 查询指定学生编号的借阅记录
    borrow_records = Bar.query.filter_by(user_id=student_id).all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200


# 获取所有学生信息
@bp.route('/api/students/all', methods=['GET'])
def get_students_all():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students]), 200


# 根据学生 ID 获取学生信息
@bp.route('/api/students/get/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_by_id(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if student:
        return jsonify(student.to_dict()), 200
    return jsonify({"error": "Student not found"}), 404


# 新增学生
@bp.route('/api/students/add', methods=['POST'])
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
@bp.route('/api/students/update/<int:student_id>', methods=['PUT'])
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
@bp.route('/api/students/delete/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    student = Student.query.filter_by(rid=student_id).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify(student.to_dict()), 200
    return jsonify({"error": "Student not found"}), 404


# 搜索学生
@bp.route('/api/students/search/<string:keyword>', methods=['GET'])
@jwt_required()
def search_students(keyword):
    # 根据姓名搜索
    students_by_name = Student.query.filter(Student.name.like(f'%{keyword}%')).all()
    if students_by_name:
        return jsonify([student.to_dict() for student in students_by_name]), 200

    # 如果没有根据姓名找到学生，返回 404
    return jsonify({"message": "No students found matching the keyword."}), 404

# 借书
@bp.route('/api/books/borrow/<int:b_bookid>&uid=<int:u_id>&days=<int:b_days>', methods=['POST'])
@jwt_required()
def borrow_book(b_bookid,u_id,b_days):

    # if b_days is None:
    #     return jsonify({"error": "Missing 'days' parameter"}), 400
    # 在前端页面判断借阅天数是否为空即可
    
    book = Book.query.filter_by(bid=b_bookid).first()
    student = Student.query.filter_by(rid=u_id).first()
    not_return = Bar.query.filter_by(user_id=u_id).filter(Bar.return_date.is_(None)).count()
    is_borrow = Bar.query.filter_by(user_id=u_id).filter_by(book_id=b_bookid).filter(Bar.return_date.is_(None)).count()


    if is_borrow > 0:
        return jsonify({"error": "你已经借阅了这本书,请勿重复借阅"}), 403
    
    if not_return >= 3:
        return jsonify({"error": "借阅数量过多,请归还其他图书后重试"}), 402
    
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if not student:
        return jsonify({"error": "Student not found"}), 404

    if book.quantity <= 0:
        return jsonify({"error": "out of stock"}), 405

    book.quantity -= 1
    db.session.commit()

    new_record = Bar(
        book_id=b_bookid,
        book_name=book.title,
        user_id=u_id,
        user_name=student.name,
        borrow_date=datetime.date.today(),
        borrow_days=b_days  # 假设Bar模型有一个字段记录借阅天数
    )

    db.session.add(new_record)
    db.session.commit()

    return jsonify(new_record.to_dict()), 201

#归还图书
@bp.route('/api/books/return/bar_id=<int:bar_id>&book_id=<int:book_id>', methods=['POST'])
@jwt_required()
def return_book(bar_id,book_id):
    bar=Bar.query.filter_by(borrow_id=bar_id).first()
    book=Book.query.filter_by(bid=book_id).first()
    
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    if not bar:
        return jsonify({"error": "借阅记录未找到"}), 404 
    
    bar.return_date=datetime.date.today()
    book.quantity += 1

    db.session.commit()
    
    return jsonify(bar.to_dict()), 201
    
@bp.route('/api/students/chpasswd', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    student_id = data.get('student_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not student_id or not old_password or not new_password:
        return jsonify({"error": "请输入学生ID、旧密码和新密码"}), 400

    student = Student.query.filter_by(rid=student_id).first()

    if not student:
        return jsonify({"error": "学生不存在"}), 404

    if student.password != old_password:
        return jsonify({"error": "旧密码不正确"}), 401

    student.password = new_password
    db.session.commit()

    return jsonify({"message": "密码修改成功"}), 200
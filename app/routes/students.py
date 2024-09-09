from sqlalchemy import or_
from app.models import Student, Book, Bar, db
from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
import datetime

student_bp = Blueprint('student_bp', __name__)


# 搜索图书
@student_bp.route('/api/students/searchBooks/<string:keyword>', methods=['GET'])
@jwt_required()
def search_book(keyword):
    books = Book.query.filter(
        or_(
            Book.bid.like(f'%{keyword}%'),  # 根据书号搜索
            Book.title.like(f'%{keyword}%'),  # 根据书名搜索
            Book.author.like(f'%{keyword}%'),  # 根据作者搜索
            Book.publisher.like(f'%{keyword}%'),  # 根据出版社搜索
        )
    ).all()

    if books:
        # 将查询结果转换为字典列表
        return jsonify([book.to_dict() for book in books]), 200

    return jsonify({"error": "Book not found"}), 404


# 借书
@student_bp.route('/api/students/borrow/<int:b_bookid>&uid=<int:u_id>&days=<int:b_days>', methods=['POST'])
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


# 归还图书
@student_bp.route('/api/students/return/bar_id=<int:bar_id>&book_id=<int:book_id>', methods=['POST'])
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

# 根据学生 ID 获取借阅记录
@student_bp.route('/api/students/show_borrow_records_by_student_id/<int:student_id>', methods=['GET'])
#@jwt_required()
def show_borrow_records_by_student_id(student_id):
    # 查询指定学生编号的借阅记录
    borrow_records = Bar.query.filter_by(user_id=student_id).all()
    
    # 将查询结果转换为字典列表
    records_list = [record.to_dict() for record in borrow_records]
    
    return jsonify(records_list), 200
  
# 搜索借阅记录
@student_bp.route('/api/students/searchBorrowRecords/<string:keyword>', methods=['GET'])
@jwt_required()
def search_borrow_record(keyword):
   
    records = Bar.query.filter(
        or_(
            Bar.borrow_id.like(f'%{keyword}%'),# 根据借阅记录ID搜索
            Bar.book_id.like(f'%{keyword}%'), # 根据书号搜索
            Bar.book_name.like(f'%{keyword}%'), # 根据书名搜索
        )
    ).all()

    if records:
        # 将查询结果转换为字典列表
        return jsonify([record.to_dict() for record in records]), 200

    return jsonify({"error": "Record not found"}), 404

# 修改密码
@student_bp.route('/api/students/chpasswd', methods=['POST'])
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
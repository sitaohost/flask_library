from flask import Blueprint, jsonify, redirect
from app.models import Book

# 创建一个名为 'public' 的蓝图实例
public_bp = Blueprint('public', __name__)

# 本地部署时，访问根目录时重定向到 index.html，以便前端路由正常工作
# 在服务器中，可以通过 Nginx 配置实现同样的效果
@public_bp.route('/')
def index():
    return redirect('/pages/index.html')

# 获取所有图书 [开放性接口]
@public_bp.route('/api/books/all', methods=['GET'])
def get_books_all():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200
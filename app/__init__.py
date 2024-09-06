'''
_init__.py 是 Flask 应用程序的初始化文件。它的作用是创建并配置 Flask 应用实例，以及初始化应用所需的扩展（如数据库、登录管理等）
'''

from flask import Flask
from .models import db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__) # 创建一个 Flask 应用实例，__name__ 参数告诉 Flask 在寻找资源文件（如静态文件）时使用当前模块的路径。
    app.json.ensure_ascii = False  # 解决中文乱码问题(防止中文字符在 JSON 响应中被转义为 Unicode 字符串)
    app.config['JWT_SECRET_KEY'] = '612'  # 改为自己的密钥
    JWTManager(app)

    # app.static_folder="../pages" # 设置静态文件目录
    # app.static_url_path='' # 设置静态文件 URL 前缀

    # 配置 MySQL 数据库 URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://library:library123@localhost/library'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化 SQLAlchemy
    db.init_app(app) # init_app() 方法将 SQLAlchemy 与应用实例绑定，从而使数据库模型与应用实例关联。

    # with app.app_context():
    #     # 创建数据库和表（如果需要，可以省略此步骤，如果表已经存在）
    #     db.create_all()

    from . import routes
    app.register_blueprint(routes.bp) # 注册蓝图 bp。蓝图（Blueprint）是一种将应用程序的各个功能模块化的方法

    return app # 返回创建的 Flask 应用实例。这样做的好处是可以在项目的其他地方（如 run.py）使用这个工厂函数create_app()来创建和配置应用实例
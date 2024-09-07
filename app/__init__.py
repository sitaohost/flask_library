from flask import Flask, config
from .models import db
from flask_jwt_extended import JWTManager
from config import Config # 导入配置文件
# 如果写成import config, 那么app.config.from_object(config.Config)


def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path='')
    app.config.from_object(Config) # 使用配置文件中的配置
    # 初始化插件
    db.init_app(app)
    JWTManager(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    return app

def register_blueprints(app):
    # 在这里导入并注册蓝图
    from .routes.public import public_bp
    from .routes.login import login_bp
    from .routes.admin import admin_bp
    from .routes.students import student_bp

    # 注册各个蓝图
    # 使用 url_prefix 来指定蓝图的 URL 前缀
    app.register_blueprint(public_bp, url_prefix='') 
    app.register_blueprint(login_bp, url_prefix='')
    app.register_blueprint(admin_bp, url_prefix='')
    app.register_blueprint(student_bp, url_prefix='')
   
    
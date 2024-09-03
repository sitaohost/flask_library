from flask_sqlalchemy import SQLAlchemy

# 创建 SQLAlchemy 实例，用于定义数据库模型和与数据库的交互。
db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'  # 映射到 'books' 表
    
    bid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    publisher = db.Column(db.String(255))
    pages = db.Column(db.Integer)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    originalquantity = db.Column(db.Integer)
    description = db.Column(db.Text)
    picture = db.Column(db.String(255))

    def to_dict(self):
        return {
            "bid": self.bid,
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "pages": self.pages,
            "price": self.price,
            "quantity": self.quantity,
            "originalquantity": self.originalquantity,
            "description": self.description,
            "picture": self.picture
        }
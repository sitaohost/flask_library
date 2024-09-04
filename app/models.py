from flask_sqlalchemy import SQLAlchemy

# 创建 SQLAlchemy 实例，用于定义数据库模型和与数据库的交互。
db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admin'
    
    aid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    sex = db.Column(db.String(5), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)

    # 定义to_dict方法
    def to_dict(self):
        return {
            "rid": self.rid,
            "name": self.name,
            "sex": self.sex,
            "age": self.age,
            "address": self.address,
            "phone": self.phone,
            "password": self.password
        }


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
    

class Bar(db.Model):
    __tablename__ = 'bar'
    
    borrow_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.bid'), nullable=False)  # 外键关联到 books 表的 bid 字段
    book_name = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('students.rid'), nullable=False)  # 外键关联到 students 表的 rid 字段
    user_name = db.Column(db.String(255), nullable=True)
    borrow_date = db.Column(db.Date, nullable=True)
    borrow_days = db.Column(db.Integer, nullable=True)
    return_date = db.Column(db.Date, nullable=True)

    # 定义to_dict方法
    def to_dict(self):
        return {
            "borrow_id": self.borrow_id,
            "book_id": self.book_id,
            "book_name": self.book_name,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "borrow_date": self.borrow_date.strftime('%Y-%m-%d') if self.borrow_date else None,
            "borrow_days": self.borrow_days,
            "return_date": self.return_date.strftime('%Y-%m-%d') if self.return_date else None
        }
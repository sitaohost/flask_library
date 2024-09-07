class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://library:library123@localhost/library'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False  # 解决中文乱码问题
    JWT_SECRET_KEY = '612'  # 改为自己的密钥
    
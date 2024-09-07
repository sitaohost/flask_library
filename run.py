from app import create_app

library_api = create_app()  # 调用 create_app() 函数创建一个 Flask 应用实例

'''
if __name__ == '__main__':是 Python 中的一个常见模式，用于检查当前模块是否是作为主程序执行。只有当该模块作为脚本直接运行时，下面的代码块才会被执行。
如果该模块被导入到其他模块中（如在单元测试或其他脚本中），则不会执行。
'''

if __name__ == '__main__':
    library_api.run(host='localhost', port=8090, debug=True)



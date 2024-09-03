from app import create_app

app = create_app() # 调用 create_app() 函数创建一个 Flask 应用实例

if __name__ == '__main__':
    app.run(host='localhost', port=8090, debug=True)

'''
if __name__ == '__main__':是 Python 中的一个常见模式，用于检查当前模块是否是作为主程序执行。只有当该模块作为脚本直接运行时，下面的代码块才会被执行。如果该模块被导入到其他模块中（如在单元测试或其他脚本中），则不会执行。
	•	app.run(host='localhost', port=8090, debug=True)：启动 Flask 开发服务器，并指定主机、端口和调试模式：
	•	host='localhost'：设置服务器监听的主机地址。'localhost' 表示只允许本地访问。如果想让外部设备可以访问，可以设置为 '0.0.0.0'。
	•	port=8090：设置服务器监听的端口号。在这个例子中，端口是 8090。你可以将其更改为其他未被占用的端口号。
	•	debug=True：启用调试模式。在调试模式下，Flask 会在代码更改时自动重新加载，并在发生错误时显示一个交互式的调试页面。
'''
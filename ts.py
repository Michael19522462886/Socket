from socket import *
# 绑定本机的所有网络接口IP地址
IP = '127.0.0.1'
PORT = 50000
BUFLEN = 512
# 使用IPv4协议，TCP传输方式
listenSocket = socket(AF_INET,SOCK_STREAM)

listenSocket.bind((IP,PORT))
# 监听连接请求，最大连接数为5
listenSocket.listen(5)
print('Socket is listening')
# 响应sync+ACk 返回的是元祖 产生一个新的socket用来传输数据
dataSocket, addr = listenSocket.accept()
print('Socket is connected',addr)
while True:
    # 阻塞式的
    data = dataSocket.recv(BUFLEN)
    # 返回空字节串表示客户端关闭连接
    if not data:
        break
    print(data.decode('utf-8'))
    dataSocket.send(b'Hello, client')
dataSocket.close()
listenSocket.close()
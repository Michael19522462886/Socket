# coding:utf-8
import re
import threading
from socket import *


# 定义处理客户端请求的函数
def handle_client(tcpCliSock, addr):
    print('Received a connection from: ', addr)
    try:
        message = tcpCliSock.recv(4096).decode()

        if not message:
            tcpCliSock.close()
            return

        # 从请求中提取文件名
        filename = message.split()[1].partition("//")[2].replace('/', '_')
        filename = re.sub(r'[?&=:]', '', filename)
        fileExist = False

        try:
            # 检查缓存中是否存在该文件
            with open(filename, "rb") as f:
                outputdata = f.read()
                fileExist = True
                print('File Exists!')

                # 将缓存文件发送给客户端
                tcpCliSock.sendall(outputdata)
                print('Read from cache')

        except IOError:
            print('File Exists in cache:', fileExist)
            if not fileExist:
                # 在代理服务器上创建一个新的socket
                print('Creating socket on proxy server...')
                c = socket(AF_INET, SOCK_STREAM)

                # 从请求中提取主机名
                hostn = message.split()[1].partition("//")[2].partition("/")[0]
                print('Host Name: ', hostn)

                try:
                    # 连接到远程服务器的80端口
                    print('Connecting to the host...')
                    c.connect((hostn, 80))
                    print('Socket connected to port 80 of the host')

                    # 将客户端的请求转发给远程服务器
                    c.sendall(message.encode())
                    print(f"Request sent to server: {message}")

                    # 从远程服务器接收响应
                    buff = b""
                    while True:
                        chunk = c.recv(4096)
                        if not chunk:
                            break
                        buff += chunk

                    print('Response received from server.')

                    # 将响应发送回客户端
                    tcpCliSock.sendall(buff)

                    # 将响应缓存起来
                    with open(filename, "wb") as tmpFile:
                        tmpFile.write(buff)
                    print('Response cached.')

                except Exception as e:
                    print(f"Illegal request or connection error: {e}")
                finally:
                    c.close()

            else:
                print('File Not Found.')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 关闭客户端连接
        tcpCliSock.close()


# 创建socket，绑定到端口，开始监听
tcpSerPort = 8899
tcpSerSock = socket(AF_INET, SOCK_STREAM)

# 准备服务器socket
tcpSerSock.bind(('', tcpSerPort))
tcpSerSock.listen(5)

print('Server is ready to serve...')

# 无限循环以接受客户端连接
while True:
    try:
        # 接受客户端连接
        tcpCliSock, addr = tcpSerSock.accept()

        # 为每个新的连接创建一个线程
        client_thread = threading.Thread(target=handle_client, args=(tcpCliSock, addr))
        client_thread.start()

    except Exception as e:
        print(f"Server Error: {e}")


tcpSerSock.close()

from socket import *

IP = "127.0.0.1"
SERVER_PORT = 50000
BUFFER_SIZE = 512

dataSocket = socket(AF_INET, SOCK_STREAM)
# 发送sync报文 第三次再连接
dataSocket.connect((IP, SERVER_PORT))

while True:
    message = input("Enter message to send: ")
    if message == "quit":
        break
    dataSocket.send(message.encode())
    data = dataSocket.recv(BUFFER_SIZE)
    print("Received from server: ", data.decode())

dataSocket.close()

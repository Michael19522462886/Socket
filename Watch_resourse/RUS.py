import socket
import json
import time
import threading
# 这个程序作为TCP服务端，获取资源使用数据，简称 RUS （Resource Usage Stat）


class RUS:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.client_socket = None
        self.is_paused = False

    def start(self):
        print("RUS started, waiting for connection...")
        # 等待客户端连接
        self.client_socket, addr = self.server_socket.accept()
        print(f"Connected to {addr}")
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            message = self.receive_message()
            if message:
                self.handle_message(message)

    def handle_message(self, message):
        message_type = message.get('type')
        if message_type == 'pause':
            self.is_paused = True
            duration = message.get('duration', 0)
            threading.Thread(target=self.pause, args=(duration,)).start()
            self.send_message({'type': 'cmd-ack', 'code': 200, 'info': '处理成功'})
        elif message_type == 'resume':
            self.is_paused = False
            self.send_message({'type': 'cmd-ack', 'code': 200, 'info': '处理成功'})
        elif message_type == 'report-ack':
            print("Report acknowledged by AT")

    def pause(self, duration):
        time.sleep(duration)
        self.is_paused = False

    def send_message(self, message):
        message_str = json.dumps(message)
        message_length = len(message_str)
        full_message = f"{message_length}\n{message_str}"
        self.client_socket.sendall(full_message.encode('utf-8'))

    def receive_message(self):
        length_str = self._recv_until_newline()
        if not length_str:
            return None
        length = int(length_str)
        message_str = self.client_socket.recv(length).decode('utf-8')
        return json.loads(message_str)

    # 获取消息头的长度
    def _recv_until_newline(self):
        data = b""
        while not data.endswith(b"\n"):
            more = self.client_socket.recv(1)
            if not more:
                return None
            data += more
        return data[:-1].decode('utf-8')

    def collect_data(self):
        while True:
            if not self.is_paused:
                data = {
                    "type": "report",
                    "info": {
                        "CPU Usage": "30%",
                        "Mem usage": "53%"
                    }
                }
                self.send_message(data)
            time.sleep(5)


if __name__ == '__main__':
    rus = RUS()
    threading.Thread(target=rus.collect_data).start()
    rus.start()
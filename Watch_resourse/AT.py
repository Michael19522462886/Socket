import socket
import json
import threading
import time
# Admin Terminal (AT) class


class AT:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to RUS")
        # 目标就是要执行的任务、一般是一个函数 start表示启动线程与主线程并行的进行
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            message = self.receive_message()
            if message:
                self.handle_message(message)

    def handle_message(self, message):
        message_type = message.get('type')
        if message_type == 'report':
            print(f"Received data: {message['info']}")
            self.send_message({'type': 'report-ack'})
        elif message_type == 'cmd-ack':
            print(f"Command acknowledged: {message['info']}")

    def send_message(self, message):
        message_str = json.dumps(message)
        message_length = len(message_str)
        full_message = f"{message_length}\n{message_str}"
        self.client_socket.sendall(full_message.encode('utf-8'))

    def receive_message(self):
        # 拿到消息头中消息体的长度
        length_str = self._recv_until_newline()
        if not length_str:
            return None
        # 字符串转数字
        length = int(length_str)
        # 拿到消息体
        message_str = self.client_socket.recv(length).decode('utf-8')
        # 字符串转json
        return json.loads(message_str)

    def _recv_until_newline(self):
        data = b""
        while not data.endswith(b"\n"):
            more = self.client_socket.recv(1)
            if not more:
                return None
            data += more
        return data[:-1].decode('utf-8')

    def send_pause_command(self, duration):
        self.send_message({"type": "pause", "duration": duration})

    def send_resume_command(self):
        self.send_message({"type": "resume"})

if __name__ == '__main__':
    at = AT()
    at.connect()
    # Example commands
    at.send_pause_command(10)
    time.sleep(15)
    at.send_resume_command()

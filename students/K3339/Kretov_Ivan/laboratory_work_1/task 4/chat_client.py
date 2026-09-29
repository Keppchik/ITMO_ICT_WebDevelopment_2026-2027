import socket
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8083))

name = input("Как вас зовут?\n")
client_socket.send(name.encode())


def receive():
    while True:
        try:
            message = client_socket.recv(1024)
        except OSError:
            break
        if not message:
            print('Сервер закрыл соединение')
            break
        print(message.decode())


thread = threading.Thread(target=receive, daemon=True)
thread.start()


while True:
    message = input()
    if message == 'EXIT':
        client_socket.close()
        break
    client_socket.send(message.encode())



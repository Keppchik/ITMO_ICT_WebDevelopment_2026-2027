import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 8083))

server_socket.listen()
clients = []
threads = []
lock = threading.Lock()

def send_all(message, sender_address, sender_name):
    with lock:
        for client in clients:
            if client[2] != sender_address:
                client[1].sendall(f'{sender_name}: {message}'.encode())

def listen_to_client(client_name, client_connection, client_address):
    while True:
        try:
            message = client_connection.recv(1024).decode()
        except OSError:
            break
        if message:
            send_all(message, client_address, client_name)
        else:
            print(f'Пользователь {client_name} отключился')
            send_all('отключился(-ась)', client_address, client_name)
            with lock:
                clients.remove([client_name, client_connection, client_address])
                client_connection.close()

while True:
    client_connection, client_address = server_socket.accept()

    client_name = client_connection.recv(1024).decode()
    print(f'Подключился {client_name}')

    client_info = [client_name, client_connection, client_address]
    clients.append(client_info)

    thread = threading.Thread(target=listen_to_client, args=client_info)

    threads.append(thread)

    thread.start()

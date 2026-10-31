import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 8081))

server_socket.listen(1)

while True:
    client_connection,  client_address = server_socket.accept()

    data = client_connection.recv(1024).decode()

    a, b, h = map(float, data.split())

    response = str((a + b) * h / 2).encode()

    client_connection.sendall(response)

    client_connection.close()
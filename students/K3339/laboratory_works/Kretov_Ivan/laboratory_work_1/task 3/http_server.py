import socket

HOST = 'localhost'
PORT = 8082

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(5)

html_file = open('index.html')

html_content = ''.join(html_file.readlines())

html_file.close()

while True:
    client_connection, client_address = server_socket.accept()

    http_response = (
        'HTTP/1.1 200 OK\r\n'
        'Content-Type: text/html; charset=UTF-8\r\n'
        f'Content-Length: {len(html_content)}\r\n'
        'Connection: close\r\n'
        '\r\n'
        + html_content
    )

    client_connection.sendall(http_response.encode())

    client_connection.close()
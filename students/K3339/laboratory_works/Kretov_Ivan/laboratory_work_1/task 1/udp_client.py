import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(b'Hello, server', ('localhost', 8080))

response = client_socket.recv(1024).decode()

print(response)

client_socket.close()
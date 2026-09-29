import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 8081))

while True:
    data = input('Введите длины оснований трапеции и ее высоту через пробел\n')
    try:
        if len(data.split()) != 3:
            raise ValueError
        _, _, _ = map(float, data.split())
        break
    except ValueError:
        print('Неверный ввод данных')

client_socket.send(data.encode())

S = client_socket.recv(1024).decode()

print('Площадь трапеции равна', S)

client_socket.close()

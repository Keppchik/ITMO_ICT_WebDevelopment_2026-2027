# Лабораторная 1. Работа с сокетами

### Цель работы
Понять принципы межсокетного взаимодействия в вебе. Научиться реализовывать базовую архитектуру клиент-сервер

## Практическое задание 1. Обмен сообщениями по UDP
UDP — протокол без установления соединения: отправитель просто посылает датаграмму, не дожидаясь подтверждения от получателя. Это быстрее TCP, но не гарантирует ни доставку, ни порядок пакетов

??? quote "Код сервера"
    ```python
    import socket
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_socket.bind(('localhost', 8080))
    
    while True:
        data, client_address = server_socket.recvfrom(1024)
        print(data.decode())
    
        server_socket.sendto(b'Hello, client', client_address)
    ```

??? quote "Код клиента"
    ```python
    import socket
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    client_socket.sendto(b'Hello, server', ('localhost', 8080))
    
    response = client_socket.recv(1024).decode()
    
    print(response)
    
    client_socket.close()
    ```

### Примеры работы:
![Screenshot 2026-09-30 at 12.39.06.png](images/Screenshot%202026-09-30%20at%2012.39.06.png)
![Screenshot 2026-09-30 at 12.41.50.png](images/Screenshot%202026-09-30%20at%2012.41.50.png)

## Практическое задание 2. Вычисления через TCP
TCP, в отличие от UDP, требует установления соединения перед обменом данными и гарантирует доставку и порядок байт. Дополнительные накладные расходы на установку соединения окупаются надёжностью: параметры, введённые пользователем на клиенте, дойдут до сервера, а результат вычисления — обратно

??? quote "Код сервера"
    ```python
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
    ```

??? quote "Код клиента"
    ```python
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
    ```

### Пример работы:
![Screenshot 2026-09-30 at 12.45.47.png](images/Screenshot%202026-09-30%20at%2012.45.47.png)

## Практическое задание 3. Раздача HTML-страницы по HTTP
HTTP-ответ — обычный текст, оформленный по строгому формату: строка статуса, заголовки, пустая строка и тело

??? quote "Код сервера"
    ```python
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
    ```

??? quote "Код страницы"
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Lab1 task3</title>
    </head>
    <body>
        <h1>Task 3</h1>
        <p>lorem ipsum</p>
    </body>
    </html>
    ```

### Пример работы:
![Screenshot 2026-09-30 at 12.51.15.png](images/Screenshot%202026-09-30%20at%2012.51.15.png)

## Практическое задание 4. Чат на сокетах
Чат отличается от предыдущих заданий тем, что сервер обслуживает не одного клиента, а нескольких одновременно

??? quote "Код сервера"
    ```python
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
    ```

??? quote "Код клиента"
    ```python
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
    ```

### Примеры работы:
![Screenshot 2026-09-30 at 12.56.15.png](images/Screenshot%202026-09-30%20at%2012.56.15.png)
![Screenshot 2026-09-30 at 12.56.25.png](images/Screenshot%202026-09-30%20at%2012.56.25.png)
![Screenshot 2026-09-30 at 12.56.34.png](images/Screenshot%202026-09-30%20at%2012.56.34.png)
![Screenshot 2026-09-30 at 12.56.48.png](images/Screenshot%202026-09-30%20at%2012.56.48.png)

## Практическое задание 5. Простой веб-сервер (GET/POST)
По методу сервер решает, что делать: сохранить присланную оценку по дисциплине или собрать HTML-страницу со списком всех оценок

??? quote "Код сервера"
    ```python
    import socket
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.bind(('localhost', 8084))
    
    server_socket.listen()
    
    class Subject:
        def __init__(self, name):
            self.name = name
            self.grades = []
    
        def add_grade(self, grade):
            self.grades.append(grade)
    
    
    class Journal:
        def __init__(self):
            self.subjects = {}
    
        def add_subject(self, subject_name):
            self.subjects[subject_name] = Subject(subject_name)
    
        def add_grade(self, subject_name, grade):
            if subject_name not in self.subjects:
                self.add_subject(subject_name)
    
            self.subjects[subject_name].add_grade(grade)
    
        def render_rows(self):
            rows = []
            for subject in self.subjects.values():
                grades_str = ', '.join(str(grade) for grade in subject.grades)
                rows.append(
                    f"<tr><td>{subject.name}</td>"
                    f"<td>{grades_str}</td></tr>"
                )
            return "\n".join(rows) if rows else '<tr><td colspan="3">Пока пусто</td></tr>'
    
    
    def parse_request(request):
        head, _, body = request.partition(b"\r\n\r\n")
        lines = head.decode().split("\r\n")
        method = lines[0].split(" ")[0]
    
        content_length = 0
        for line in lines:
            if "content-length:" in line.lower():
                content_length = int(line.split(":", 1)[1].strip())
    
        return method, body[:content_length].decode()
    
    def html_response():
        html_file = open('index.html')
        html_content = ''.join(html_file.readlines())
        html_file.close()
    
        html_content = html_content.replace("{{ROWS}}", journal.render_rows()).encode()
    
        http_response = (
            'HTTP/1.1 200 OK\r\n'
            'Content-Type: text/html; charset=UTF-8\r\n'
            f'Content-Length: {len(html_content)}\r\n'
            'Connection: close\r\n'
            '\r\n'
        ).encode() + html_content
    
        return http_response
    
    def redirect_response(location="/"):
        return (
            "HTTP/1.1 303 See Other\r\n"
            f"Location: {location}\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
    
    journal = Journal()
    
    while True:
        client_connection, client_address = server_socket.accept()
    
        request = client_connection.recv(4096)
    
        method, body = parse_request(request)
    
        if method == "GET":
            client_connection.sendall(html_response())
        elif method == "POST":
            body = body.split("&")
            subject = body[0].split("=")[1]
            grade = body[1].split("=")[1]
            journal.add_grade(subject, int(grade))
    
            client_connection.sendall(redirect_response().encode())
    ```

??? quote "Код страницы"
    ```html
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Журнал оценок</title>
    </head>
    <body>
        <h1>Журнал оценок</h1>
        <table>
            <tr><th>Дисциплина</th><th>Оценки</th></tr>
            {{ROWS}}
        </table>
    
        <h2>Добавить оценку</h2>
        <form method="POST" action="/submit">
            <label>
                Дисциплина:
                <input name="subject" required>
            </label>
            <label>
                Оценка:
                <input name="grade" type="number" min="1" max="5" required>
            </label>
            <button type="submit">Добавить</button>
        </form>
    </body>
    </html>
    ```

### Примеры работы:
![Screenshot 2026-09-30 at 13.02.15.png](images/Screenshot%202026-09-30%20at%2013.02.15.png)
![Screenshot 2026-09-30 at 13.03.24.png](images/Screenshot%202026-09-30%20at%2013.03.24.png)
![Screenshot 2026-09-30 at 13.03.37.png](images/Screenshot%202026-09-30%20at%2013.03.37.png)




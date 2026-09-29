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
import socket
from threading import Thread


def input_check(message=''):
    # 2. Модифицируйте код сервера таким образом, чтобы он читал строки в цикле до тех пор, пока клиент не введет “exit”.
    # Можно считать, что это команда разрыва соединения со стороны клиента.
    a = input(message)
    if a in ['exit', '/stop']:
        exit()
    return a


connection_alive = True


def receive_messages():
    # Функция для приема сообщений от сервера
    global connection_alive
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            print(data)
        except (ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError) as e:
            connection_alive = False
            print(e)
            break


def send_text(conn, message):
    # Функция для отправки текстового сообщения серверу
    message = message.encode('utf-8')
    conn.send(message)


try:
    # Реализовать безопасный ввод данных и значения по умолчанию.
    print("Для использования настроек по умолчанию ничего не вводите")
    # 4. Модифицируйте код клиента и сервера таким образом, чтобы номер порта и имя хоста (для клиента) они спрашивали у пользователя. 
    host = input_check("Введите имя хоста: ")
    if not host:
        host = '127.0.1.1'
        print(f"Выставили адрес хоста по умолчанию {host}")
    port = input_check(f"Введите порт для {host}: ")
    if not port:
        port = 9000
        print(f"Выставили порт по умолчанию: {port}")
    else:
        port = int(port)
    # Реализовать безопасный ввод данных и значения по умолчанию.
except ValueError:
    print("Неверно указан порт! Попробуйте еще раз!")
try:
    sock = socket.socket()
    sock.connect((host, port))
    print(f"Подключение к {host}:{port} успешно!\n")
except (socket.gaierror, ConnectionRefusedError) as e:
    print(f"Не удается подключиться к {host}:{port} ({e})!")

# Поток для прослушивания информации с сервера
Thread(target=receive_messages, daemon=True).start()

while True:
    while True:
        message = input_check()
        if connection_alive:
            send_text(sock, message)
        else:
            sock.close()
            break

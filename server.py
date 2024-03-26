import json
import random
import socket
from threading import Thread
import logging
import hashlib

# 5. Модифицировать код сервера таким образом, чтобы все служебные сообщения выводились не в консоль, а в специальный лог-файл.
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
                    handlers=[logging.FileHandler("logs/server.log"), logging.StreamHandler()], level=logging.INFO)

USERS = {}
CONNECTIONS_LIST = []
SALT = 'random_salt'.encode('utf-8')
COLORS = ['\33[31m', '\33[32m', '\33[33m', '\33[34m', '\33[35m', '\33[36m', '\33[91m', '\33[92m', '\33[93m', '\33[94m',
          '\33[95m', '\33[96m']


class ClientThread(Thread):
    def __init__(self, connection, address):
        super().__init__(daemon=True)
        self.connected = True
        self.conn = connection
        self.addr = address
        self.username = None
        self.color = random.choice(COLORS)
        self.login()

    def login(self):
        # 7. Реализовать сервер идентификации. 
        self.send_msg('Введите имя пользователя')
        name = self.receive_msg()
        self.username = name
        if name in USERS.keys():
            self.send_msg('Введите пароль')
            if USERS[name]['password'] == get_password_hash(self.receive_msg()):
                self.success_login()
            else:
                self.close_connection('неправильный пароль')
        else:
            self.send_msg('Установите новый пароль')
            USERS.update({name: {'password': get_password_hash(self.receive_msg())}})
            save_users()

    def success_login(self):
        # 7. Реализовать сервер аутентификации. 
        # Успешный вход пользователя
        self.send_msg(f'Вход выполнен успешно')
        save_users()

    def close_connection(self, reason=''):
        # Функция для закрытия соединения с пользователем
        logging.info(f'Соединение закрыто {self.addr} {" - " + reason if reason else ""}')
        self.connected = False
        send_msg_all(f"{self.username} покинул чат")
        if self in CONNECTIONS_LIST:
            CONNECTIONS_LIST.remove(self)

    def send_msg(self, message):
        # Функция для отправки сообщения пользователю
        if self.connected:
            send_text(self.conn, message)

    def receive_msg(self):
        # Функция для получения сообщения от пользователя
        if not self.connected:
            return
        try:
            return receive_text(self.conn)
        except ConnectionResetError:
            self.close_connection('ошибка соединения')

    def run(self):
        # Запуск потока для пользователя
        CONNECTIONS_LIST.append(self)
        self.send_msg(f'{self.username}, добро пожаловать в чат')
        service_msg(self, 'присоединился к чату')

        # 3. Модифицируйте код сервера таким образом, чтобы при разрыве соединения клиентом он продолжал слушать данный порт и,
        # таким образом, был доступен для повторного подключения.
        while True and self.connected:
            message = self.receive_msg()          
            # 2. Модифицируйте код сервера таким образом, чтобы он читал строки в цикле до тех пор, пока клиент не введет “exit”.
            # Можно считать, что это команда разрыва соединения со стороны клиента.
            if message == 'exit':
                self.close_connection('пользователь вышел из чата')
                break
            send_msg_all(f'{self.color}{self.username}\33[0m: {message}')


def save_users():
    # Функция для сохранения пользователей в файл
    with open('users.json', 'w') as f:
        json.dump(USERS, f, indent=4)


def send_msg_all(message):
    # Функция для отправки сообщения всем пользователям
    [i.send_msg(message) for i in CONNECTIONS_LIST]


def service_msg(user, message):
    # Функция для отправки служебного сообщения всем пользователям, кроме определенного пользователя
    [i.send_msg(f'\33[4m{user.username} {message}\33[0m') for i in CONNECTIONS_LIST if i != user]


def get_password_hash(password):
    # Функция для получения хэша пароля
    return hashlib.sha512(password.encode('utf-8') + SALT).hexdigest()

# 8. Напишите вспомогательные функции, которые реализуют отправку и принятие текстовых сообщений в сокет
def receive_text(conn):
    return conn.recv(1024).decode('utf-8')

def send_text(conn, message):
    # Функция для отправки текстового сообщения пользователю
    message = message.encode('utf-8')
    conn.send(message)


if __name__ == '__main__':    # Точка входа в программу
    # 6. Модифицируйте код сервера таким образом, чтобы он автоматически изменял номер порта, если он уже занят. 
    # Сервер должен выводить в консоль номер порта, который он слушает.
    sock = socket.socket()
    port = 9000
    while True:
        try:
            sock.bind(('', port))
            break
        except OSError:
            port += 1
    print(f'Запущено на {socket.gethostbyname(socket.gethostname())}:{port}')
    logging.info(f'Запущено на {socket.gethostbyname(socket.gethostname())}:{port}')
    sock.listen(10)
    try:
        with open('users.json', 'r') as file:
            USERS = json.load(file)
    except json.decoder.JSONDecodeError:
        USERS = {}
    while True:
        # Создание новых потоков для пользователей
        conn, addr = sock.accept()
        print(f'Открыто соединение {addr} ')
        logging.info(f'Открыто соединение {addr} ')
        thread = ClientThread(conn, addr)
        thread.start()

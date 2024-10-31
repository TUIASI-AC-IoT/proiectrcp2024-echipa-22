# Server.py
import socket
import threading


class SocketServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.nicknames = []

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(f'{nickname} a părăsit chat-ul!'.encode('utf-8'))
                self.nicknames.remove(nickname)
                break

    def start(self):
        print("Serverul a pornit și așteaptă conexiuni...")
        while True:
            client, address = self.server.accept()
            print(f"Conectat cu {str(address)}")

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f'Numele clientului este {nickname}!')
            self.broadcast(f'{nickname} s-a alăturat chat-ului!'.encode('utf-8'))
            client.send('Conectat la server!'.encode('utf-8'))

            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()


if __name__ == "__main__":
    server = SocketServer()
    server.start()

# Client.py
import socket
import threading


class SocketClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.nickname = input("Alege un nume: ")

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print("A apărut o eroare!")
                self.client.close()
                break

    def write(self):
        while True:
            message = f'{self.nickname}: {input("")}'
            self.client.send(message.encode('utf-8'))

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()


if __name__ == "__main__":
    client = SocketClient()
    client.start()

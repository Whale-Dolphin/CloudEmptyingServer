import socket

import threading

import config

host = config.HOST
port = config.PORT
log_level = config.LOG_LEVEL
class ChatServer:
    def __init__(self, host, port):
        self.host = "localhost"
        self.port = 5000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.clients = []

    def listen_for_clients(self):
        self.server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New client connected: {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        self.clients.append(client_socket)
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"Received message: {message}")
                    self.broadcast(message, client_socket)
                else:
                    self.remove_client(client_socket)
                    break
            except:
                self.remove_client(client_socket)
                break

    def broadcast(self, message, sender_socket):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode())
                except:
                    self.remove_client(client_socket)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            print(f"Client disconnected: {client_socket.getpeername()}")

if __name__ == "__main__":
    server = ChatServer("localhost", 5000)
    server.listen_for_clients()

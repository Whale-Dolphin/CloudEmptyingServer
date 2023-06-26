import socket
import threading
import cfg
import sqlite3
import utils
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

utils.setup_logging(cfg.LOG_LEVEL)
timestamp = utils.get_timestamp()

@app.route('/users')
def get_users():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    users = []
    for row in rows:
        user = {'id': row[0], 'name': row[1], 'message': row[2]}
        users.append(user)
    db.close()
    return jsonify(users)

if __name__ == '__main__':
    app.run()

class ChatServer:
    def __init__(self, host, port):
        self.host = "localhost"
        self.port = 11454
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
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, message TEXT)')

        # Read from database
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        # Write to database
        cursor.execute('INSERT INTO users (name, message) VALUES (?, ?)', ('Alice', 'Hello, world!'))
        db.commit()

        # Handle client messages
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    self.broadcast(message, client_socket)
                else:
                    self.remove_client(client_socket)
                    break
            except:
                self.remove_client(client_socket)
                break

        # Close database connection
        cursor.close()
        db.close()

    def broadcast(self, message, sender_socket):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode())
                except:
                    self.remove_client(client_socket)

    def remove_client(self, client_socket):
        self.clients.remove(client_socket)
        print(f"Client disconnected: {client_socket.getpeername()}")

if __name__ == "__main__":
    server = ChatServer("localhost", 5000)
    server.listen_for_clients()
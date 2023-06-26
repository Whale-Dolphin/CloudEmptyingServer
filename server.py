import socket
import threading
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# @app.route('/')
# def index():
#     return 'Hello, World!'

db = sqlite3.connect('users.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, message TEXT)')
db.commit()

clients = []

@app.route('/users')
def get_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    users = []
    for row in rows:
        user = {'id': row[0], 'name': row[1], 'message': row[2]}
        users.append(user)
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    name = request.json['name']
    message = request.json['message']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, message) VALUES (?, ?)', (name, message))
    conn.commit()
    conn.close()
    return jsonify({'message': 'User added successfully'})

@socketio.on('connect')
def handle_connect():
    print(f"New client connected: {request.namespace.socket.sessid}")
    clients.append(request.namespace.socket.sessid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.namespace.socket.sessid}")
    clients.remove(request.namespace.socket.sessid)

@socketio.on('message')
def handle_message(data):
    message = data['message']
    name = data['name']

    # Write to database
    cursor.execute('INSERT INTO users (name, message) VALUES (?, ?)', (name, message))
    db.commit()

    # Broadcast message to all clients
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=11454)

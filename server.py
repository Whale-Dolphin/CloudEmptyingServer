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
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, account TEXT, password TEXT)')
db.commit()

clients = []

import smtplib
import random

@app.before_request
def log_request_info():
    # app.logger.debug('Request Headers: %s', request.headers)
    # app.logger.debug('Request Body: %s', request.get_data())
    print('Request Headers: %s', request.headers)
    print('Request Body: %s', request.get_data())

@app.route('/users')
def get_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    users = []
    for row in rows:
        user = {'account': row[0], 'name': row[1], 'message': row[2]}
        users.append(user)
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    account = request.form.get('account')
    password = request.form.get('password')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (account, password) VALUES (?, ?)', ((account, password)))
    conn.commit()
    conn.close()
    success = 1
    return jsonify({'success': success})

@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    email = request.form.get('email')
    code = str(random.randint(100000, 999999))
    sender_email = 'cloud_emptying@163.com'
    sender_password = 'KFNGWDEVBLAHUZVI'
    receiver_email = email
    message = 'Subject: Verification Code\n\nYour verification code is: ' + code
    server = smtplib.SMTP('smtp.163.com', 25)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()
    return code

@app.route('/test', methods=['POST'])
def test():
    return jsonify({'message': 'success'})

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
    socketio.run(app, host='192.168.31.229', port=11454)
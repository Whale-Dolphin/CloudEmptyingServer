import socket
import threading
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

engine = create_engine('sqlite:///users.db')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    account = Column(String)
    password = Column(String)
    nickname = Column(String)
    merit = Column(Integer)

Base.metadata.create_all(engine)

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
    nickname = request.form.get('nickname')
    session = Session()
    user = User(account=account, password=password,nickname=nickname, merit=0)
    session.add(user)
    session.commit()
    session.close()

    success = 1
    return jsonify({'success': success})

@app.route('/rename', methods=['POST'])
def rename():
    account = request.form.get('account')
    nickname = request.form.get('nickname')
    session = Session()
    user = session.query(User).filter_by(account=account).first()
    user.nickname = nickname
    session.commit()
    session.close()
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    account = request.form.get('account')
    password = request.form.get('password')

    session = Session()
    user = session.query(User).filter_by(account=account, password=password).first()
    session.close()

    if user:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid account or password'})

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

if __name__ == '__main__':
    socketio.run(app, host='192.168.31.229', port=11455)
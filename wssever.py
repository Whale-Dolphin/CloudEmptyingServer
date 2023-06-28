import asyncio
import websockets
import json
import sqlite3
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import query
from sqlalchemy.orm import declarative_base

clients = []

Base = declarative_base()
# 定义映射到 users 表的 SQLAlchemy 模型
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String)

# 创建数据库引擎和会话工厂
engine = create_engine('sqlite:///user.db')
Session = sessionmaker(bind=engine)

async def handle_handshake(websocket, path):
    print(f'New client connected: {websocket.remote_address}')

    clients.append(websocket)

    try:
        async for message in websocket:
            await handle_json(websocket, message)
    except websockets.exceptions.ConnectionClosedError:
        pass

    clients.remove(websocket)
    print(f'Client disconnected: {websocket.remote_address}')

async def handle_json(websocket, message):
    data = json.loads(message)
    type = data.get('type')
    if type == 0:
        await handle_online(websocket, message)
    elif type == 1:
        await handle_message(websocket, message)
    # 记得检查一下客户端传来的文件格式
    
async def handle_online(websocket,message):
    data = json.loads(message)
    id = data.get('id')
    nickname = data.get('nickname')
    data = {'id': id, 'nickname': nickname}
    for client in clients:
        if client != websocket and client.open:
            await client.send(json.dumps(data))

async def handle_message(websocket,message):
    data = json.loads(message)
    id = data.get('id')
    message = data.get('message')
    data = {'id': id, 'message': message}
    for client in clients:
        if client != websocket and client.open:
            await client.send(json.dumps(data))


async def main():
    async with websockets.serve(handle_handshake, "192.168.31.229", 11454):
        await asyncio.Future()

asyncio.run(main())
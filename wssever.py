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
import websockets.exceptions
import websockets.server

clients = []
client_online = []

engine = create_engine('sqlite:///users.db')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    account = Column(String,primary_key=True)
    password = Column(String)
    nickname = Column(String)
    merit = Column(Integer)

Base.metadata.create_all(engine)

type_online = -1
account_online = ''
nickname_online = ''
message_online = ''
send_json= [type_online, account_online, nickname_online, message_online]

async def handle_handshake(websocket, path):
    
    global client_online

    print(f'New client connected: {websocket.remote_address}')

    clients.append(websocket)

    try:
        async for message in websocket:
            # print('test')
            await handle_json(websocket, message)
    
    except websockets.exceptions.ConnectionClosed:
        print('test')
        # 客户端断开连接，从 client_online 列表中删除该客户端对应的用户信息
        for client in clients:
            if client != websocket :
                client_offline = [client for client in client_online if client['websocket_online'] == websocket]
                send_list = []
                for item in client_offline:
                    send_list.append({'type_online': 1, 'account_online': item['account_online'], 'nickname_onine': item['nickname_online'], 'message_online': ''})
                print(send_list)
                await client.send(json.dumps(send_list))
            if client == websocket:
                print('test')
                clients.remove(client)
                client_online = [client for client in client_online if client['websocket_online'] != websocket]
                print(client_online)
    
    print(f'Client disconnected: {websocket.remote_address}')

async def handle_json(websocket, message):
    data = json.loads(message)
    print(message)
    print(f'Received message from client: {data}')
    # client_online.append({'account': data.get('account'), 'nickname': get_nickname_from_account(data.get('account')) , 'websocket': websocket})
    # print('test')
    type_online = data.get('type_online')
    if type_online == 0:
        await handle_online(websocket, message)
    elif type_online == 1:
        await handle_message(websocket, message)
    # 记得检查一下客户端传来的文件格式
    
async def handle_online(websocket, message):
    data = json.loads(message)
    account = data.get('account_online')
    nickname = get_nickname_from_account(account)
    client_online.append({'account_online': account, 'nickname_online': nickname, 'websocket_online': websocket})
    data = {'id': id, 'nickname': nickname}
    # print('test')
    for client in clients:
        if client != websocket and client.open:
            # await client.send(json.dumps(data))
            send_list = []
            send_list.append({'type_online': 3, 'account_online': account, 'nickname_online': nickname, 'message_online': ''})
            send_json = json.dumps(send_list)
            await client.send(send_json)
        if client == websocket and client.open:
            print(client_online)
            client_online_except_me = [{'account': client['account_online'], 'nickname': client['nickname_online']} for client in client_online if client['websocket_online'] != websocket]
            print(client_online_except_me)
            new_list = [{'account': client['account'], 'nickname': client['nickname']} for client in client_online_except_me]
            send_list = []
            for item in new_list:
                send_list.append({'type_online': 0, 'account_online': item['account'], 'nickname_online': item['nickname'], 'message_online': ''})
            # print(send_list)
            send_json = json.dumps(send_list)
            await client.send(send_json)

def get_nickname_from_account(account):
    session = Session()
    user = session.query(User).filter_by(account=account).first()
    session.close()
    if user:
        return user.nickname
    else:
        return '0'

async def handle_message(websocket,message):
    data = json.loads(message)
    account = data.get('account_online')
    message = data.get('message_online')
    # data = {'account': account, 'message': message}
    # send_json = {'type_server': 0, 'users_online': '', 'account_client': account, 'message_client': message}
    # for client in clients:
    #     if client != websocket and client.open:
    #         await client.send(json.dumps(send_json))
    send_list = []
    send_list.append({'type_online': 2, 'account_online': account, 'nickname_online': '', 'message_online': message})
    send_json = json.dumps(send_list)
    for client in clients:
        if client != websocket and client.open:
            await client.send(send_json)

async def main():
    async with websockets.serve(handle_handshake, "192.168.31.229", 11454):
        await asyncio.Future()

asyncio.run(main())
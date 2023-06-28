import asyncio
import websockets

loop = asyncio.get_event_loop()

# 存储客户端连接的列表
clients = []

async def handle_client(websocket, path):
    print(f'New client connected: {websocket.remote_address}')

    clients.append(websocket)

    try:
        async for message in websocket:
            for client in clients:
                if client != websocket and client.open:
                    await client.send(message)
    except websockets.exceptions.ConnectionClosedError:
        pass

    clients.remove(websocket)
    print(f'Client disconnected: {websocket.remote_address}')

async def main():
    async with websockets.serve(handle_client, "127.0.0.1", 11454):
        await asyncio.Future() 

asyncio.run(main())
# CloudEmptying README

# 服务器结构

服务器采用python编写，使用了websocket和falsk，两个服务器分别存储在falskapp.py和wsserver,py中，两者的运行代码均在文件最后，使用时需要根据需要把ip改成服务器ip

# 接口列表（基于flask，需使用post命令）

| 接口名称 | 传入值 | 返回值 | 备注 |
| --- | --- | --- | --- |
| /addusers | account(int),password(string),nickname(string) | success(json) |  |
| /rename | account(int),nickname(string) | success(json) |  |
| /login | account(int),password(string) | success(json.true),Invalid account or password(json.false) |  |
| /send_verification_code | email(string) | code(int) |  |

# 基于ws服务器的功能

目前服务器主要实现了两个功能，一个是登录转发，登录以后会告诉所有的客户端该用户已上线，第二个是消息转发，在聊天框内发送的消息会被转发给所有其他客户端

服务器接受的json文件遵循以下格式

type:0表示登录请求，1表示消息请求

account:用户邮箱

message:用户的消息
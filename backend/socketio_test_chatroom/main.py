# main.py (socketio_test_chatroom)
import asyncio
from typing import Dict, Any, Callable
import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from message_handler import handle_message
from log_config import logger, set_current_username, clear_current_username
from functools import wraps
import traceback

# Store for persistent data
persistent_data: Dict[str, Dict[str, Any]] = {}

# Set up the Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()

def with_user_context(func: Callable):
    @wraps(func)
    async def wrapper(sid, *args, **kwargs):
        user_data = persistent_data.get(sid, {})
        username = user_data.get('username', f"User_{sid[:4]}")
        set_current_username(username)
        try:
            result = await func(sid, username, user_data, *args, **kwargs)
            persistent_data[sid] = user_data  # Save any changes back to persistent_data
            return result
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            logger.error(f"Error for user {username}: {error_message}\n{traceback.format_exc()}")
            await sio.emit('error_message', {'message': error_message}, room=sid)
        finally:
            clear_current_username()
    return wrapper

@sio.event
@with_user_context
async def connect(sid, username, user_data, environ):
    user_data['username'] = username
    user_data['message_count'] = 0
    logger.info("User connected")
    await sio.emit('status', {'message': f'{username} has joined the chat'}, room=None)

@sio.event
@with_user_context
async def disconnect(sid, username, user_data):
    message_count = user_data.get('message_count', 0)
    logger.info(f"User disconnected. Total messages: {message_count}")
    await sio.emit('status', {'message': f'{username} has left the chat'}, room=None)
    persistent_data.pop(sid, None)

@sio.event
@with_user_context
async def chat_message(sid, username, user_data, data):
    message_count = user_data.get('message_count', 0)
    new_message_count = await handle_message(data, username, message_count, sio.emit)
    user_data['message_count'] = new_message_count

socket_app = socketio.ASGIApp(sio, app)

# Serve a simple HTML page for the chat interface
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Socket.IO Chat</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <style>
            .error {
                color: red;
                font-weight: bold;
            }
        </style>
        <script type="text/javascript" charset="utf-8">
            var socket = io();
            socket.on('connect', function() {
                console.log('Connected to server');
            });
            socket.on('status', function(data) {
                var p = document.createElement('p');
                p.innerHTML = data.message;
                document.getElementById('chat').appendChild(p);
            });
            socket.on('chat_message', function(data) {
                var p = document.createElement('p');
                p.innerHTML = data.username + ': ' + data.message;
                document.getElementById('chat').appendChild(p);
            });
            socket.on('error_message', function(data) {
                var p = document.createElement('p');
                p.className = 'error';
                p.innerHTML = 'Error: ' + data.message;
                document.getElementById('chat').appendChild(p);
                console.error('Received error:', data.message);
                socket.disconnect();
            });
            function sendMessage() {
                var message = document.getElementById('message').value;
                socket.emit('chat_message', message);
                document.getElementById('message').value = '';
            }
        </script>
    </head>
    <body>
        <h1>Socket.IO Chat</h1>
        <div id="chat"></div>
        <input type="text" id="message" autocomplete="off" /><button onclick="sendMessage()">Send</button>
    </body>
    </html>
    """

# Run the server
if __name__ == '__main__':
    uvicorn.run(socket_app, host='127.0.0.1', port=8000)
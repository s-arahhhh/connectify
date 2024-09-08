# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
socketio = SocketIO(app)

# Route for joining a room
@app.route('/<room>')
def index(room):
    return render_template('index.html', room=room)

# Handle chat messages and broadcast them to the room
@socketio.on('message')
def handle_message(data):
    send(data['msg'], to=data['room'])

# Handle user joining a room
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    send(f"{data['username']} has joined the room.", to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)

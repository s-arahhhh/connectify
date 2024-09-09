from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Store rooms and users
rooms = {}

@app.route('/')
def index():
    return render_template('index4.html')

@app.route('/create-room', methods=['POST'])
def create_room():
    room_id = str(len(rooms) + 1)
    rooms[room_id] = {'users': []}
    return jsonify({'room_id': room_id})

@app.route('/join-room', methods=['POST'])
def join_room():
    room_id = request.json.get('room_id')
    if room_id in rooms:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 404

@socketio.on('join')
def handle_join(data):
    room_id = data['room_id']
    username = data['username']
    if room_id in rooms:
        rooms[room_id]['users'].append(username)
        emit('status', {'msg': f'{username} has joined the room.'}, room=room_id)
        emit('update_users', {'users': rooms[room_id]['users']}, room=room_id)
    else:
        emit('status', {'msg': 'Room not found.'})

@socketio.on('leave')
def handle_leave(data):
    room_id = data['room_id']
    username = data['username']
    if room_id in rooms and username in rooms[room_id]['users']:
        rooms[room_id]['users'].remove(username)
        emit('status', {'msg': f'{username} has left the room.'}, room=room_id)
        emit('update_users', {'users': rooms[room_id]['users']}, room=room_id)

@socketio.on('message')
def handle_message(data):
    room_id = data['room_id']
    message = data['message']
    emit('message', {'message': message}, room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)

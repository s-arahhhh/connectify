document.addEventListener('DOMContentLoaded', () => {
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    const createRoomButton = document.getElementById('create-room');
    const joinRoomButton = document.getElementById('join-room');
    const sendMessageButton = document.getElementById('send-message');
    const chatLog = document.getElementById('chat-log');
    const chatInput = document.getElementById('chat-input');
    const roomIdDisplay = document.getElementById('room-id');
    const userList = document.getElementById('user-list');
    const joinRoomId = document.getElementById('join-room-id');
    const usernameInput = document.getElementById('username');

    let currentRoomId = null;

    createRoomButton.addEventListener('click', () => {
        fetch('/create-room', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                roomIdDisplay.textContent = `Room ID: ${data.room_id}`;
                currentRoomId = data.room_id;
            });
    });

    joinRoomButton.addEventListener('click', () => {
        const roomId = joinRoomId.value;
        const username = usernameInput.value;
        fetch('/join-room', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room_id: roomId })
        })
        .then(response => {
            if (response.ok) {
                currentRoomId = roomId;
                socket.emit('join', { room_id: roomId, username: username });
            } else {
                alert('Room not found');
            }
        });
    });

    sendMessageButton.addEventListener('click', () => {
        const message = chatInput.value;
        if (message && currentRoomId) {
            socket.emit('message', { room_id: currentRoomId, message: message });
            chatInput.value = '';
        }
    });

    socket.on('message', (data) => {
        if (data.message) {
            chatLog.value += data.message + '\n';
        }
    });

    socket.on('status', (data) => {
        if (data.msg) {
            chatLog.value += data.msg + '\n';
        }
    });

    socket.on('update_users', (data) => {
        userList.innerHTML = '';
        data.users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user;
            userList.appendChild(li);
        });
    });
});

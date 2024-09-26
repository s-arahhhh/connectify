// Date and Time Script
function updateTime() {
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const date = now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });

    document.getElementById('time').innerText = time;
    document.getElementById('date').innerText = date;
}
setInterval(updateTime, 1000);

// To-Do List Functionality
let tasks = [];

function addTask() {
    const taskInput = document.getElementById('new-task');
    const taskText = taskInput.value;

    if (taskText.trim()) {
        tasks.push(taskText);
        updateTodoList();
        taskInput.value = '';
    }
}

function updateTodoList() {
    const listElement = document.getElementById('todo-list');
    listElement.innerHTML = '';

    tasks.forEach((task, index) => {
        const listItem = document.createElement('li');
        listItem.innerText = task;

        const deleteButton = document.createElement('button');
        deleteButton.innerText = 'Delete';
        deleteButton.onclick = () => {
            tasks.splice(index, 1);
            updateTodoList();
        };

        listItem.appendChild(deleteButton);
        listElement.appendChild(listItem);
    });
}

// Timer Functionality
let timer;
let minutes = 25;
let seconds = 0;

function startTimer() {
    timer = setInterval(function () {
        if (seconds === 0) {
            if (minutes === 0) {
                clearInterval(timer);
            } else {
                minutes--;
                seconds = 59;
            }
        } else {
            seconds--;
        }

        document.getElementById('minutes').innerText = String(minutes).padStart(2, '0');
        document.getElementById('seconds').innerText = String(seconds).padStart(2, '0');
    }, 1000);
}

function resetTimer() {
    clearInterval(timer);
    minutes = 25;
    seconds = 0;
    document.getElementById('minutes').innerText = '25';
    document.getElementById('seconds').innerText = '00';
}

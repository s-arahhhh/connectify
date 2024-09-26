from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from urllib.parse import unquote
from config import Config
from models import db, Message

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(app)

def create_tables():
    with app.app_context():
        db.create_all()

#-------

@app.route("/")
def home():
    return render_template("index.html", rooms=rooms)

rooms = {
    'introduction to computing tech': {'members': 0, 'messages': []},
    'problem solving & design': {'members': 0, 'messages': []},
    'mini it project': {'members': 0, 'messages': []},
    'maths 1': {'members': 0, 'messages': []},
    'maths 2': {'members': 0, 'messages': []},
    'maths 3': {'members': 0, 'messages': []},
    'introduction to digital systems': {'members': 0, 'messages': []},
    'principles of physics': {'members': 0, 'messages': []},
    'introduction to business management': {'members': 0, 'messages': []},
    'critical thinking': {'members': 0, 'messages': []},
    'multimedia fundamentals': {'members': 0, 'messages': []},
    'communicative english': {'members': 0, 'messages': []},
    'essential english': {'members': 0, 'messages': []},
    'academic english': {'members': 0, 'messages': []},
}


@app.route('/subject/<subject_name>')
def subject(subject_name):
    subject_info = {
        'introduction to computing tech': 'An overview of fundamental computing technologies...',
        'problem solving & design': 'Focuses on developing problem-solving skills...',
        'mini it project': 'A practical course where students apply their knowledge...',
        'maths 1': 'Covers foundational mathematical concepts...',
        'maths 2': 'Continues from Maths 1 with a focus on advanced topics...',
        'maths 3': 'Expands on previous mathematics courses...',
        'introduction to digital systems': 'Introduces the fundamentals of digital systems...',
        'principles of physics': 'Provides a foundation in classical physics...',
        'introduction to business management': 'Covers basic principles of management...',
        'critical thinking': 'Focuses on developing analytical and evaluative skills...',
        'multimedia fundamentals': 'Explores the core concepts of multimedia technology...',
        'communicative english': 'Aims to improve students proficiency in English...',
        'essential english': 'Focuses on developing basic English language skills...',
        'academic english': 'Enhances advanced English language skills needed for academic success...'
    }

    normalized_subject_name = subject_name.lower()
    info = subject_info.get(normalized_subject_name, 'No information available')

    display_name = ' '.join(word.capitalize() for word in normalized_subject_name.split())

    return render_template('subject.html',
                           subject_name=display_name,
                           subject_info=info,
                           subject_description="Description of " + display_name)

@app.route("/chat/<subject_name>", methods=["POST", "GET"])
def chat(subject_name):
    subject_name = unquote(subject_name).lower()

    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("chat.html", subject_name=subject_name, error="Please enter a nickname.")
        
        session["room"] = subject_name
        session["name"] = name
        return redirect(url_for("chat_room", subject_name=subject_name))

    if session.get("room") == subject_name and session.get("name"):
        return redirect(url_for("chat_room", subject_name=subject_name))

    return render_template("chat.html", subject_name=subject_name)

@app.route("/chatroom/<subject_name>")
def chat_room(subject_name):
    room = session.get("room")
    name = session.get("name")

    if not room or room != subject_name or not name:
        return redirect(url_for("chat", subject_name=subject_name))

    messages = Message.query.filter_by(room=subject_name).all()
    return render_template("chat.html", subject_name=subject_name, room=subject_name, messages=messages)

@socketio.on("message")
def handle_message(data):
    room = session.get("room")
    if room:
        content = {
            "name": session.get("name"),
            "message": data["data"]
        }
        emit("message", content, room=room)

        message = Message(username=session.get("name"), content=data["data"], room=room)
        db.session.add(message)
        db.session.commit()

@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")
    if room and name:
        join_room(room)
        emit("message", {"name": name, "message": "has entered the room"}, room=room)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")

    if room and name:
        leave_room(room)
        emit("message", {"name": name, "message": "has left the room"}, room=room)

if __name__ == "__main__":
    create_tables()
    socketio.run(app, debug=True)

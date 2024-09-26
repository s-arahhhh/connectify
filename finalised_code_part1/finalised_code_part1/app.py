from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from urllib.parse import unquote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed  # Add this line
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, validators
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from flask_bcrypt import Bcrypt
from datetime import datetime
import sqlite3
import os
import random
import string


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class UploadForm(FlaskForm):
    file = FileField('Upload File', validators=[FileAllowed(['jpg', 'png', 'mp4'], 'Images and videos only!')])
    submit = SubmitField('Upload')


class Message(db.Model):
    __tablename__ = 'chat_messages'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    room = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id}>'

def init_db():
    with app.app_context():  
        db.create_all()  

init_db()  

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@login_manager.user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class FeedbackForm(FlaskForm):
    rating = IntegerField(validators=[InputRequired(), NumberRange(min=1, max=5)])
    comments = TextAreaField(validators=[Length(max=500)])
    submit = SubmitField('Submit Feedback')

def init_user_profiles_db():
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY,
            about TEXT,
            age INTEGER CHECK(age BETWEEN 16 AND 40),
            gender TEXT CHECK(gender IN ('Male', 'Female')),
            status TEXT CHECK(status IN ('Single', 'Taken', 'Heartbroken', 'Not Available')),
            watch_list TEXT,
            likes TEXT,
            dislikes TEXT,
            emoji TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER NOT NULL,
            comments TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, 
            path TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def save_feedback(rating, comments):
    conn = sqlite3.connect("user_profiles.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (rating, comments) VALUES (?, ?)', (rating, comments))
    conn.commit()
    cursor.close()
    conn.close()

def save_file_metadata(name, path):
    conn = sqlite3.connect("user_profiles.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO my_table (name, path) VALUES (?, ?)", (name, path))
    conn.commit()
    cursor.close()
    conn.close()

def get_uploaded_files():
    conn = sqlite3.connect("user_profiles.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM my_table")
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    return files

emoji_options = ['😀', '😂', '😍', '😎', '🥳', '🤩', '🥺', '😡', '👽']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return {"code": room_code}

@app.route('/join_room', methods=['GET', 'POST'])
def join_room_view():
    if request.method == 'POST':
        room_code = request.form['room_code']
        session['room'] = room_code
        return redirect(url_for('chat_room', room_code=room_code))
    return render_template('join_room.html') 
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profiles WHERE id=1")
    user_data = cursor.fetchone()
    conn.close()
    return render_template('profile.html', user_data=user_data, editable=False, emoji_options=emoji_options)

@app.route('/edit', methods=['GET'])
def edit_profile():
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profiles WHERE id=1")
    user_data = cursor.fetchone()
    conn.close()
    return render_template('profile.html', user_data=user_data, editable=True, emoji_options=emoji_options)

@app.route('/save', methods=['POST'])
def save_profile():
    about = request.form.get('about', '')
    age = request.form.get('age', type=int)
    gender = request.form.get('gender', '')
    status = request.form.get('status', '')
    watch_list = request.form.get('watch_list', '')
    likes = request.form.get('likes', '')
    dislikes = request.form.get('dislikes', '')
    emoji = request.form.get('emoji', '')

    if age < 16 or age > 40 or gender not in ['Male', 'Female'] or status not in ['Single', 'Taken', 'Heartbroken', 'Not Available']:
        return "Invalid input", 400

    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_profiles 
        (id, about, age, gender, status, watch_list, likes, dislikes, emoji)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (about, age, gender, status, watch_list, likes, dislikes, emoji))
    conn.commit()
    conn.close()

    return redirect(url_for('profile'))

@app.route('/feedback', methods=["GET", "POST"])
def feedback():
    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        rating = feedback_form.rating.data
        comments = feedback_form.comments.data
        save_feedback(rating, comments)
        return redirect(url_for('thank_you'))
    return render_template('feedback.html', feedback_form=feedback_form)

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/studyspace')
def studyspace():
    return render_template('studyspace.html', rooms=rooms)

@app.route('/studybuddy/<subject_name>')
def studybuddy(subject_name):
    return render_template('studybuddy.html', subject_name=subject_name)

@app.route('/study_alone/<subject_name>')
def study_alone(subject_name):
    return render_template('study_alone.html', subject_name=subject_name)

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
                           subject_description="Description of " + display_name,
                           join_chat_link=url_for('library')) 
@app.route('/chat/<subject_name>', methods=['GET', 'POST'])
def chat(subject_name):
    if request.method == 'POST':
        name = request.form.get('name')
        session['name'] = name
        session['room'] = subject_name
        return redirect(url_for('chatroom', subject_name=subject_name))  

    messages = Message.query.filter_by(room=subject_name).all()
    return render_template('chat.html', subject_name=subject_name, messages=messages)

@app.route("/chatroom/<subject_name>")
def chatroom(subject_name):
    room = session.get("room")
    name = session.get("name")

    if not room or room != subject_name or not name:
        return redirect(url_for("chat", subject_name=subject_name))

    messages = Message.query.filter_by(room=subject_name).all()
    return render_template("chat.html", subject_name=subject_name, messages=messages)


@app.route('/library')
def library():
    return render_template('library.html')


@socketio.on("message")
def handle_message(data):
    room_code = session.get("room")
    if room_code:
        content = {
            "name": session.get("name"),
            "message": data["message"]
        }
        emit("message", content, room=room_code)

        message = Message(username=session.get("name"), content=data["message"], room=room_code)
        db.session.add(message)
        db.session.commit()

@socketio.on("connect")
def connect():
    room_code = session.get("room")
    name = session.get("name")
    if room_code and name:
        join_room(room_code)
        emit("message", {"name": name, "message": "has entered the room"}, room=room_code)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")

    if room and name:
        leave_room(room)
        emit("message", {"name": name, "message": "has left the room"}, room=room)


@app.route('/upload', methods=["GET", "POST"])
def upload():
    upload_form = UploadForm()  
    if upload_form.validate_on_submit():
        file = upload_form.file.data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        try:
            file.save(filepath)
            save_file_metadata(name=file.filename, path=filepath)
            return redirect(url_for('upload'))
        except Exception as e:
            print("Error uploading file:", e)

    files = get_uploaded_files()
    return render_template('upload.html', upload_form=upload_form, files=files)

@app.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    return render_template('upload_file.html') 


@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app, debug=True)

from fileinput import filename
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, validators
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from flask_bcrypt import Bcrypt
import sqlite3
import os

# App configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Flask-login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model for Flask-login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

# Register form
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

# Login form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

# Rating form
class RatingsForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    opinion = TextAreaField('Opinion', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Feedback form
class FeedbackForm(FlaskForm):
    rating = IntegerField("Rating (1 to 5)", [validators.InputRequired(), validators.NumberRange(min=1, max=5)])
    comments = TextAreaField("Comments")
    submit = SubmitField("Submit")

# Upload form
class UploadForm(FlaskForm):
    file = FileField("File", [validators.DataRequired()])
    submit = SubmitField("Submit")

# Initialize SQLite databases
def init_db():
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    # User profiles
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
    # Feedback and uploads
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

# Save feedback into the database
def save_feedback(rating, comments):
    conn = sqlite3.connect("user_profiles.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (rating, comments) VALUES (?, ?)', (rating, comments))
    conn.commit()
    cursor.close()
    conn.close()

# Save file metadata into the database
def save_file_metadata(name, path):
    conn = sqlite3.connect("user_profiles.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO my_table (name, path) VALUES (?, ?)", (name, path))
    conn.commit()
    cursor.close()
    conn.close()

# Get uploaded files
def get_uploaded_files():
    conn = sqlite3.connect("user_profiles.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM my_table")
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    return files

# Emoji options for profile
emoji_options = ['😀', '😂', '😍', '😎', '🥳', '🤩', '🥺', '😡', '👽']

@app.route('/')
def index():
    return render_template('index.html')

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
    return render_template('studyspace.html')

@app.route('/upload', methods=["GET", "POST"])
def upload():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        file = upload_form.file.data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        try:
            file.save(filepath)
            save_file_metadata(name=file.filename, path=filepath)  # Use file.filename
            return redirect(url_for('upload'))
        except Exception as e:
            print("Error uploading file:", e)

    files = get_uploaded_files()  # Get the list of uploaded files
    return render_template('upload.html', upload_form=upload_form, files=files)


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

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5002)

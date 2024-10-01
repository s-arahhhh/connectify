from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
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
    conn.commit()
    conn.close()

init_db()

# Emoji options
emoji_options = ['😀', '😂', '😍', '😎', '🥳', '🤩', '🥺', '😡', '👽']

@app.route('/')
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

if __name__ == '__main__':
    app.run(debug=True)

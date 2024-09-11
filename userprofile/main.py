from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

user_data = {
    "about": "",
    "age": "",
    "gender": "",
    "status": "",
    "watch_list": "",
    "likes": "",
    "dislikes": "",
    "avatar": "default_avatar.png"
}

@app.route('/')
def profile():
    return render_template('profile.html', user_data=user_data, editable=False)

@app.route('/edit', methods=['GET'])
def edit_profile():
    return render_template('profile.html', user_data=user_data, editable=True)

@app.route('/save', methods=['POST'])
def save_profile():
    user_data['about'] = request.form.get('about', '')
    user_data['age'] = request.form.get('age', '')
    user_data['gender'] = request.form.get('gender', '')
    user_data['status'] = request.form.get('status', '')
    user_data['watch_list'] = request.form.get('watch_list', '')
    user_data['likes'] = request.form.get('likes', '')
    user_data['dislikes'] = request.form.get('dislikes', '')
    return redirect(url_for('profile'))

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        return redirect(url_for('profile'))
    file = request.files['avatar']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user_data['avatar'] = filename
    return redirect(url_for('profile'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

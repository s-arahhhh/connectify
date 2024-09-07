from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

user_data = {
    "test"
}

@app.route('/')
def profile():
    return render_template('profile.html', user_data=user_data, editable=False)

@app.route('/edit', methods=['GET'])
def edit_profile():
    return render_template('profile.html', user_data=user_data, editable=True)

@app.route('/save', methods=['POST'])
def save_profile():
    user_data['about'] = request.form['about']
    user_data['age'] = request.form['age']
    user_data['gender'] = request.form['gender']
    user_data['status'] = request.form['status']
    user_data['watch_list'] = request.form['watch_list']
    user_data['likes'] = request.form['likes']
    user_data['dislikes'] = request.form['dislikes']
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)

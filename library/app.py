from flask import Flask, redirect, url_for, request, render_template, send_file
from io import BytesIO
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField
import sqlite3

print("All Modules Loaded .... ")

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"


class UploadForm(FlaskForm):
    file = FileField()
    submit = SubmitField("Submit")
    download = SubmitField("Download")


def database(name, data):
    conn = sqlite3.connect("pdf.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS my_table (name TEXT, data BLOB)""")
    cursor.execute("""INSERT INTO my_table (name, data) VALUES (?, ?)""", (name, data))

    conn.commit()
    cursor.close()
    conn.close()


@app.route('/', methods=["GET", "POST"])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        file_name = form.file.data
        database(name=file_name.filename, data=file_name.read())
        return render_template('home.html', form=form)

    return render_template('home.html', form=form)


@app.route('/download', methods=["GET", "POST"])
def download():
    form = UploadForm()
    if form.validate_on_submit() and form.download.data:
        conn = sqlite3.connect("pdf.db")
        cursor = conn.cursor()
        c = cursor.execute("""SELECT * FROM my_table""")

        for x in c.fetchall():
            name_v = x[0]
            data_v = x[1]
            break

        conn.commit()
        cursor.close()
        conn.close()

        return send_file(BytesIO(data_v), attachment_filename=name_v, as_attachment=True)

    return render_template('home.html', form=form)


if __name__ == "__main__":
    app.run(port=5001, debug=True)

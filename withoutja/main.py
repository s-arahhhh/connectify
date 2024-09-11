from flask import Flask, render_template, request, session, redirect, url_for
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "whywesuffer"

rooms = {}

def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join")
        create = request.form.get("create")

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code)

        if join and not code:
            return render_template("home.html", error="Please enter a room code.", code=code)

        if create:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif join:
            room = code
            if room not in rooms:
                return render_template("home.html", error="Room does not exist.", code=code)
        else:
            return render_template("home.html", error="Invalid action.", code=code)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("loading"))

    return render_template("home.html")

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/chat", methods=["POST", "GET"])
def chat():
    room = session.get("room")
    name = session.get("name")
    if room is None or name is None or room not in rooms:
        return redirect(url_for("home"))

    if request.method == "POST":
        message = request.form.get("message")
        if message:
            rooms[room]["messages"].append({"name": name, "message": message})

    return render_template("chat.html", code=room, messages=rooms[room]["messages"])


@app.route("/chat", methods=["POST", "GET"])
def chat():
    room = session.get("room")
    name = session.get("name")
    if room is None or name is None or room not in rooms:
        return redirect(url_for("home"))

    if request.method == "POST":
        message = request.form.get("message")
        if message:
            rooms[room]["messages"].append({"name": name, "message": message})

    return render_template("chat.html", code=room, messages=rooms[room]["messages"])
@app.route("/loading")
def loading():
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(debug=True)

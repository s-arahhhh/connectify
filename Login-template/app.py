import sqlite3
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/submit_details', methods=['GET', 'POST'])     #get and post because we want to post the data to the function of the page 
def submit_details():                                       #submit_details will be used to post data from our form and save to the local database
    return redirect(url_for('index'))

@app.route('/view_contacts', methods=['GET'])                      #used to get all the contacts, pass them to the contacts.html and display them to check our database is working
def view_contacts():
    return render_template('contacts.html')

if __name__ == "__main__":
    app.run(debug=True)
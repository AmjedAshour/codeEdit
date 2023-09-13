from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import uuid
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
socket = SocketIO(app)
mysql = MySQL(app)

app.config['SECRET_KEY'] = 'qwertyhajsdm1j2378asdnjk123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'chatapp'



connected_users = {}

language = None


@app.route('/',methods=['GET','POST'])
def login():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        username_result = cur.fetchone()
        if username_result:
            return redirect(url_for('editor',username= username))
        else:
            flash('Incorrect username/password!')
    return render_template('login.html')

@app.route('/editor/<username>')
def editor(username):
    cur = mysql.connection.cursor()
    cur.execute('''select rooms.idrooms,rooms.room_name, users.idusers from rooms 
                join users on rooms.idusers = users.idusers 
                where users.username = %s''', (username,))
    rooms_results = cur.fetchall()
    return render_template('editor.html', username=username, rooms = rooms_results)



@socket.on('disconnect')
def disconnect():
    uid = request.sid
    emit('disconnected', uid, broadcast=True)
    print(f'Client disconnected with user id: {uid}')


@socket.on('typing')
def typing(socketID):
    print(f'Typing: {socketID}')
    emit('typing', socketID, broadcast=True)


# Workspaces config
# code , chat, users, language


@socket.on('connect')
def connect():
    uid = request.sid
    connected_users[uid] = uid
    print(connected_users)
    print(f'Client connected with user id: {uid}')

@socket.on('change')
def change(data,userID):
    emit('change', {'text':data, 'userID':userID},broadcast=True)

@socket.on('lang')
def lang(data):
    global language
    language = data
    print(f'Language: {data}')
    emit('lang', data, broadcast=True)

@socket.on('chat')
def chat(chat,userID):
    print(f'Chat: {chat}')
    emit('chat', {'chat':chat, 'userID':userID}, broadcast=True)











if __name__ == '__main__':
    socket.run(app, debug=True)
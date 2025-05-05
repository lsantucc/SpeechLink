# Flask server. Make this more modular (i.e. make utils.py file that contains things like check_decibels etc)

from flask import Flask, flash, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from werkzeug.utils import secure_filename
import db
import whisper_app
import whisperx
from flask_socketio import SocketIO
from flask_socketio import join_room

app = Flask(__name__)

# https://pythonexamples.org/python-flask-and-websocket-example/
socketio = SocketIO(app)

limiter = Limiter(
    get_remote_address, # can do ipdb abuse post with this to check need api key though
    app=app,
    default_limits=["2000 per day", "500 per hour"], # current websocket method maybe not work with this
    storage_uri="memory://",
)

dir_path = os.path.dirname(os.path.realpath(__file__))
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000 # max size of 32 mb

# create whisper model so we don't have to re-create every time in whisper_app.transcribe()
device = "cpu"
model="small"
compute_type = "float32"
whisper_model = whisperx.load_model(model, device=device, compute_type=compute_type)

# SQL Injection is mostly prevented by default; the default response type in flask is HTML which is automatically escaped (sanitized)
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/room/host', methods=["GET","POST"])
def host():

    if request.method == "POST":
        code = request.form.get('code')
        con = db.connectCodes()
        try:
            db.create_entryCode(con, code)
        finally:
            db.disconnect(con)

    return render_template("host.html")

@app.route('/room/user', methods=["GET","POST"])
def user():

    if request.method == "POST":
        code = request.form.get('code')
        con = db.connectCodes()
        try:
            tempCode = db.return_entryCode(con, code)
        finally:
            db.disconnect(con)

        if (tempCode is None) or (str(tempCode[0]) != str(code)):
            return '', 926

    return render_template("user.html")

# Need a socket for when the user wants the transibed message

@socketio.on('join_room')
def handle_join(data):
    session_id = data

    join_room(session_id)
    
    socketio.emit('joined')

""" @socketio.on('request')
def request_live_transcription(data):
    sessionID = data
    
    con = db.connectCodes()

    msg = db.requestTranscript(con, sessionID)
    db.disconnect(con)

    socketio.emit("request", msg)
     """

# Socket for live recording
@socketio.on('message')
def receive_raw_audio(data):
    try:
        # implement silence checking here, etc.
        sessionID = data.get('code')
        msg = data.get('msg')

        # debugging
        print(type(msg), len(msg))

        # need database to hold transcribed text overtime for room code function
        transcribed_text, language = whisper_app.transcribe(msg, whisper_model)


        # send text to frontend via websocket. maybe need to use emit
        socketio.emit("message", transcribed_text, room=sessionID)
        socketio.emit("request", transcribed_text, room=sessionID)
        print("emitted to frontend")
        socketio.emit("code", sessionID)

        con = db.connectCodes()
        db.insert_or_update_message(con, sessionID, transcribed_text)
        db.disconnect(con)

        
    except Exception as e:
        print(e)
        return f'Exception {e}', 420


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80)
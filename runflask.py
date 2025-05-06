# Flask server. Serves html pages, defines routes, interacts with database and whisper.

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

# Limit uses by address to prevent abuse
limiter = Limiter(
    get_remote_address, 
    app=app,
    default_limits=["2000 per day", "500 per hour"], 
    storage_uri="memory://",
)

dir_path = os.path.dirname(os.path.realpath(__file__))
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000 # max size of 32 mb

# Create whisper model. Can change device to CUDA if a torch distribution with cuda is downloaded and 
# you have an NVIDIA GPU. RTX cards and greater run best with compute_type float16
device = "cpu"
model= "small"
compute_type = "float32"
whisper_model = whisperx.load_model(model, device=device, compute_type=compute_type)

# Default route serve front page
@app.route('/')
def index():
    return render_template("index.html")

# Route to connect with database and render host page
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

# Route to connect with database and render user page
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

# Socket to join room
@socketio.on('join_room')
def handle_join(data):
    session_id = data

    join_room(session_id)
    
    socketio.emit('joined')

# Socket for live recording
@socketio.on('message')
def receive_raw_audio(data):
    try:
        sessionID = data.get('code')
        msg = data.get('msg')

        # debugging
        print(type(msg), len(msg))

        # Make call to whisper to get trancribed text
        transcribed_text, language = whisper_app.transcribe(msg, whisper_model)

        # Send text to room via socket
        socketio.emit("message", transcribed_text, room=sessionID)
        socketio.emit("request", transcribed_text, room=sessionID)
        print("emitted to frontend")
        socketio.emit("code", sessionID)

        # Insert text into db
        con = db.connectCodes()
        db.insert_or_update_message(con, sessionID, transcribed_text)
        db.disconnect(con)

    except Exception as e:
        print(e)
        return f'Exception {e}', 420


if __name__ == "__main__":
    # Host on port 80
    socketio.run(app, host='0.0.0.0', port=80)
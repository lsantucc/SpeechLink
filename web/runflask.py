# Flask server. Make this more modular (i.e. make utils.py file that contains things like check_decibels etc)

from flask import Flask, flash, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from werkzeug.utils import secure_filename
import db
from datetime import datetime
import whisper_app
import hashlib
import whisperx
from flask_socketio import SocketIO

app = Flask(__name__)

# https://pythonexamples.org/python-flask-and-websocket-example/
socketio = SocketIO(app)

limiter = Limiter(
    get_remote_address, # can do ipdb abuse post with this to check need api key though
    app=app,
    default_limits=["2000 per day", "500 per hour"], # current websocket method maybe not work with this
    storage_uri="memory://",
)

if not os.path.exists("temp"):
    os.mkdir("temp")

dir_path = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path, "temp")
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000 # max size of 32 mb

# create whisper model so we don't have to re-create every time in whisper_app.transcribe()
device = "cpu"
model="small"
compute_type = "float32"
whisper_model = whisperx.load_model(model, device=device, compute_type=compute_type)

# SQL Injection is mostly prevented by default; the default response type in flask is HTML which is automatically escaped (sanitized)
@app.route('/')
def index():
    print(f"CWD is {os.getcwd()}")
    return render_template("index.html")

@app.route('/room/host')
def host():
    return render_template("host.html")
@app.route('/room/user')
def user():
    return render_template("user.html")

# Route for when user uploads a file
@app.route('/upload_file', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return '', 400

    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return '', 400
        
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        with open(path, "rb") as f:
            digest = hashlib.file_digest(f, "md5")
        hash = digest.hexdigest()

        con = db.connect()
        
        # hash check allows us to skip transcribing the text if we already have which saves time (40 seconds vs <0.5 seconds)
        entry = db.check_hash(con, hash)
        if entry:
            upload_id = entry[0]
            return f'{upload_id}', 200

        else:
            transcribed_text, language = whisper_app.transcribe(path, whisper_model)
            upload_object = db.Upload(filename, os.path.getsize(path), datetime.now(), transcribed_text, language, hash)
        
            if upload_object:
                upload_id = db.create_entry(con, upload_object)
                return f'{upload_id}', 200
            
    # if file isnt valid for whatever reason
    return '', 500

# Socket for live recording
@socketio.on('message')
def receive_raw_audio(data):
    try:
        # implement silence checking here, etc.

        # debugging
        print(type(data), len(data))

        # need database to hold transcribed text overtime for room code function
        transcribed_text, language = whisper_app.transcribe(data, whisper_model)

        # send text to frontend via websocket. maybe need to use emit
        socketio.emit("message", transcribed_text)
        print("emitted to frontend")
        
    except Exception as e:
        print(e)
        return f'Exception {e}', 420

# display transcribed text via id
@app.route('/display/<int:mp3_id>')
def display_api(mp3_id):
    # connect to db
    con = db.connect()
    # returns tuple
    entry = db.return_entry(con, mp3_id)

    # disconnect from db
    db.disconnect(con)

    #shutil.rmtree("temp")
    #os.mkdir("temp")
    if entry:
        return f'''Filename: {entry[1]}. Detected language: {entry[5]}. Transcribed text: {entry[4]}. '''
    
# roomcode route
# @app.route('/roomcode/<int:room_id>', methods=['POST'])
# def room_code():
    
#     return


if __name__ == "__main__":
    socketio.run(app, debug=True)

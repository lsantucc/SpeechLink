# Flask server

from flask import Flask, flash, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from werkzeug.utils import secure_filename
import db
from datetime import datetime
import whisper_app
import hashlib
import shutil
import whisper

app = Flask(__name__)

limiter = Limiter(
    get_remote_address, # can do ipdb abuse post with this to check need api key though
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

if not os.path.exists("temp"):
    os.mkdir("temp")

dir_path = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path, "temp")
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000 # max size of 32 mb
device = "cpu"
whisper_model = whisper.load_model("medium")
whisper_model = whisper_model.to(device)

# SQL Injection is mostly prevented by default; the default response type in flask is HTML which is automatically escaped (sanitized)
@app.route('/')
def index():
    return render_template("index.html")

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

@app.route('/upload_raw_audio', methods=['POST'])
def upload_raw_audio():
    if 'audio' not in request.files:
        return '', 400
    
    try:
        audio = request.files['audio'].read()
        # *** check decibel of audio; if its below 30 decibels we just ignore (involves sending 
        # specific response to frontend indicating this)
        pydub
        # we are receiving raw audio that we just read into bytes
        # use current_time to avoid conflict where multiple uploads happen at once
        current_time = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f"raw_audio_{current_time}.ogg"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(path, 'wb') as f:
            f.write(audio)
        
        # now that we've written the audio we can put it into whisper
        con = db.connect()

        transcribed_text, language = whisper_app.transcribe(path, whisper_model)
        # audio uploaded via mic will never have same hash
        upload_object = db.Upload(filename, os.path.getsize(path), datetime.now(), transcribed_text, language, 0)
        
        if upload_object:
            upload_id = db.create_entry(con, upload_object)
            return f'{upload_id}', 200
        
    except Exception as e:
        return f'Exception {e}', 420

# display transcribed text via id
@app.route('/display/<int:mp3_id>')
def display_api(mp3_id):
    con = db.connect()
    # returns tuple
    entry = db.return_entry(con, mp3_id)

    # if entry:
    #     db.disconnect(con)
    #     return f'''
    #     <!doctype html>
    #     <title>Test</title>
    #     <h1>Data entry</h1>
    #     <pre>
    #     Upload ID: {entry[0]}
    #     File Name: {entry[1]}
    #     File Size: {entry[2]} bytes
    #     Upload Time: {entry[3]}
    #     Transcribed Text: {entry[4]}
    #     Language: {entry[5]}e
    #     </pre>
    #     '''
    # else:
    #     db.disconnect(con)
    #     return f'<h1>No entry found for Upload ID {mp3_id}</h1>'
    db.disconnect(con)
    #shutil.rmtree("temp")
    #os.mkdir("temp")
    if entry:
        return f'''Filename: {entry[1]}. Detected language: {entry[5]}. Transcribed text: {entry[4]}. '''
    
# @app.route('/roomcode/<int:room_id>', methods=['POST'])
# def room_code():
    
#     return


if __name__ == "__main__":
    app.run(debug=True)

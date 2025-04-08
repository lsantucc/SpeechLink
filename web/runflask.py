# Flask server

from flask import Flask, flash, request, render_template
import os
from werkzeug.utils import secure_filename
import db
from datetime import datetime
import whisper_app
import hashlib

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = f"{dir_path}/uploads"
app.config['MAX_CONTENT_LENGTH'] = 64 * 1000 * 1000 # max size of 64 mb

# SQL Injection is mostly prevented by default; the default response type in flask is HTML which is automatically escaped (sanitized)
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
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
            upload_object = db.Upload(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])

            if upload_object:
                upload_id = entry[0]
                return f'{upload_id}', 200

        else:
            transcribed_text, language = whisper_app.transcribe(path)
            upload_object = db.Upload(filename, os.path.getsize(path), datetime.now(), transcribed_text, language, hash)
        
            if upload_object:
                upload_id = db.create_entry(con, upload_object)
                return f'{upload_id}', 200
            
    # if file isnt valid for whatever reason
    return '', 500
    
# display transcribed text
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

    if entry:
        return f'''Filename: {entry[1]}. Detected language: {entry[5]}. Transcribed text: {entry[4]}. '''
    
if __name__ == "__main__":
    app.run(debug=True)
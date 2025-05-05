# Interact with SQL database
import sqlite3
from datetime import datetime

class Upload:
    def __init__(self, file_name, file_size, upload_time, transcribed_text, language, hash):
        self.file_name = file_name
        self.file_size = file_size
        self.upload_time = upload_time
        self.transcribed_text = transcribed_text
        self.language = language
        self.hash = hash
    
def connect():
    return sqlite3.connect("uploads.db")

def connectCodes():
    return sqlite3.connect("codes.db")

def create_entryCode(con, code):
    cur = con.cursor()
    cur.execute("INSERT INTO codes (code) VALUES (?)", (code,))
    
    con.commit()
    return cur.lastrowid

def return_entryCode(con, code):
    cur = con.cursor()
    cur.execute(f"SELECT * FROM codes WHERE code=?", (code,))
    return cur.fetchone() 

def disconnect(con):
    con.commit()
    con.close()
    return

def create_entry(con, upload):
    cur = con.cursor()
    cur.execute("INSERT INTO uploads (file_name, file_size, upload_time, transcribed_text, language, hash) VALUES (?, ?, ?, ?, ?, ?)", 
                (upload.file_name, upload.file_size, upload.upload_time, upload.transcribed_text, upload.language, upload.hash))
    con.commit()
    return cur.lastrowid

def return_entry(con, upload_id):
    cur = con.cursor()
    cur.execute(f"SELECT * FROM uploads WHERE upload_id=?", (upload_id,))
    return cur.fetchone() 

def check_hash(con, hash):
    cur = con.cursor()
    cur.execute("SELECT * FROM uploads WHERE hash=?", (hash,)) 
    result = cur.fetchone()
    if result is not None:
        return result
        
    return None

# setup if you run the script directly
if __name__ == "__main__":
    conn = sqlite3.connect('uploads.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            upload_time TEXT NOT NULL,
            transcribed_text TEXT,
            language TEXT,
            hash TEXT
        )
    ''')

    conn.commit()
    conn.close()

    conn = sqlite3.connect('codes.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            code INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

    

    
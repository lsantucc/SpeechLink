# Interact with SQL database
import sqlite3
from datetime import datetime

def connectCodes():
    return sqlite3.connect("codes.db")

def create_entryCode(con, code):
    cur = con.cursor()
    cur.execute("INSERT INTO codes (code) VALUES (?)", (code,))
    
    con.commit()
    return cur.lastrowid

def insert_or_update_message(con, code, transcribed_text):
    cur = con.cursor()

        # Directly update the transcribed_text for the given code
    cur.execute('''
        UPDATE codes
        SET transcribed_text = ?
        WHERE code = ?
    ''', (transcribed_text, code))

    print(f"Updated code {code} with new message.")

def requestTranscript(con, code):
    cur = con.cursor()

    cur.execute('''
            SELECT transcribed_text
            FROM codes
            WHERE code = ?
        ''', (code,))
    
    msg = cur.fetchone()

    return msg

def return_entryCode(con, code):
    cur = con.cursor()
    cur.execute("SELECT * FROM codes WHERE code=?", (code,))
    return cur.fetchone() 

def disconnect(con):
    con.commit()
    con.close()
    return

# setup if you run the script directly
if __name__ == "__main__":
    conn = sqlite3.connect('codes.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            code INTEGER NOT NULL,
            transcribed_text TEXT
        )
    ''')

    conn.commit()
    conn.close()

    

    
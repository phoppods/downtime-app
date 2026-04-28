from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os


app = Flask(__name__)
CORS(app)

DB = "downtime.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line TEXT,
            machine TEXT,
            tech TEXT,
            reason TEXT,
            start TEXT,
            end TEXT,
            notes TEXT,
            resNote TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def serve_html():
    return send_from_directory(os.getcwd(), "machine_downtime_logger1.html")

@app.route("/events", methods=["GET"])
def get_events():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    keys = ["id","line","machine","tech","reason","start","end","notes","resNote"]
    return jsonify([dict(zip(keys,row)) for row in rows])

@app.route("/events", methods=["POST"])
def add_event():
    data = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        INSERT INTO events (line,machine,tech,reason,start,end,notes,resNote)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (
        data["line"], data["machine"], data["tech"], data["reason"],
        data["start"], data.get("end"), data.get("notes"), ""
    ))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

@app.route("/events/<int:id>/end", methods=["POST"])
def end_event(id):
    data = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        UPDATE events
        SET end=?, resNote=?
        WHERE id=?
    ''', (data["end"], data.get("resNote",""), id))
    conn.commit()
    conn.close()
    return jsonify({"status":"updated"})

if __name__ == "__main__":
    app.run(debug=True)
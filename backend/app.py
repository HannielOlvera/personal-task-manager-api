import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASS"),
    "dbname": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT", 5432))
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"success": False, "error": "Missing fields"}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s", (data["username"],))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Username already exists"}), 400
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (data["username"], data["password"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username=%s", (data.get("username"),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and user[2] == data.get("password"):
        return jsonify({"success": True, "user_id": user[0], "username": user[1]})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id", type=int)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, completed, last_modified_by, last_modified_at, created_at FROM tasks WHERE user_id=%s", (user_id,))
    tasks = [
        {
            "id": row[0],
            "text": row[1],
            "completed": row[2],
            "last_modified_by": row[3],
            "last_modified_at": row[4],
            "created_at": row[5]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, text, last_modified_by) VALUES (%s, %s, %s) RETURNING id",
        (data["user_id"], data["text"], data["last_modified_by"])
    )
    task_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "task_id": task_id})

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET text=%s, last_modified_by=%s, last_modified_at=NOW() WHERE id=%s",
        (data.get("text"), data.get("last_modified_by"), task_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET completed=TRUE, last_modified_by=%s, last_modified_at=NOW() WHERE id=
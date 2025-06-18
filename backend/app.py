from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulación de base de datos en memoria (puedes cambiar por SQLite/MySQL)
users = []
tasks = []
user_id_counter = 1
task_id_counter = 1

@app.route("/register", methods=["POST"])
def register():
    global user_id_counter
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"success": False, "error": "Missing fields"}), 400
    if any(u["username"] == data["username"] for u in users):
        return jsonify({"success": False, "error": "Username already exists"}), 400
    users.append({"id": user_id_counter, "username": data["username"], "password": data["password"]})
    user_id_counter += 1
    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    for u in users:
        if u["username"] == data.get("username") and u["password"] == data.get("password"):
            return jsonify({"success": True, "user_id": u["id"], "username": u["username"]})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id", type=int)
    user_tasks = [t for t in tasks if t["user_id"] == user_id]
    return jsonify(user_tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    global task_id_counter
    data = request.json
    if not data or "user_id" not in data or "text" not in data or "last_modified_by" not in data:
        return jsonify({"success": False, "error": "Missing fields"}), 400
    task = {
        "id": task_id_counter,
        "user_id": data["user_id"],
        "text": data["text"],
        "completed": False,
        "last_modified_by": data["last_modified_by"]
    }
    tasks.append(task)
    task_id_counter += 1
    return jsonify({"success": True})

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.json
    for t in tasks:
        if t["id"] == task_id:
            t["text"] = data.get("text", t["text"])
            t["last_modified_by"] = data.get("last_modified_by", t["last_modified_by"])
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"success": True})

@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = True
            t["last_modified_by"] = request.json.get("last_modified_by", t["last_modified_by"])
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "Task not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
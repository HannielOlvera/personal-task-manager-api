<?php
header('Content-Type: application/json');

// Configuración de la base de datos
$mysqli = new mysqli(
    "sql202.infinityfree.com",
    "if0_39265679",
    "Ftwck1tJDSzC8",
    "if0_39265679_personal_task_manager"
);
if ($mysqli->connect_errno) {
    echo json_encode(["error" => "Failed to connect"]);
    exit();
}

function clean($data) {
    global $mysqli;
    return $mysqli->real_escape_string(trim($data));
}

$action = $_GET['action'] ?? '';

// --- LOGIN ---
if ($action == 'login' && isset($_POST['username'], $_POST['password'])) {
    $username = clean($_POST['username']);
    $password = $_POST['password'];
    $result = $mysqli->query("SELECT * FROM users WHERE username='$username' LIMIT 1");
    if ($row = $result->fetch_assoc()) {
        if (password_verify($password, $row['password_hash'])) {
            echo json_encode(["success" => true, "user_id" => $row['id'], "username" => $row['username']]);
        } else {
            echo json_encode(["success" => false, "error" => "Incorrect password"]);
        }
    } else {
        echo json_encode(["success" => false, "error" => "User not found"]);
    }
}

// --- REGISTER ---
elseif ($action == 'register' && isset($_POST['username'], $_POST['password'])) {
    $username = clean($_POST['username']);
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT);
    $result = $mysqli->query("SELECT id FROM users WHERE username='$username'");
    if ($result->num_rows > 0) {
        echo json_encode(["success" => false, "error" => "Username already exists"]);
    } else {
        $mysqli->query("INSERT INTO users (username, password_hash) VALUES ('$username', '$password')");
        echo json_encode(["success" => true]);
    }
}

// --- GET TASKS ---
elseif ($action == 'get_tasks' && isset($_GET['user_id'])) {
    $user_id = intval($_GET['user_id']);
    $result = $mysqli->query("SELECT * FROM tasks WHERE user_id=$user_id");
    $tasks = [];
    while ($row = $result->fetch_assoc()) {
        $tasks[] = $row;
    }
    echo json_encode($tasks);
}

// --- ADD TASK ---
elseif ($action == 'add_task' && isset($_POST['user_id'], $_POST['text'], $_POST['last_modified_by'])) {
    $user_id = intval($_POST['user_id']);
    $text = clean($_POST['text']);
    $last_modified_by = clean($_POST['last_modified_by']);
    $mysqli->query("INSERT INTO tasks (user_id, text, last_modified_by) VALUES ($user_id, '$text', '$last_modified_by')");
    echo json_encode(["success" => true]);
}

// --- EDIT TASK ---
elseif ($action == 'edit_task' && isset($_POST['task_id'], $_POST['text'], $_POST['last_modified_by'])) {
    $task_id = intval($_POST['task_id']);
    $text = clean($_POST['text']);
    $last_modified_by = clean($_POST['last_modified_by']);
    $mysqli->query("UPDATE tasks SET text='$text', last_modified_by='$last_modified_by', last_modified_at=NOW() WHERE id=$task_id");
    echo json_encode(["success" => true]);
}

// --- DELETE TASK ---
elseif ($action == 'delete_task' && isset($_POST['task_id'])) {
    $task_id = intval($_POST['task_id']);
    $mysqli->query("DELETE FROM tasks WHERE id=$task_id");
    echo json_encode(["success" => true]);
}

// --- COMPLETE TASK ---
elseif ($action == 'complete_task' && isset($_POST['task_id'], $_POST['last_modified_by'])) {
    $task_id = intval($_POST['task_id']);
    $last_modified_by = clean($_POST['last_modified_by']);
    $mysqli->query("UPDATE tasks SET completed=1, last_modified_by='$last_modified_by', last_modified_at=NOW() WHERE id=$task_id");
    echo json_encode(["success" => true]);
}

else {
    echo json_encode(["error" => "Invalid action or missing parameters"]);
}
?>
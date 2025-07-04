<?php
/*
FILE LOCATION: /login.php (REPLACE your existing login.php)
SAVE AS: login.php (in your website root)

Film Price Guide - Secure Login System
Now uses protected configuration files
*/

// Define access constant for secure config
define('FILM_PRICE_GUIDE_ACCESS', true);

// Start session with secure settings
ini_set('session.cookie_httponly', 1);
ini_set('session.use_strict_mode', 1);
session_start();

// Include secure configuration
require_once 'config/secure_config.php';

// Get database configuration securely
$db_config = get_secure_config('database');

// Function to connect to database
function get_db_connection($config) {
    try {
        $dsn = "mysql:host={$config['host']};dbname={$config['dbname']};charset={$config['charset']}";
        $pdo = new PDO($dsn, $config['username'], $config['password'], $config['options']);
        return $pdo;
    } catch (PDOException $e) {
        error_log("Database connection failed: " . $e->getMessage());
        return null;
    }
}

// Function to hash password
function hash_password($password) {
    return password_hash($password, PASSWORD_DEFAULT);
}

// Function to verify password
function verify_password($password, $hash) {
    return password_verify($password, $hash);
}

// Redirect if already logged in
if (isset($_SESSION['user_id'])) {
    if (isset($_SESSION['is_admin']) && $_SESSION['is_admin']) {
        header('Location: index.php?page=admin');
    } else {
        header('Location: index.php?page=dashboard');
    }
    exit;
}

$error_message = '';
$success_message = '';
$db_error = false;

// Test database connection
$pdo = get_db_connection($db_config);
if (!$pdo) {
    $db_error = true;
    $error_message = 'Database connection failed. Please check secure configuration.';
}

// Handle form submissions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    if ($action === 'login' && !$db_error) {
        $login = trim($_POST['login'] ?? '');
        $password = $_POST['password'] ?? '';
        
        if (empty($login) || empty($password)) {
            $error_message = 'Please enter both email/username and password.';
        } else {
            try {
                // Check if input is email or username
                if (filter_var($login, FILTER_VALIDATE_EMAIL)) {
                    $stmt = $pdo->prepare("SELECT id, username, email, password_hash, first_name, last_name, is_admin FROM users WHERE email = ? AND is_active = 1");
                } else {
                    $stmt = $pdo->prepare("SELECT id, username, email, password_hash, first_name, last_name, is_admin FROM users WHERE username = ? AND is_active = 1");
                }
                
                $stmt->execute([$login]);
                $user = $stmt->fetch();
                
                if ($user && verify_password($password, $user['password_hash'])) {
                    // Login successful
                    $_SESSION['user_id'] = $user['id'];
                    $_SESSION['username'] = $user['username'];
                    $_SESSION['email'] = $user['email'];
                    $_SESSION['first_name'] = $user['first_name'];
                    $_SESSION['is_admin'] = (bool)$user['is_admin'];
                    
                    // Update last login
                    $update_stmt = $pdo->prepare("UPDATE users SET last_login = NOW() WHERE id = ?");
                    $update_stmt->execute([$user['id']]);
                    
                    // Log successful login
                    error_log("Successful login: " . $user['username'] . " from " . $_SERVER['REMOTE_ADDR']);
                    
                    // Redirect based on admin status
                    if ($_SESSION['is_admin']) {
                        header('Location: index.php?page=admin');
                    } else {
                        header('Location: index.php?page=dashboard');
                    }
                    exit;
                } else {
                    $error_message = 'Invalid email/username or password.';
                    // Log failed login attempt
                    error_log("Failed login attempt: " . $login . " from " . $_SERVER['REMOTE_ADDR']);
                }
            } catch (Exception $e) {
                error_log("Login error: " . $e->getMessage());
                $error_message = 'Login failed. Please try again.';
            }
        }
    }
    
    // Handle registration (only if database is working)
    if ($action === 'register' && !$db_error) {
        $username = trim($_POST['username'] ?? '');
        $email = trim($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';
        $confirm_password = $_POST['confirm_password'] ?? '';
        $first_name = trim($_POST['first_name'] ?? '');
        $last_name = trim($_POST['last_name'] ?? '');
        
        // Validation
        if (empty($username) || empty($email) || empty($password)) {
            $error_message = 'Please fill in all required fields.';
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error_message = 'Please enter a valid email address.';
        } elseif (strlen($password) < 8) {
            $error_message = 'Password must be at least 8 characters long.';
        } elseif ($password !== $confirm_password) {
            $error_message = 'Passwords do not match.';
        } else {
            try {
                // Check if username or email already exists
                $stmt = $pdo->prepare("SELECT id FROM users WHERE username = ? OR email = ?");
                $stmt->execute([$username, $email]);
                
                if ($stmt->fetch()) {
                    $error_message = 'Username or email already exists.';
                } else {
                    // Check if this is the first user (make them admin)
                    $count_stmt = $pdo->prepare("SELECT COUNT(*) as count FROM users");
                    $count_stmt->execute();
                    $user_count = $count_stmt->fetch()['count'];
                    $is_admin = ($user_count == 0) ? 1 : 0; // First user becomes admin
                    
                    // Create new user
                    $password_hash = hash_password($password);
                    
                    $stmt = $pdo->prepare("
                        INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, NOW())
                    ");
                    
                    if ($stmt->execute([$username, $email, $password_hash, $first_name, $last_name, $is_admin])) {
                        if ($is_admin) {
                            $success_message = '🔑 Admin account created successfully! You now have full system access to configure APIs, manage users, and monitor the system.';
                        } else {
                            $success_message = '✅ User account created successfully! You can now log in to create watchlists, set price alerts, and track your movie collection.';
                        }
                        
                        // Log successful registration
                        error_log("New user registered: " . $username . " (Admin: " . ($is_admin ? 'Yes' : 'No') . ")");
                    } else {
                        $error_message = 'Failed to create account. Please try again.';
                    }
                }
            } catch (Exception $e) {
                error_log("Registration error: " . $e->getMessage());
                $error_message = 'Registration failed. Please try again.';
            }
        }
    }
    
    // Handle admin creation if no users exist
    if ($action === 'create_admin' && !$db_error) {
        $admin_username = trim($_POST['admin_username'] ?? '');
        $admin_email = trim($_POST['admin_email'] ?? '');
        $admin_password = $_POST['admin_password'] ?? '';
        
        if (empty($admin_username) || empty($admin_email) || empty($admin_password)) {
            $error_message = 'Please fill in all admin fields.';
        } else {
            try {
                $password_hash = hash_password($admin_password);
                
                $stmt = $pdo->prepare("
                    INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, created_at)
                    VALUES (?, ?, ?, 'Admin', 'User', 1, NOW())
                ");
                
                if ($stmt->execute([$admin_username, $admin_email, $password_hash])) {
                    $success_message = '🔑 Admin account created successfully! You now have full system access to configure APIs, manage users, and monitor the system.';
                    error_log("Admin account created: " . $admin_username);
                } else {
                    $error_message = 'Failed to create admin account.';
                }
            } catch (Exception $e) {
                $error_message = 'Failed to create admin account: ' . $e->getMessage();
            }
        }
    }
}

// Check if any users exist
$has_users = false;
if ($pdo) {
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) as count FROM users");
        $stmt->execute();
        $user_count = $stmt->fetch()['count'];
        $has_users = ($user_count > 0);
    } catch (Exception $e) {
        // Table might not exist yet
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Film Price Guide</title>
    <style>
        /* Include all your existing CSS styles here */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
            color: white; padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 40px; max-width: 500px; width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 {
            font-size: 2rem; background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .alert { padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid; }
        .error { background: rgba(255, 107, 107, 0.2); color: #ff6b6b; border-color: rgba(255, 107, 107, 0.3); }
        .success { background: rgba(76, 205, 196, 0.2); color: #4ecdc4; border-color: rgba(76, 205, 196, 0.3); }
        .warning { background: rgba(255, 193, 7, 0.2); color: #ffc107; border-color: rgba(255, 193, 7, 0.3); }
        .tabs { display: flex; margin-bottom: 30px; border-radius: 10px; overflow: hidden; background: rgba(255, 255, 255, 0.1); }
        .tab { flex: 1; padding: 15px; text-align: center; cursor: pointer; transition: all 0.3s ease; border: none; background: none; color: white; font-size: 16px; }
        .tab.active { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; font-weight: 500; color: #4ecdc4; }
        .form-input { width: 100%; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 10px; background: rgba(255, 255, 255, 0.1); color: white; font-size: 16px; transition: all 0.3s ease; }
        .form-input:focus { outline: none; border-color: #4ecdc4; box-shadow: 0 0 15px rgba(78, 205, 196, 0.3); }
        .form-input::placeholder { color: rgba(255, 255, 255, 0.5); }
        .btn { width: 100%; padding: 15px; border: none; border-radius: 10px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; margin-top: 10px; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(78, 205, 196, 0.4); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .form-content { display: none; }
        .form-content.active { display: block; }
        .home-link { text-align: center; margin-top: 20px; }
        .home-link a { color: #4ecdc4; text-decoration: none; font-weight: 500; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🎬 Film Price Guide</h1>
            <p style="margin-top: 10px; color: rgba(255,255,255,0.8); font-size: 0.9rem;">
                🔒 Secure Authentication System
            </p>
        </div>

        <?php if ($db_error): ?>
            <div class="alert error">
                <h3>🔧 Configuration Error</h3>
                <p>Database connection failed. Please check your secure configuration file.</p>
                <p><strong>File:</strong> config/secure_config.php</p>
            </div>
        <?php elseif (!$has_users): ?>
            <div class="alert warning">
                <h3>🚀 Initial Setup</h3>
                <p>No users found. Create the first admin account to get started.</p>
            </div>
        <?php endif; ?>

        <?php if ($error_message): ?>
            <div class="alert error"><?= htmlspecialchars($error_message) ?></div>
        <?php endif; ?>

        <?php if ($success_message): ?>
            <div class="alert success"><?= htmlspecialchars($success_message) ?></div>
        <?php endif; ?>

        <!-- Rest of the form HTML remains the same as your original login.php -->
        <!-- Just replace the existing forms with the same structure -->

        <div class="home-link">
            <a href="index.php">← Back to Home</a>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.form-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + '-form').classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
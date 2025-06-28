<?php
// Session configuration fix for shared hosting
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h2>🔧 Fixing Session Configuration</h2>";

// Check current session settings
echo "<h3>Current Session Settings:</h3>";
echo "<p>Session save path: " . session_save_path() . "</p>";
echo "<p>Session name: " . session_name() . "</p>";
echo "<p>Session status: ";
switch (session_status()) {
    case PHP_SESSION_DISABLED:
        echo "Sessions are disabled";
        break;
    case PHP_SESSION_NONE:
        echo "Sessions are enabled, but none exists";
        break;
    case PHP_SESSION_ACTIVE:
        echo "Sessions are enabled, and one exists";
        break;
}
echo "</p>";

// Try to set a custom session save path in a writable directory
$custom_session_path = __DIR__ . '/../sessions';

// Create sessions directory if it doesn't exist
if (!is_dir($custom_session_path)) {
    if (mkdir($custom_session_path, 0755, true)) {
        echo "<p>✅ Created sessions directory: {$custom_session_path}</p>";
    } else {
        echo "<p>❌ Failed to create sessions directory</p>";
    }
}

// Set session save path if directory is writable
if (is_writable($custom_session_path)) {
    session_save_path($custom_session_path);
    echo "<p>✅ Set custom session path: {$custom_session_path}</p>";
} else {
    echo "<p>⚠️ Custom session path not writable, using default</p>";
}

// Configure session settings for shared hosting
ini_set('session.gc_maxlifetime', 3600); // 1 hour
ini_set('session.cookie_lifetime', 0);   // Until browser closes
ini_set('session.cookie_httponly', 1);   // Security
ini_set('session.use_strict_mode', 1);   // Security

// Try to start session
echo "<h3>Testing Session Start:</h3>";
try {
    if (session_start()) {
        echo "<p>✅ Session started successfully!</p>";
        
        // Test session variables
        $_SESSION['test'] = 'Session working!';
        echo "<p>✅ Session variable set: " . $_SESSION['test'] . "</p>";
        
        // Display session ID
        echo "<p>Session ID: " . session_id() . "</p>";
        
    } else {
        echo "<p>❌ Failed to start session</p>";
    }
} catch (Exception $e) {
    echo "<p>❌ Session error: " . $e->getMessage() . "</p>";
}

// Check if sessions directory was created and is writable
if (is_dir($custom_session_path)) {
    $files = scandir($custom_session_path);
    echo "<p>Files in sessions directory: " . count($files) - 2 . "</p>"; // -2 for . and ..
}

?>

<h2>🔧 Session Fixed Configuration</h2>
<p>Copy this code to the top of your main files:</p>

<div style="background: #2d3748; color: #e2e8f0; padding: 1rem; border-radius: 8px; font-family: monospace;">
&lt;?php<br>
// Session configuration for shared hosting<br>
$session_path = __DIR__ . '/sessions';<br>
if (!is_dir($session_path)) mkdir($session_path, 0755, true);<br>
if (is_writable($session_path)) session_save_path($session_path);<br>
<br>
ini_set('session.gc_maxlifetime', 3600);<br>
ini_set('session.cookie_httponly', 1);<br>
ini_set('session.use_strict_mode', 1);<br>
<br>
session_start();<br>
?&gt;
</div>

<p><a href="debug.php">← Back to Debug</a> | <a href="test-full.php">Test Complete Setup →</a></p>
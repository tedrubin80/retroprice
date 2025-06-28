<?php
// Dreamhost Database Configuration
// Replace these with your actual Dreamhost database details

$db_config = [
    // Dreamhost always uses this hostname:
    'host' => 'mysql.dreamhost.com',
    
    // Your database name (will look like: yourusername_filmguide)
    'dbname' => 'yourusername_filmguide',     // 🔧 CHANGE: Replace 'yourusername' with your actual Dreamhost username
    
    // Your database username (you created this in Dreamhost panel)
    'username' => 'filmguide_admin',          // 🔧 CHANGE: The username you created
    
    // Your database password (you set this in Dreamhost panel)
    'password' => 'your_password_here',       // 🔧 CHANGE: The password you set
    
    'charset' => 'utf8mb4'
];

// Dreamhost-specific connection function
function connect_to_dreamhost($config) {
    try {
        echo "<p>🔍 Connecting to Dreamhost MySQL...</p>";
        echo "<p>Host: {$config['host']}</p>";
        echo "<p>Database: {$config['dbname']}</p>";
        echo "<p>Username: {$config['username']}</p>";
        
        $dsn = "mysql:host={$config['host']};dbname={$config['dbname']};charset={$config['charset']}";
        
        $options = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4",
            PDO::ATTR_TIMEOUT => 10  // Dreamhost can be slow sometimes
        ];
        
        $pdo = new PDO($dsn, $config['username'], $config['password'], $options);
        
        // Test the connection
        $result = $pdo->query("SELECT 1 as test")->fetch();
        
        if ($result['test'] == 1) {
            echo "<p>✅ <strong>SUCCESS!</strong> Connected to Dreamhost database</p>";
            
            // Show database info
            $db_info = $pdo->query("SELECT DATABASE() as db_name")->fetch();
            echo "<p>📊 Connected to database: <strong>{$db_info['db_name']}</strong></p>";
            
            return $pdo;
        }
        
    } catch (PDOException $e) {
        echo "<p>❌ <strong>Connection Failed:</strong> " . $e->getMessage() . "</p>";
        
        // Common Dreamhost issues and solutions
        if (strpos($e->getMessage(), 'Access denied') !== false) {
            echo "<div style='background: rgba(255, 107, 107, 0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>";
            echo "<h3>🔒 Access Denied - Check These:</h3>";
            echo "<ul>";
            echo "<li>Username and password are correct</li>";
            echo "<li>Database user has permissions to access the database</li>";
            echo "<li>Database name includes your Dreamhost username prefix</li>";
            echo "</ul>";
            echo "</div>";
        }
        
        if (strpos($e->getMessage(), 'Unknown database') !== false) {
            echo "<div style='background: rgba(255, 193, 7, 0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>";
            echo "<h3>🗄️ Database Not Found - Check These:</h3>";
            echo "<ul>";
            echo "<li>Database name is correct (should be: yourusername_filmguide)</li>";
            echo "<li>Database was created in Dreamhost panel</li>";
            echo "<li>Database creation has finished (can take a few minutes)</li>";
            echo "</ul>";
            echo "</div>";
        }
        
        throw $e;
    }
}

// Display current configuration
echo "<h1>🏠 Dreamhost Database Configuration</h1>";

echo "<div style='background: rgba(78, 205, 196, 0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>";
echo "<h3>📋 Your Current Settings:</h3>";
echo "<p><strong>Host:</strong> {$db_config['host']} ✅ (Correct for Dreamhost)</p>";
echo "<p><strong>Database:</strong> {$db_config['dbname']}</p>";
echo "<p><strong>Username:</strong> {$db_config['username']}</p>";
echo "<p><strong>Password:</strong> " . (strlen($db_config['password']) > 10 ? '✅ Set' : '❌ Not set or too short') . "</p>";
echo "</div>";

// Test the connection
echo "<h2>🧪 Testing Connection:</h2>";

try {
    $pdo = connect_to_dreamhost($db_config);
    
    echo "<h2>🎉 Database Connection Successful!</h2>";
    
    // Check for existing tables
    echo "<h3>📊 Checking for Film Price Guide Tables:</h3>";
    $tables = ['users', 'films', 'price_history', 'watchlist'];
    
    foreach ($tables as $table) {
        try {
            $stmt = $pdo->query("SHOW TABLES LIKE '{$table}'");
            if ($stmt->rowCount() > 0) {
                $count_stmt = $pdo->query("SELECT COUNT(*) as count FROM {$table}");
                $count = $count_stmt->fetch()['count'];
                echo "<p>✅ Table '<strong>{$table}</strong>' exists ({$count} rows)</p>";
            } else {
                echo "<p>⚠️ Table '<strong>{$table}</strong>' not found</p>";
            }
        } catch (Exception $e) {
            echo "<p>❌ Error checking table '{$table}': " . $e->getMessage() . "</p>";
        }
    }
    
    // Check if we need to import schema
    $stmt = $pdo->query("SHOW TABLES");
    $existing_tables = $stmt->fetchAll(PDO::FETCH_COLUMN);
    
    if (count($existing_tables) === 0) {
        echo "<div style='background: rgba(255, 193, 7, 0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>";
        echo "<h3>📥 Next Step: Import Database Schema</h3>";
        echo "<ol>";
        echo "<li>Go to Dreamhost Panel → <strong>Goodies → phpMyAdmin</strong></li>";
        echo "<li>Select your database: <strong>{$db_config['dbname']}</strong></li>";
        echo "<li>Click <strong>Import</strong> tab</li>";
        echo "<li>Upload your <strong>database/schema.sql</strong> file</li>";
        echo "<li>Click <strong>Go</strong></li>";
        echo "</ol>";
        echo "</div>";
    } else {
        echo "<p>✅ Database has " . count($existing_tables) . " tables total</p>";
    }
    
} catch (Exception $e) {
    echo "<div style='background: rgba(255, 107, 107, 0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>";
    echo "<h3>❌ Connection Failed</h3>";
    echo "<p><strong>Error:</strong> " . $e->getMessage() . "</p>";
    echo "</div>";
    
    echo "<div style='background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>";
    echo "<h3>🔧 How to Fix This:</h3>";
    echo "<ol>";
    echo "<li><strong>Go to Dreamhost Panel:</strong> https://panel.dreamhost.com/</li>";
    echo "<li><strong>Navigate to:</strong> Advanced → MySQL Databases</li>";
    echo "<li><strong>Either:</strong>";
    echo "<ul>";
    echo "<li>Use existing database credentials, OR</li>";
    echo "<li>Create new database with name like 'filmguide'</li>";
    echo "</ul>";
    echo "</li>";
    echo "<li><strong>Update this file</strong> with the correct credentials</li>";
    echo "<li><strong>Refresh this page</strong> to test again</li>";
    echo "</ol>";
    echo "</div>";
}
?>

<h2>📖 Dreamhost Database Guide:</h2>

<div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
    <h3>🎯 Typical Dreamhost Database Details:</h3>
    <ul>
        <li><strong>Host:</strong> Always <code>mysql.dreamhost.com</code></li>
        <li><strong>Database Name:</strong> <code>yourusername_filmguide</code></li>
        <li><strong>Username:</strong> Whatever you created (like <code>filmguide_admin</code>)</li>
        <li><strong>Password:</strong> What you set when creating the database</li>
    </ul>
    
    <h3>🚀 Quick Links:</h3>
    <ul>
        <li><a href="https://panel.dreamhost.com/" target="_blank" style="color: #4ecdc4;">Dreamhost Panel</a></li>
        <li><a href="https://help.dreamhost.com/hc/en-us/articles/221691727-Creating-a-MySQL-database" target="_blank" style="color: #4ecdc4;">Dreamhost MySQL Guide</a></li>
    </ul>
</div>

<p>
    <a href="../debug.php" style="color: #4ecdc4;">← Back to Debug</a> | 
    <a href="../index.php" style="color: #4ecdc4;">Try Main App →</a>
</p>
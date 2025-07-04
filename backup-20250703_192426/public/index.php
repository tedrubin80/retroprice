<?php
/**
 * Film Price Guide - Main Entry Point
 * Multi-API Search Engine for VHS, DVD, and Graded Movies
 * 
 * Compatible with: Dreamhost, GitHub Apps, Standard LAMP
 */

// Start session
session_start();

// Security headers
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('X-XSS-Protection: 1; mode=block');

// Load configuration
require_once '../config/config.php';
require_once '../src/common/functions.php';
require_once '../src/auth/auth.php';

// Get current page
$page = $_GET['page'] ?? 'home';
$allowed_pages = ['home', 'search', 'dashboard', 'admin', 'profile', 'api-test'];

if (!in_array($page, $allowed_pages)) {
    $page = 'home';
}

// Check admin access for admin pages
if ($page === 'admin' && (!isset($_SESSION['is_admin']) || !$_SESSION['is_admin'])) {
    header('Location: index.php?page=login&error=admin_required');
    exit;
}

// Include header
include '../src/common/header.php';

// Include page content
switch($page) {
    case 'home':
        include '../src/common/home.php';
        break;
    case 'search':
        include '../src/search/search.php';
        break;
    case 'dashboard':
        include '../src/user/dashboard.php';
        break;
    case 'admin':
        include '../src/admin/admin.php';
        break;
    case 'profile':
        include '../src/user/profile.php';
        break;
    case 'api-test':
        include '../src/search/api-test.php';
        break;
    default:
        include '../src/common/404.php';
}

// Include footer
include '../src/common/footer.php';
?>

# 🎬 Film Price Guide

Multi-API Search Engine for VHS, DVD, and Graded Movies

## 🚀 Features

- **Multi-API Integration**: OMDb, TMDb, eBay, Heritage Auctions
- **User Authentication**: Secure login/registration system
- **Admin Panel**: API key management, user administration
- **Price Tracking**: Real-time pricing from multiple sources
- **Advanced Search**: Filter by format, condition, rarity
- **Responsive Design**: Mobile-friendly interface
- **MySQL Database**: Complete schema for movies and pricing

## 📋 Requirements

- PHP 8.0+
- MySQL 5.7+ / MariaDB 10.2+
- Apache/Nginx with mod_rewrite
- cURL extension
- PDO extension

## 🛠️ Installation

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd film-price-guide
composer install
npm install
```

### 2. Configure Environment
```bash
cp config/env/.env.example config/env/.env
# Edit .env with your database and API credentials
```

### 3. Database Setup
```bash
mysql -u root -p < database/schema.sql
```

### 4. Set Permissions
```bash
chmod 755 public/uploads/
chmod 644 config/env/.env
```

## 🌐 Deployment

### Dreamhost
```bash
./scripts/deploy/dreamhost-deploy.sh
```

### GitHub Apps
Push to main branch - automated via GitHub Actions

### Manual Upload
Upload `public/` contents to your web root directory

## 🔧 Configuration

### API Keys Required
- **OMDb API**: Movie metadata
- **TMDb API**: Additional movie data
- **eBay API**: Price tracking
- **Heritage Auctions**: Graded media prices

### Environment Variables
See `config/env/.env.example` for all available options

## 📁 Project Structure

```
film-price-guide/
├── public/              # Web-accessible files
│   ├── index.php       # Main entry point
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── uploads/        # User uploads
├── src/                # Application source
│   ├── auth/           # Authentication
│   ├── admin/          # Admin panel
│   ├── search/         # Search functionality
│   └── user/           # User dashboard
├── config/             # Configuration files
├── database/           # SQL schemas & migrations
├── api/                # API routes & controllers
└── scripts/            # Deployment & maintenance
```

## 🔐 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- Session management
- File upload validation

## 📊 API Endpoints

- `/api/search` - Movie search
- `/api/prices` - Price data
- `/api/admin` - Admin functions
- `/api/user` - User management

## 🧪 Testing

```bash
composer test
npm test
```

## 📈 Performance

- Gzip compression
- Browser caching
- Optimized database queries
- CDN-ready assets

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 📞 Support

For issues and feature requests, please use the GitHub Issues page.

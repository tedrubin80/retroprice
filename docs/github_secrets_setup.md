# 🔐 GitHub Secrets Setup Guide

## How to Add Secrets to Your Repository

1. **Go to your GitHub repository**
2. **Click Settings** (top menu)
3. **Click Secrets and variables** → **Actions** (left sidebar)
4. **Click "New repository secret"**
5. **Add each secret below**

---

## 🔑 Required Secrets

### eBay API Credentials (Production)
```
Name: EBAY_APP_ID
Value: YourApp-YourAppI-PRD-abc123def456

Name: EBAY_CERT_ID  
Value: PRD-abc123def456ghi789jkl012mno345pqr678stu901vwx234

Name: EBAY_DEV_ID
Value: 12345abc-6789-def0-1234-56789abcdef0
```

### eBay API Credentials (Testing) - Optional
```
Name: EBAY_APP_ID_TEST
Value: YourApp-YourAppI-SBX-abc123def456

Name: EBAY_CERT_ID_TEST
Value: SBX-abc123def456ghi789jkl012mno345pqr678

Name: EBAY_DEV_ID_TEST  
Value: 12345abc-6789-def0-1234-56789abcdef0
```

### Database Configuration
```
Name: DATABASE_URL
Value: mysql://username:password@host:port/film_price_guide
```

### Deployment Platform Secrets

#### For Railway Deployment (Recommended)
```
Name: RAILWAY_TOKEN
Value: [Get from Railway dashboard → Account Settings → Tokens]

Name: RAILWAY_SERVICE_ID
Value: [Get from Railway project settings]
```

#### For Render Deployment (Alternative)
```
Name: RENDER_API_KEY
Value: [Get from Render dashboard → Account Settings → API Keys]

Name: RENDER_SERVICE_ID
Value: [Get from your Render service URL]
```

#### For Heroku Deployment (Alternative)
```
Name: HEROKU_API_KEY
Value: [Get from Heroku Account Settings → API Key]
```

### Optional Integrations
```
Name: OMDB_API_KEY
Value: [Your OMDb API key]

Name: TMDB_API_KEY
Value: [Your TMDb API key]

Name: SLACK_WEBHOOK_URL
Value: [For deployment notifications]
```

---

## 📁 Complete Project Structure

```
film-price-guide/
├── .github/                           ← GitHub configuration
│   └── workflows/
│       └── deploy.yml                ← Save the workflow here ⚠️
├── .gitignore                        ← Don't commit sensitive files
├── README.md
├── requirements.txt                  ← Root dependencies (optional)
│
├── backend/                          ← Your Flask application
│   ├── app.py                       ← Main Flask app
│   ├── wsgi.py                      ← Production entry point
│   ├── requirements.txt             ← Python dependencies
│   ├── .env.example                 ← Environment template
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── ebay_api.py             ← Your eBay endpoint
│   │   ├── ebay_deletion.py        ← eBay compliance endpoint
│   │   └── admin_api.py
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── tests/                       ← Test files for GitHub Actions
│       ├── __init__.py
│       ├── test_api.py
│       └── test_services.py
│
├── frontend/                         ← Your HTML/CSS/JS files
│   ├── index.html                   ← Homepage
│   ├── search-results.html
│   ├── item-detail.html
│   ├── dashboard.html
│   ├── backend_admin_config.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── database/
│   ├── schema.sql                   ← MySQL schema
│   └── migrations/
│
└── docs/                            ← Documentation
    ├── api.md
    └── setup.md
```

---

## 🚀 How to Deploy

### Step 1: Push to GitHub
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "🎬 Initial Film Price Guide setup"

# Add GitHub remote
git remote add origin https://github.com/yourusername/film-price-guide.git

# Push to GitHub
git push -u origin main
```

### Step 2: GitHub Actions Automatically Run
- ✅ Tests run automatically on push
- ✅ Security scans execute
- ✅ If tests pass, deploys to production
- ✅ Health checks verify deployment
- ✅ Notifications sent on success/failure

### Step 3: Monitor in GitHub
- **Actions tab**: See workflow runs
- **Settings → Secrets**: Manage credentials
- **Pull requests**: Auto-testing on PRs
- **Issues**: Track bugs and features

---

## 🔧 Workflow Triggers

Your workflow will run when:

| Trigger | Action |
|---------|--------|
| `git push main` | Full test + deploy to production |
| `git push develop` | Run tests only (no deployment) |
| Pull Request to `main` | Run tests + security checks |
| Manual trigger | Can manually run from GitHub Actions tab |

---

## 🐛 Troubleshooting

### Common Issues:

**Workflow not running?**
- Check file is saved as `.github/workflows/deploy.yml`
- Ensure proper YAML formatting (spaces, not tabs)
- Verify branch name matches trigger (`main`)

**Tests failing?**
- Check MySQL schema exists in `database/schema.sql`
- Verify test files exist in `backend/tests/`
- Ensure requirements.txt includes test dependencies

**Deployment failing?**
- Verify all required secrets are set in GitHub
- Check Railway/Render/Heroku credentials
- Review deployment logs in Actions tab

**eBay API errors?**
- Confirm API credentials are correct
- Check eBay Developer Account is active
- Verify environment (sandbox vs production)

### Debug Commands:
```bash
# Test workflow locally
act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04

# Validate YAML syntax  
yamllint .github/workflows/deploy.yml

# Check secrets
gh secret list
```
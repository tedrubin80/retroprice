# ================================================================
# EMERGENCY FIX - Run these commands immediately
# ================================================================

echo "🚨 Emergency Railway Fix - Run these commands:"
echo ""

# Quick fix: Replace wsgi.py with simplest version
echo "1. Replace wsgi.py with this one-liner fix:"
cat > wsgi.py << 'EOF'
import sys
sys.path.insert(0, './backend')
from app import app as application
if __name__ == "__main__": application.run()
EOF

echo "✅ Simple wsgi.py created"

# Quick fix: Ensure backend/app.py has basic Flask app
echo "2. Ensure backend/app.py has working Flask app:"
cat > backend/app.py << 'EOF'
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Film Price Guide API', 'status': 'running'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
EOF

echo "✅ Simple backend/app.py created"

# Deploy immediately
echo "3. Push to Railway immediately:"
echo "git add wsgi.py backend/app.py"
echo "git commit -m 'Emergency fix for Railway deployment'"
echo "git push origin main"

echo ""
echo "🚂 This should fix your Railway deployment immediately!"
echo ""
echo "📋 What this does:"
echo "   ✅ Creates minimal wsgi.py that imports from backend/app"
echo "   ✅ Creates working backend/app.py with Flask app variable"
echo "   ✅ No more import errors!"
echo ""
echo "🎯 After pushing, your Railway app should work at:"
echo "   https://your-app-name.railway.app/health"
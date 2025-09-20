#!/bin/bash

# Domain deployment script for PlayTheList
set -e

echo "🌐 PlayTheList Domain Deployment Script"
echo "======================================"

# Check if domain is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your domain name"
    echo "Usage: ./deploy-domain.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
echo "🎯 Deploying to domain: $DOMAIN"

# Check if running on server
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running as root - good for server setup"
else
    echo "⚠️  Not running as root - some commands may need sudo"
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "1. ✅ Domain purchased and DNS configured"
echo "2. ✅ Server provisioned (VPS/Cloud)"
echo "3. ✅ SSH access to server"
echo "4. ✅ .env file with production values"
echo ""

read -p "Have you completed all checklist items? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please complete the checklist first"
    exit 1
fi

echo ""
echo "🔧 Starting deployment process..."

# Update system packages
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Install Nginx
echo "🌐 Installing Nginx..."
if ! command -v nginx &> /dev/null; then
    apt install nginx -y
    systemctl enable nginx
    systemctl start nginx
else
    echo "✅ Nginx already installed"
fi

# Install Certbot for SSL
echo "🔒 Installing Certbot for SSL certificates..."
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y
else
    echo "✅ Certbot already installed"
fi

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Create production environment file
echo "📝 Creating production environment..."
if [ ! -f ".env.production" ]; then
    cp env.example .env.production
    echo "⚠️  Please edit .env.production with your production values"
    echo "   - Update SPOTIFY_REDIRECT_URI to https://$DOMAIN/callback"
    echo "   - Set ENVIRONMENT=production"
    echo "   - Set DEBUG=false"
    echo "   - Add your production API keys"
fi

# Update Nginx configuration for domain
echo "🌐 Configuring Nginx for domain: $DOMAIN"
cat > /etc/nginx/sites-available/playthelist << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration will be added by Certbot
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone \$binary_remote_addr zone=general:10m rate=30r/m;

    location / {
        limit_req zone=general burst=20 nodelay;
        
        proxy_pass http://localhost:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://localhost:8501/_stcore/health;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        proxy_pass http://localhost:8501;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/playthelist /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

echo ""
echo "🎉 Server setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env.production with your production values"
echo "2. Run: ./setup-ssl.sh $DOMAIN"
echo "3. Run: ./start-production.sh"
echo ""
echo "🔗 Your app will be available at: https://$DOMAIN"

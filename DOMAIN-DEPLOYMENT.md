# 🌐 Domain Deployment Guide - PlayTheList

This guide covers deploying PlayTheList to your own domain with SSL, production security, and monitoring.

## 📋 Prerequisites

### 1. **Domain & DNS**
- ✅ **Domain purchased** (e.g., from Namecheap, GoDaddy, Cloudflare)
- ✅ **DNS configured** to point to your server's IP address
- ✅ **A record**: `yourdomain.com` → `YOUR_SERVER_IP`
- ✅ **CNAME record**: `www.yourdomain.com` → `yourdomain.com`

### 2. **Production Server**
- ✅ **VPS/Cloud Server** (DigitalOcean, AWS, Google Cloud, Linode)
- ✅ **Minimum specs**: 1GB RAM, 1 CPU core, 20GB storage
- ✅ **Operating System**: Ubuntu 20.04+ or similar
- ✅ **SSH access** to the server

### 3. **API Credentials**
- ✅ **Spotify API**: Update redirect URI to `https://yourdomain.com/callback`
- ✅ **OpenAI API**: Production-ready key
- ✅ **YouTube API**: Configured for production

## 🚀 Quick Deployment (3 Steps)

### Step 1: Server Setup
```bash
# On your server, run:
wget https://raw.githubusercontent.com/yourusername/playthelist/main/deploy-domain.sh
chmod +x deploy-domain.sh
./deploy-domain.sh yourdomain.com
```

### Step 2: SSL Certificate
```bash
# After server setup, run:
./setup-ssl.sh yourdomain.com
```

### Step 3: Start Production
```bash
# Start the application:
./start-production.sh
```

## 🔧 Manual Deployment Steps

### 1. **Server Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. **Configure Firewall**

```bash
# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
```

### 3. **Environment Configuration**

Create `.env.production`:
```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Spotify API (update redirect URI)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://yourdomain.com/callback
SPOTIFY_SCOPE=playlist-modify-public

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# YouTube/Google API
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_API_KEY=your_youtube_api_key

# Redis (with password for security)
REDIS_URL=redis://:your-secure-redis-password@redis:6379/0
REDIS_PASSWORD=your-secure-redis-password

# Security
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Rate limiting (adjust for production)
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_MINUTES=60
```

### 4. **Nginx Configuration**

Create `/etc/nginx/sites-available/playthelist`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration (added by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/m;

    location / {
        limit_req zone=general burst=20 nodelay;
        
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
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
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/playthelist /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 5. **SSL Certificate**

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run

# Set up auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 6. **Deploy Application**

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🔍 Verification & Testing

### 1. **Health Checks**
```bash
# Test application health
curl https://yourdomain.com/health

# Test SSL certificate
curl -I https://yourdomain.com

# Check all services
docker-compose -f docker-compose.prod.yml ps
```

### 2. **Security Testing**
```bash
# Test SSL rating
curl -s "https://api.ssllabs.com/api/v3/analyze?host=yourdomain.com"

# Test security headers
curl -I https://yourdomain.com
```

### 3. **Performance Testing**
```bash
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com

# Load testing (optional)
ab -n 100 -c 10 https://yourdomain.com/
```

## 📊 Monitoring & Maintenance

### 1. **Log Monitoring**
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f app

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
```

### 2. **Health Monitoring**
- **Uptime monitoring**: Use services like UptimeRobot, Pingdom
- **SSL monitoring**: Monitor certificate expiration
- **Performance monitoring**: Track response times and errors

### 3. **Backup Strategy**
```bash
# Backup Redis data
docker-compose -f docker-compose.prod.yml exec redis redis-cli BGSAVE

# Backup application logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env.production docker-compose.prod.yml
```

## 🚨 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew manually
   sudo certbot renew
   ```

2. **Nginx Configuration Errors**
   ```bash
   # Test configuration
   sudo nginx -t
   
   # Reload configuration
   sudo systemctl reload nginx
   ```

3. **Application Not Starting**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs app
   
   # Restart services
   docker-compose -f docker-compose.prod.yml restart
   ```

4. **DNS Issues**
   ```bash
   # Check DNS resolution
   nslookup yourdomain.com
   dig yourdomain.com
   ```

## 💰 Cost Estimation

### **Monthly Costs**
- **VPS/Server**: $5-20/month (DigitalOcean, Linode, Vultr)
- **Domain**: $10-15/year
- **SSL Certificate**: Free (Let's Encrypt)
- **Total**: ~$5-20/month

### **One-time Costs**
- **Domain registration**: $10-15/year
- **Server setup**: Free (using scripts)

## 🎯 Production Checklist

- [ ] Domain purchased and DNS configured
- [ ] Server provisioned and secured
- [ ] SSL certificate installed and auto-renewing
- [ ] Environment variables configured
- [ ] Application deployed and running
- [ ] Health checks passing
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Performance tested
- [ ] Security headers configured

## 🚀 Next Steps

1. **Deploy to your domain** using the scripts above
2. **Set up monitoring** with external services
3. **Configure backups** for data and logs
4. **Set up CI/CD** for automated deployments
5. **Add analytics** to track usage
6. **Implement user authentication** for premium features

---

**🎉 Your PlayTheList application will be live at https://yourdomain.com!**

#!/bin/bash

# SSL certificate setup script for PlayTheList
set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your domain name"
    echo "Usage: ./setup-ssl.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
echo "🔒 Setting up SSL certificate for: $DOMAIN"

# Check if Nginx is running
if ! systemctl is-active --quiet nginx; then
    echo "❌ Error: Nginx is not running"
    echo "Please start Nginx first: sudo systemctl start nginx"
    exit 1
fi

# Check if domain is pointing to this server
echo "🔍 Checking if domain $DOMAIN points to this server..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    echo "⚠️  Warning: Domain $DOMAIN ($DOMAIN_IP) doesn't point to this server ($SERVER_IP)"
    echo "Please update your DNS records first"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Obtain SSL certificate
echo "🔒 Obtaining SSL certificate from Let's Encrypt..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Test certificate renewal
echo "🔄 Testing certificate renewal..."
certbot renew --dry-run

# Set up automatic renewal
echo "⏰ Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Restart Nginx
echo "🔄 Restarting Nginx..."
systemctl restart nginx

# Test SSL
echo "🧪 Testing SSL configuration..."
if curl -s -I https://$DOMAIN | grep -q "HTTP/2 200"; then
    echo "✅ SSL certificate is working!"
    echo "🔗 Your site is now available at: https://$DOMAIN"
else
    echo "❌ SSL setup failed. Please check the configuration."
    exit 1
fi

echo ""
echo "🎉 SSL setup completed successfully!"
echo "🔗 Your PlayTheList app is now available at: https://$DOMAIN"
echo "🔒 SSL certificate will auto-renew every 90 days"

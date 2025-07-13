# 🚀 NotesHub Deployment Guide

This guide will help you deploy NotesHub to production environments.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (recommended for production)
- Redis (optional, for caching)
- Web server (Nginx/Apache)
- Domain name (optional)

## 🛠️ Step-by-Step Deployment

### 1. **Server Setup**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Redis (optional)
sudo apt install redis-server -y
```

### 2. **Project Setup**

```bash
# Clone your project
git clone <your-repo-url>
cd NotesHub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn psycopg2-binary redis
```

### 3. **Database Configuration**

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE noteshub;
CREATE USER noteshub_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE noteshub TO noteshub_user;
\q
```

### 4. **Environment Variables**

Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=noteshub
DB_USER=noteshub_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis (optional)
REDIS_URL=redis://127.0.0.1:6379/1

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. **Django Configuration**

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Create logs directory
mkdir logs

# Test with production settings
python manage.py runserver --settings=noteshub.settings_production
```

### 6. **Gunicorn Configuration**

Create `gunicorn.conf.py`:

```python
# Gunicorn configuration
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 7. **Systemd Service**

Create `/etc/systemd/system/noteshub.service`:

```ini
[Unit]
Description=NotesHub Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/Noteshub
Environment="PATH=/path/to/your/Noteshub/venv/bin"
ExecStart=/path/to/your/Noteshub/venv/bin/gunicorn --config gunicorn.conf.py noteshub.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 8. **Nginx Configuration**

Create `/etc/nginx/sites-available/noteshub`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Static files
    location /static/ {
        alias /path/to/your/Noteshub/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/your/Noteshub/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Frontend files
    location / {
        root /path/to/your/Noteshub/frontend;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Admin interface
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 9. **Enable Services**

```bash
# Enable and start services
sudo systemctl enable noteshub
sudo systemctl start noteshub
sudo systemctl enable nginx
sudo systemctl start nginx

# Enable site
sudo ln -s /etc/nginx/sites-available/noteshub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 10. **SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Production Optimizations

### **Database Optimization**

```sql
-- Add indexes for better performance
CREATE INDEX idx_note_subject ON marketplace_note(subject_id);
CREATE INDEX idx_note_seller ON marketplace_note(seller_id);
CREATE INDEX idx_note_created ON marketplace_note(created_at);
CREATE INDEX idx_note_approved ON marketplace_note(is_approved);
```

### **Caching Configuration**

```python
# In settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### **Monitoring**

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor logs
sudo journalctl -u noteshub -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🚨 Security Checklist

- [ ] Change default Django secret key
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up firewall rules
- [ ] Configure database with strong passwords
- [ ] Set up regular backups
- [ ] Enable security headers
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging

## 📊 Performance Monitoring

### **Django Debug Toolbar (Development)**

```bash
pip install django-debug-toolbar
```

### **Production Monitoring**

- **New Relic**: Application performance monitoring
- **Sentry**: Error tracking and monitoring
- **Prometheus + Grafana**: Metrics and visualization

## 🔄 Backup Strategy

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump noteshub > backup_$DATE.sql
gzip backup_$DATE.sql

# Keep only last 7 days
find . -name "backup_*.sql.gz" -mtime +7 -delete
```

## 🆘 Troubleshooting

### **Common Issues**

1. **502 Bad Gateway**: Check if Gunicorn is running
2. **Static files not loading**: Run `collectstatic`
3. **Database connection errors**: Check PostgreSQL service
4. **Permission denied**: Check file permissions

### **Useful Commands**

```bash
# Check service status
sudo systemctl status noteshub
sudo systemctl status nginx

# View logs
sudo journalctl -u noteshub -n 50
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart noteshub
sudo systemctl restart nginx
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify all services are running
3. Test each component individually
4. Review security configurations

---

**Happy Deploying! 🚀** 
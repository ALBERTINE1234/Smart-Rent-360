# SmartRent360 Backend - Setup & Deployment Guide

## Overview
This guide provides step-by-step instructions for setting up and deploying the SmartRent360 Django REST Framework backend.

## Table of Contents
1. [Development Setup](#development-setup)
2. [Database Setup](#database-setup)
3. [Running the Server](#running-the-server)
4. [Testing](#testing)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Development Setup

### Step 1: Clone the Repository
```bash
cd smartrent360
```

### Step 2: Create Python Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements_new.txt
```

**Required Packages:**
- Django 4.2.11
- djangorestframework 3.14.0
- django-cors-headers 4.3.1
- django-filter 23.5
- python-decouple 3.8
- mysqlclient 2.2.0
- pillow 10.1.0
- django-environ 0.11.2

### Step 4: Configure Environment Variables

Create a `.env` file in the project root (`smartrent360/smartrent360/.env`):

```env
# Django Settings
SECRET_KEY=your-very-secret-key-here-change-in-production
DEBUG=True

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartrent360
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306

# Optional Settings
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generate a secure SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Database Setup

### Step 1: Create MySQL Database

```bash
# Open MySQL command line
mysql -u root -p

# Create database
CREATE DATABASE smartrent360 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional but recommended)
CREATE USER 'smartrent'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON smartrent360.* TO 'smartrent'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 2: Run Migrations

```bash
# Create migration files from models
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create tables for rest_framework (Token auth)
python manage.py migrate rest_framework
```

### Step 3: Create Superuser

```bash
python manage.py createsuperuser
# Follow the prompts to create admin user
```

### Step 4: Load Initial Data (Optional)

You can create property types and amenities through the admin panel or via management commands:

```python
# Create via Django shell
python manage.py shell

from properties_app.models import PropertyType, PropertyAmenity

PropertyType.objects.create(name='Apartment', description='Modern apartment')
PropertyType.objects.create(name='House', description='Standalone house')
PropertyType.objects.create(name='Land', description='Land for agriculture or construction')
PropertyType.objects.create(name='Room', description='Single room rental')

PropertyAmenity.objects.create(name='WiFi', icon='wifi')
PropertyAmenity.objects.create(name='Parking', icon='parking')
PropertyAmenity.objects.create(name='Garden', icon='leaf')
PropertyAmenity.objects.create(name='Gym', icon='dumbbell')
PropertyAmenity.objects.create(name='Pool', icon='swimming')

exit()
```

---

## Running the Server

### Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000/api/v1/`

**Admin Panel:** `http://localhost:8000/admin/`

### Running with Different Port

```bash
python manage.py runserver 8080
```

### Running on All Interfaces

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
python manage.py test users_app
python manage.py test properties_app
python manage.py test bookings_app
```

### Run with Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## Production Deployment

### Step 1: Update Settings for Production

Update `.env` file:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Update `settings.py`:
```python
# Disable CORS for production (or restrict to your domain)
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Add security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Step 2: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 3: Use Production Server

Install Gunicorn:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn smartrent360.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Step 4: Setup Nginx (Reverse Proxy)

Install Nginx:
```bash
# Ubuntu/Debian
sudo apt-get install nginx

# macOS
brew install nginx
```

Create Nginx configuration (`/etc/nginx/sites-available/smartrent360`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /path/to/smartrent360/staticfiles/;
    }

    location /media/ {
        alias /path/to/smartrent360/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:
```bash
sudo ln -s /etc/nginx/sites-available/smartrent360 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Setup SSL Certificate

Using Let's Encrypt:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Step 6: Setup Systemd Service

Create `/etc/systemd/system/smartrent360.service`:
```ini
[Unit]
Description=SmartRent360 Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/smartrent360
Environment="PATH=/path/to/smartrent360/venv/bin"
ExecStart=/path/to/smartrent360/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    smartrent360.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartrent360
sudo systemctl start smartrent360
```

### Step 7: Setup Database Backups

Create a backup script (`backup_db.sh`):
```bash
#!/bin/bash
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/path/to/backups"
mysqldump -u root -p$MYSQL_PASSWORD smartrent360 > $BACKUP_DIR/smartrent360_$DATE.sql
gzip $BACKUP_DIR/smartrent360_$DATE.sql
```

Schedule with cron:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup_db.sh
```

---

## Monitoring & Logging

### Enable Logging

Add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/smartrent360/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### Monitor Application Health

Setup monitoring tools:
- **Sentry** for error tracking
- **New Relic** for performance monitoring
- **ELK Stack** for centralized logging

---

## Troubleshooting

### Common Issues

**1. Module not found errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements_new.txt

# Reinstall problematic packages
pip install --upgrade --force-reinstall package-name
```

**2. Database connection errors**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u root -p -h localhost
```

**3. Permission errors on Linux**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/smartrent360/media/
sudo chmod -R 755 /path/to/smartrent360/media/
```

**4. Static files not loading**
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput
```

**5. CORS errors**
- Update `CORS_ALLOWED_ORIGINS` in settings.py
- Verify frontend URL matches allowed origins

**6. Token authentication issues**
- Create token: `python manage.py drf_create_token username`
- Verify token in request headers
- Check if user exists in database

---

## Performance Optimization

### Database Optimization
```python
# Use select_related for foreign keys
from django.db.models import Prefetch
Property.objects.select_related('landlord').prefetch_related('images')

# Add database indexes
class Property(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'district']),
            models.Index(fields=['created_at']),
        ]
```

### API Optimization
```python
# Use pagination
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Use caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def get_properties(request):
    pass
```

---

## Maintenance

### Regular Tasks

1. **Weekly**
   - Monitor error logs
   - Check database size
   - Review server resources

2. **Monthly**
   - Update dependencies
   - Review security updates
   - Backup database

3. **Quarterly**
   - Performance optimization
   - Code review
   - Update documentation

---

## Support & Resources

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **MySQL Docs**: https://dev.mysql.com/doc/

---

## License

This project is proprietary software.

---

**Last Updated**: May 2026

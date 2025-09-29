Production Deployment
===================

Comprehensive guide for deploying the Personal Finance application in production environments.

.. contents:: Table of Contents
   :local:
   :depth: 3

.. toctree::
   :maxdepth: 2

   Docker Deployment <deployment/docker>
   Cloud Platforms <deployment/cloud>
   Security Hardening <deployment/security>
   Monitoring <deployment/monitoring>
   Backup & Recovery <deployment/backup>

Deployment Overview
-------------------

The Personal Finance application supports multiple deployment strategies:

* **Docker Containerization**: Complete containerized deployment with docker-compose
* **Cloud Platform Integration**: Support for AWS, GCP, Azure, Heroku, and Render
* **Traditional VPS**: Direct deployment on virtual private servers
* **Kubernetes**: Scalable container orchestration for enterprise deployments

Architecture Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~

**Minimum Production Requirements:**

+----------------+------------------+
| Component      | Minimum Specs    |
+================+==================+
| CPU            | 2 cores          |
+----------------+------------------+
| RAM            | 4GB              |
+----------------+------------------+
| Storage        | 50GB SSD         |
+----------------+------------------+
| Database       | PostgreSQL 13+   |
+----------------+------------------+
| Cache          | Redis 6+         |
+----------------+------------------+
| Python         | 3.11+            |
+----------------+------------------+

**Recommended Production Setup:**

+----------------+------------------+
| Component      | Recommended      |
+================+==================+
| CPU            | 4+ cores         |
+----------------+------------------+
| RAM            | 8GB+             |
+----------------+------------------+
| Storage        | 100GB+ SSD       |
+----------------+------------------+
| Load Balancer  | Nginx/HAProxy    |
+----------------+------------------+
| SSL/TLS        | Let's Encrypt    |
+----------------+------------------+
| Monitoring     | Prometheus/Grafana|
+----------------+------------------+

Quick Deployment Guide
----------------------

Using Docker Compose (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/personal-finance.git
   cd personal-finance

   # Copy environment template
   cp .env.example .env.production

   # Edit production environment variables
   nano .env.production

   # Deploy with docker-compose
   docker-compose -f docker-compose.production.yml up -d

   # Run initial setup
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic --noinput
   docker-compose exec web python manage.py createsuperuser

**Required Environment Variables:**

.. code-block:: bash

   # .env.production
   DJANGO_SETTINGS_MODULE=config.settings.production

   # Security
   DJANGO_SECRET_KEY=your-very-long-secret-key-here
   DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

   # Database
   DATABASE_URL=postgresql://user:password@postgres:5432/personal_finance

   # External APIs
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
   YAHOO_FINANCE_API_KEY=your-yahoo-finance-key

   # Email (optional)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password

   # Redis
   REDIS_URL=redis://redis:6379/0

Manual VPS Deployment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install system dependencies
   sudo apt install -y python3.11 python3.11-dev python3.11-venv \\
       postgresql postgresql-contrib redis-server nginx git \\
       build-essential libpq-dev

   # Create application user
   sudo useradd -m -s /bin/bash finance
   sudo usermod -aG sudo finance

   # Switch to application user
   sudo su - finance

   # Clone and setup application
   git clone https://github.com/yourusername/personal-finance.git
   cd personal-finance

   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Setup environment
   cp .env.example .env
   # Edit .env with your production values

   # Database setup
   sudo -u postgres createdb personal_finance
   sudo -u postgres createuser --interactive finance

   # Run migrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser

Docker Deployment
-----------------

Production Docker Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Dockerfile.production
   FROM python:3.11-slim

   # Set environment variables
   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1
   ENV DJANGO_SETTINGS_MODULE=config.settings.production

   # Install system dependencies
   RUN apt-get update && apt-get install -y \\
       build-essential \\
       libpq-dev \\
       curl \\
       && rm -rf /var/lib/apt/lists/*

   # Create app user
   RUN useradd --create-home --shell /bin/bash app

   # Set work directory
   WORKDIR /app

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Change ownership of files
   RUN chown -R app:app /app
   USER app

   # Collect static files
   RUN python manage.py collectstatic --noinput

   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
       CMD curl -f http://localhost:8000/health/ || exit 1

   # Expose port
   EXPOSE 8000

   # Start command
   CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"--workers\", \"3\", \"config.wsgi:application\"]

Docker Compose for Production
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # docker-compose.production.yml
   version: '3.8'

   services:
     web:
       build:
         context: .
         dockerfile: Dockerfile.production
       ports:
         - \"8000:8000\"
       environment:
         - DJANGO_SETTINGS_MODULE=config.settings.production
       env_file:
         - .env.production
       depends_on:
         - postgres
         - redis
       volumes:
         - static_volume:/app/staticfiles
         - media_volume:/app/media
       restart: unless-stopped
       networks:
         - personal_finance_network

     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: personal_finance
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./backups:/backups
       ports:
         - \"5432:5432\"
       restart: unless-stopped
       networks:
         - personal_finance_network

     redis:
       image: redis:7-alpine
       volumes:
         - redis_data:/data
       ports:
         - \"6379:6379\"
       restart: unless-stopped
       networks:
         - personal_finance_network

     nginx:
       image: nginx:alpine
       ports:
         - \"80:80\"
         - \"443:443\"
       volumes:
         - ./compose/production/nginx:/etc/nginx/conf.d
         - static_volume:/app/staticfiles
         - media_volume:/app/media
         - ./certbot/conf:/etc/letsencrypt
         - ./certbot/www:/var/www/certbot
       depends_on:
         - web
       restart: unless-stopped
       networks:
         - personal_finance_network

     certbot:
       image: certbot/certbot
       volumes:
         - ./certbot/conf:/etc/letsencrypt
         - ./certbot/www:/var/www/certbot
       command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@domain.com --agree-tos --no-eff-email -d your-domain.com -d www.your-domain.com

     price-feed:
       build:
         context: .
         dockerfile: Dockerfile.production
       command: python manage.py start_price_feed --interval 30 --batch-size 50
       environment:
         - DJANGO_SETTINGS_MODULE=config.settings.production
       env_file:
         - .env.production
       depends_on:
         - postgres
         - redis
       restart: unless-stopped
       networks:
         - personal_finance_network

   volumes:
     postgres_data:
     redis_data:
     static_volume:
     media_volume:

   networks:
     personal_finance_network:
       driver: bridge

Nginx Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: nginx

   # compose/production/nginx/default.conf
   upstream django_app {
       server web:8000;
   }

   # Redirect HTTP to HTTPS
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;

       location /.well-known/acme-challenge/ {
           root /var/www/certbot;
       }

       location / {
           return 301 https://$host$request_uri;
       }
   }

   # HTTPS server
   server {
       listen 443 ssl http2;
       server_name your-domain.com www.your-domain.com;

       # SSL configuration
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

       # SSL security settings
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
       ssl_prefer_server_ciphers off;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 10m;

       # Security headers
       add_header Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\";
       add_header X-Content-Type-Options nosniff;
       add_header X-Frame-Options DENY;
       add_header X-XSS-Protection \"1; mode=block\";
       add_header Referrer-Policy \"strict-origin-when-cross-origin\";

       # Gzip compression
       gzip on;
       gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

       # Client max body size
       client_max_body_size 10M;

       # Static files
       location /static/ {
           alias /app/staticfiles/;
           expires 1y;
           add_header Cache-Control \"public, immutable\";
       }

       # Media files
       location /media/ {
           alias /app/media/;
           expires 1M;
           add_header Cache-Control \"public\";
       }

       # WebSocket support
       location /ws/ {
           proxy_pass http://django_app;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection \"upgrade\";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 86400s;
           proxy_send_timeout 86400s;
       }

       # Application
       location / {
           proxy_pass http://django_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_redirect off;
       }
   }

Cloud Platform Deployment
--------------------------

Heroku Deployment
~~~~~~~~~~~~~~~~~

**Procfile:**

.. code-block:: text

   web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
   release: python manage.py migrate && python manage.py collectstatic --noinput
   worker: python manage.py start_price_feed

**app.json:**

.. code-block:: json

   {
     \"name\": \"Personal Finance\",
     \"description\": \"Personal finance management application\",
     \"keywords\": [\"django\", \"finance\", \"portfolio\"],
     \"env\": {
       \"DJANGO_SECRET_KEY\": {
         \"description\": \"Django secret key\",
         \"generator\": \"secret\"
       },
       \"ALPHA_VANTAGE_API_KEY\": {
         \"description\": \"Alpha Vantage API key for market data\"
       },
       \"DJANGO_SETTINGS_MODULE\": {
         \"value\": \"config.settings.production\"
       }
     },
     \"addons\": [
       \"heroku-postgresql:mini\",
       \"heroku-redis:mini\"
     ],
     \"buildpacks\": [
       {\"url\": \"heroku/python\"}
     ]
   }

**Deployment Commands:**

.. code-block:: bash

   # Install Heroku CLI
   brew install heroku/brew/heroku  # macOS

   # Login to Heroku
   heroku login

   # Create application
   heroku create your-finance-app

   # Set environment variables
   heroku config:set DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
   heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production
   heroku config:set ALPHA_VANTAGE_API_KEY=your-api-key

   # Add addons
   heroku addons:create heroku-postgresql:mini
   heroku addons:create heroku-redis:mini

   # Deploy
   git push heroku main

   # Scale workers
   heroku ps:scale web=1 worker=1

AWS ECS Deployment
~~~~~~~~~~~~~~~~~~

**ECS Task Definition:**

.. code-block:: json

   {
     \"family\": \"personal-finance\",
     \"networkMode\": \"awsvpc\",
     \"requiresCompatibilities\": [\"FARGATE\"],
     \"cpu\": \"512\",
     \"memory\": \"1024\",
     \"executionRoleArn\": \"arn:aws:iam::account:role/ecsTaskExecutionRole\",
     \"taskRoleArn\": \"arn:aws:iam::account:role/ecsTaskRole\",
     \"containerDefinitions\": [
       {
         \"name\": \"web\",
         \"image\": \"your-account.dkr.ecr.region.amazonaws.com/personal-finance:latest\",
         \"portMappings\": [
           {
             \"containerPort\": 8000,
             \"protocol\": \"tcp\"
           }
         ],
         \"environment\": [
           {\"name\": \"DJANGO_SETTINGS_MODULE\", \"value\": \"config.settings.production\"}
         ],
         \"secrets\": [
           {\"name\": \"DJANGO_SECRET_KEY\", \"valueFrom\": \"arn:aws:ssm:region:account:parameter/personal-finance/secret-key\"},
           {\"name\": \"DATABASE_URL\", \"valueFrom\": \"arn:aws:ssm:region:account:parameter/personal-finance/database-url\"}
         ],
         \"logConfiguration\": {
           \"logDriver\": \"awslogs\",
           \"options\": {
             \"awslogs-group\": \"/ecs/personal-finance\",
             \"awslogs-region\": \"us-east-1\",
             \"awslogs-stream-prefix\": \"ecs\"
           }
         },
         \"healthCheck\": {
           \"command\": [\"CMD-SHELL\", \"curl -f http://localhost:8000/health/ || exit 1\"],
           \"interval\": 30,
           \"timeout\": 5,
           \"retries\": 3,
           \"startPeriod\": 60
         }
       }
     ]
   }

**Deploy Script:**

.. code-block:: bash

   #!/bin/bash
   # deploy-aws.sh

   # Build and push Docker image
   docker build -t personal-finance -f Dockerfile.production .
   docker tag personal-finance:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/personal-finance:latest
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/personal-finance:latest

   # Update ECS service
   aws ecs update-service --cluster personal-finance --service web --force-new-deployment

   # Wait for deployment
   aws ecs wait services-stable --cluster personal-finance --services web

Google Cloud Run
~~~~~~~~~~~~~~~~

**cloudbuild.yaml:**

.. code-block:: yaml

   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/$PROJECT_ID/personal-finance', '-f', 'Dockerfile.production', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'gcr.io/$PROJECT_ID/personal-finance']
   - name: 'gcr.io/cloud-builders/gcloud'
     args: ['run', 'deploy', 'personal-finance',
            '--image', 'gcr.io/$PROJECT_ID/personal-finance',
            '--region', 'us-central1',
            '--platform', 'managed',
            '--allow-unauthenticated']

**Deploy Commands:**

.. code-block:: bash

   # Set project
   gcloud config set project YOUR_PROJECT_ID

   # Enable APIs
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com

   # Deploy
   gcloud builds submit --config cloudbuild.yaml

Environment Configuration
-------------------------

Production Settings
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config/settings/production.py
   from .base import *

   # Security
   DEBUG = False
   ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
   SECRET_KEY = env('DJANGO_SECRET_KEY')

   # HTTPS settings
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_HSTS_SECONDS = 31536000  # 1 year
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True

   # Database with connection pooling
   DATABASES = {
       'default': {
           **env.db('DATABASE_URL'),
           'CONN_MAX_AGE': 600,
           'OPTIONS': {
               'MAX_CONNS': 20,
               'MIN_CONNS': 5,
           }
       }
   }

   # Redis configuration
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': env('REDIS_URL'),
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
               'IGNORE_EXCEPTIONS': True,
               'CONNECTION_POOL_KWARGS': {
                   'max_connections': 50,
                   'retry_on_timeout': True,
               }
           }
       }
   }

   # Email configuration
   if env('EMAIL_HOST', default=None):
       EMAIL_HOST = env('EMAIL_HOST')
       EMAIL_PORT = env.int('EMAIL_PORT', 587)
       EMAIL_HOST_USER = env('EMAIL_HOST_USER')
       EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
       EMAIL_USE_TLS = True
       DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

   # Logging configuration
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
           'json': {
               '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
               'format': '%(levelname)s %(asctime)s %(name)s %(lineno)d %(message)s'
           },
       },
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/personal-finance/django.log',
               'maxBytes': 1024*1024*10,  # 10MB
               'backupCount': 5,
               'formatter': 'json',
           },
           'console': {
               'level': 'ERROR',
               'class': 'logging.StreamHandler',
               'formatter': 'verbose',
           }
       },
       'root': {
           'level': 'INFO',
           'handlers': ['file', 'console'],
       },
       'loggers': {
           'django': {
               'level': 'INFO',
               'handlers': ['file'],
               'propagate': False,
           },
           'personal_finance': {
               'level': 'INFO',
               'handlers': ['file'],
               'propagate': False,
           }
       }
   }

   # Performance settings
   USE_TZ = True
   USE_I18N = True
   USE_L10N = True

   # Static and media files
   STATIC_ROOT = '/app/staticfiles'
   MEDIA_ROOT = '/app/media'

   # API rate limiting
   REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
       'anon': '100/hour',
       'user': '1000/hour',
       'premium': '10000/hour'
   }

   # Market data settings
   MARKET_DATA_UPDATE_INTERVAL = 30  # seconds
   MARKET_DATA_CACHE_TIMEOUT = 300   # 5 minutes

Environment Variables Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.production.example

   # Django Core Settings
   DJANGO_SETTINGS_MODULE=config.settings.production
   DJANGO_SECRET_KEY=your-very-long-secret-key-minimum-50-characters-long
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com,api.your-domain.com

   # Database Configuration
   DATABASE_URL=postgresql://username:password@host:port/database_name

   # Redis Configuration
   REDIS_URL=redis://username:password@host:port/database_number

   # External API Keys
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
   YAHOO_FINANCE_API_KEY=your-yahoo-finance-api-key
   IEX_CLOUD_API_KEY=your-iex-cloud-api-key

   # Email Configuration (Optional)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@domain.com
   EMAIL_HOST_PASSWORD=your-app-specific-password
   DEFAULT_FROM_EMAIL=noreply@your-domain.com

   # Security Settings
   SECURE_SSL_REDIRECT=True
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True

   # Performance Settings
   MARKET_DATA_UPDATE_INTERVAL=30
   MARKET_DATA_CACHE_TIMEOUT=300

   # File Storage (Optional - for cloud storage)
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
   AWS_S3_REGION_NAME=us-east-1

   # Monitoring (Optional)
   SENTRY_DSN=your-sentry-dsn
   NEW_RELIC_LICENSE_KEY=your-new-relic-key

SSL/TLS Configuration
---------------------

Let's Encrypt with Certbot
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install certbot
   sudo apt install certbot python3-certbot-nginx

   # Get certificates
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com

   # Verify auto-renewal
   sudo certbot renew --dry-run

   # Setup auto-renewal cron job
   echo \"0 12 * * * /usr/bin/certbot renew --quiet\" | sudo crontab -

Manual SSL Certificate Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: nginx

   # nginx SSL configuration
   server {
       listen 443 ssl http2;
       server_name your-domain.com;

       ssl_certificate /path/to/your/certificate.crt;
       ssl_certificate_key /path/to/your/private.key;
       ssl_dhparam /path/to/dhparam.pem;

       # Modern SSL configuration
       ssl_protocols TLSv1.3 TLSv1.2;
       ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
       ssl_prefer_server_ciphers off;

       # OCSP stapling
       ssl_stapling on;
       ssl_stapling_verify on;
       ssl_trusted_certificate /path/to/chain.crt;
       resolver 8.8.8.8 8.8.4.4 valid=300s;
       resolver_timeout 5s;
   }

Database Optimization
---------------------

PostgreSQL Production Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- PostgreSQL optimization settings
   -- Add to postgresql.conf

   # Memory settings
   shared_buffers = 256MB                 # 25% of RAM
   effective_cache_size = 1GB             # 75% of RAM
   work_mem = 4MB                         # Per connection
   maintenance_work_mem = 64MB

   # Checkpoint settings
   checkpoint_completion_target = 0.9
   wal_buffers = 16MB

   # Connection settings
   max_connections = 100

   # Query planner
   random_page_cost = 1.1                 # For SSD storage
   effective_io_concurrency = 200         # For SSD storage

   # Logging
   log_min_duration_statement = 1000      # Log slow queries
   log_checkpoints = on
   log_connections = on
   log_disconnections = on

Database Connection Pooling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Using pgbouncer for connection pooling
   # pgbouncer.ini
   [databases]
   personal_finance = host=localhost port=5432 dbname=personal_finance

   [pgbouncer]
   listen_port = 6432
   listen_addr = 127.0.0.1
   auth_type = trust
   auth_file = /etc/pgbouncer/userlist.txt
   admin_users = postgres
   stats_users = postgres
   pool_mode = transaction
   server_reset_query = DISCARD ALL
   max_client_conn = 100
   default_pool_size = 20

Backup and Monitoring
--------------------

Automated Backups
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # backup_script.sh

   DATE=$(date +\"%Y%m%d_%H%M%S\")
   BACKUP_DIR=\"/backups\"
   DB_NAME=\"personal_finance\"

   # Create backup directory
   mkdir -p $BACKUP_DIR

   # Database backup
   pg_dump -h localhost -U postgres $DB_NAME > $BACKUP_DIR/db_$DATE.sql

   # Compress backup
   gzip $BACKUP_DIR/db_$DATE.sql

   # Upload to S3 (optional)
   aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-backup-bucket/database/

   # Clean old backups (keep 30 days)
   find $BACKUP_DIR -name \"db_*.sql.gz\" -mtime +30 -delete

   echo \"Backup completed: db_$DATE.sql.gz\"

Health Checks and Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # health/views.py
   from django.http import JsonResponse
   from django.db import connection
   from django.core.cache import cache
   from django.utils import timezone

   def health_check(request):
       \"\"\"Comprehensive health check endpoint.\"\"\"

       health_status = {
           'status': 'healthy',
           'timestamp': timezone.now().isoformat(),
           'checks': {}
       }

       # Database check
       try:
           with connection.cursor() as cursor:
               cursor.execute('SELECT 1')
               health_status['checks']['database'] = 'healthy'
       except Exception as e:
           health_status['checks']['database'] = f'unhealthy: {str(e)}'
           health_status['status'] = 'unhealthy'

       # Cache check
       try:
           cache.set('health_check', 'ok', 10)
           if cache.get('health_check') == 'ok':
               health_status['checks']['cache'] = 'healthy'
           else:
               health_status['checks']['cache'] = 'unhealthy: cache not working'
               health_status['status'] = 'degraded'
       except Exception as e:
           health_status['checks']['cache'] = f'unhealthy: {str(e)}'
           health_status['status'] = 'degraded'

       # Disk space check
       import shutil
       free_space = shutil.disk_usage('/')[2] / (1024**3)  # GB
       if free_space > 1:  # At least 1GB free
           health_status['checks']['disk_space'] = f'healthy: {free_space:.1f}GB free'
       else:
           health_status['checks']['disk_space'] = f'warning: {free_space:.1f}GB free'
           health_status['status'] = 'degraded'

       status_code = 200 if health_status['status'] == 'healthy' else 503
       return JsonResponse(health_status, status=status_code)

Troubleshooting
---------------

Common Deployment Issues
~~~~~~~~~~~~~~~~~~~~~~~~

**Memory Issues:**

.. code-block:: bash

   # Check memory usage
   free -h
   ps aux --sort=-%mem | head -20

   # Optimize Django memory usage
   # In settings.py:
   DEBUG = False  # Always in production
   CONN_MAX_AGE = 0  # If having connection issues

**Database Connection Issues:**

.. code-block:: bash

   # Test database connection
   python manage.py dbshell

   # Check PostgreSQL logs
   tail -f /var/log/postgresql/postgresql-*.log

   # Verify database settings
   python manage.py shell
   >>> from django.db import connection
   >>> connection.ensure_connection()

**SSL/TLS Issues:**

.. code-block:: bash

   # Test SSL certificate
   openssl s_client -connect your-domain.com:443 -servername your-domain.com

   # Check certificate expiry
   echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates

**Performance Issues:**

.. code-block:: bash

   # Monitor system resources
   htop
   iotop
   nethogs

   # Django performance profiling
   pip install django-debug-toolbar
   pip install django-silk

Rollback Procedures
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Docker rollback
   docker-compose -f docker-compose.production.yml down
   docker tag your-app:previous-version your-app:latest
   docker-compose -f docker-compose.production.yml up -d

   # Database rollback (if needed)
   python manage.py migrate app_name 0001_initial

   # Git rollback
   git revert <commit-hash>
   git push origin main

See Also
--------

* :doc:`../config/security` - Security configuration and hardening
* :doc:`../modules/realtime` - Real-time service deployment considerations
* :doc:`../api/rest_endpoints` - API deployment and rate limiting
* :doc:`../config/django_settings` - Django configuration for production

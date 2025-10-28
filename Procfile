# Process types for 12-factor app deployment
web: daphne -b 0.0.0.0 -p $PORT config.asgi:application
worker: celery -A config worker --loglevel=info --concurrency=2
beat: celery -A config beat --loglevel=info
flower: celery -A config flower --port=5555

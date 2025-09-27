web: gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --worker-class uvicorn.workers.UvicornWorker config.asgi:application
worker: celery -A config.celery_app worker --loglevel=infoweb: DJANGO_SETTINGS_MODULE=config.settings.production gunicorn --bind 0.0.0.0:$PORT config.wsgi

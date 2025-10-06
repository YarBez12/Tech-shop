web: gunicorn conf.wsgi:application --workers=3 --timeout=60
worker: celery -A conf worker -l INFO
beat: celery -A conf beat -l INFO
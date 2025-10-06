web: gunicorn conf.wsgi:application --workers=1 --threads=2 --timeout=60 --max-requests=500 --max-requests-jitter=50
worker: celery -A conf worker -l INFO
beat: celery -A conf beat -l INFO
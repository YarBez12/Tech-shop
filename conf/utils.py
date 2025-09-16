import redis
from django.conf import settings

r = redis.Redis.from_url(settings.REDIS_URL)
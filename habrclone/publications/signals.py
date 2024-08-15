from django.conf import settings
import redis

r = redis.Redis(host = settings.REDIS_HOST,
                port = settings.REDIS_PORT,
                db = settings.REDIS_DB)

def likes_changed(sender, instance, action, **kwargs):
    app_name = instance._meta.app_label
    instance_id = instance.id

    instance_key = f'{app_name}:{instance_id}'
    rating_key = f'{instance_key}:rating'

    if action == "post_add":
        r.incr(rating_key)
    elif action == "post_remove":
        r.decr(rating_key)
    
def dislikes_changed(sender, instance, action, **kwargs):
    app_name = instance._meta.app_label
    instance_id = instance.id

    instance_key = f'{app_name}:{instance_id}'
    rating_key = f'{instance_key}:rating'

    if action == "post_add":
        r.decr(rating_key)
    elif action == "post_remove":
        r.incr(rating_key)

from conf.utils import r

def get_category_views(category_id):
    score = r.zscore('category:views:zset', category_id)
    return int(score) if score else 0


def zincrby_product_view(product_id):
    r.zincrby('product:views:zset', 1, product_id)


def get_product_views(product_id):
    score = r.zscore('product:views:zset', product_id)
    return int(score) if score else 0

def zincrby_category_view(category_id):
    r.zincrby('category:views:zset', 1, category_id)


def like_product(user_id, product_id):
    r.sadd(f'favourite:user:{user_id}', product_id)

def unlike_product(user_id, product_id):
    r.srem(f'favourite:user:{user_id}', product_id)

def get_user_favourites(user_id):
    return r.smembers(f'favourite:user:{user_id}')


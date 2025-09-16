from conf.utils import r

def get_top_viewed_products(limit=10, oversample=5):
    return [int(pid) for pid in r.zrevrange('product:views:zset', 0, limit * max(1, oversample) - 1)]
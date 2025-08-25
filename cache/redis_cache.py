import time

import redis
from config import conf
class SimpleCache:
    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value
    def delete(self, key):
        del self._cache[key]
    def clear(self):
        self._cache.clear()
    def keys(self):
        return self._cache.keys()
    def setex(self, key, value, ex):
        self._cache[key] = value
        self._cache[key + '_expire'] = time.time() + ex
    def getex(self, key):
        if key + '_expire' in self._cache:
            if self._cache[key + '_expire'] < time.time():
                del self._cache[key]
                del self._cache[key + '_expire']

data_cache = SimpleCache()

if conf().get('redis_host', None) \
    and conf().get('redis_pass', None) \
    and conf().get('redis_port', None) \
    and conf().get('redis_db', None) :
    data_cache = redis.Redis(connection_pool=redis.ConnectionPool(
        host=conf().get('redis_host', None),
        password=conf().get('redis_pass', None),
        port=conf().get('redis_port', None),
        db=int(conf().get('redis_db', None)),
        protocol=3))
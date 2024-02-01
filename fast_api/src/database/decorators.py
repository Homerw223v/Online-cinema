from models.abstract_models.abstract_cache import AbstractCache


async def caching(cache: AbstractCache):
    async def _caching(func):
        async def inner(*args, **kwargs):
            cache_key = f"{'_'.join(*args)}_{'_'.join(**kwargs)}"
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached
            output = func(*args, **kwargs)
            await cache.set(cache_key, output)
            return output

        return inner

    return _caching

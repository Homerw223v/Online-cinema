import os
import time

from elasticsearch import Elasticsearch
from redis import Redis
from concurrent import futures
import backoff


@backoff.on_predicate(wait_gen=backoff.expo, max_time=120)
def wait_for(service: Elasticsearch | Redis) -> None:
    return service.ping()


if __name__ == '__main__':
    es = Elasticsearch(hosts=os.environ.get('ES_HOST'))
    redis = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))

    with futures.ThreadPoolExecutor() as executor:
        executor.map(wait_for, (es, redis))

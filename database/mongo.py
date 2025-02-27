from contextlib import contextmanager

from pymongo import MongoClient

from conf.mongodb import mongodb_config


@contextmanager
def get_mongo_client():
    client = MongoClient(mongodb_config.host, int(mongodb_config.port))
    try:
        yield client
    finally:
        client.close()

def get_db():
    with get_mongo_client() as client:
        yield client[mongodb_config.database]

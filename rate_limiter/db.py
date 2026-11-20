
from pymongo import MongoClient

from .config import DB_NAME, MONGO_URI

mongo = MongoClient(MONGO_URI, tz_aware=True, serverSelectionTimeoutMS=2000)
rate_limit = mongo[DB_NAME]["rate_limit"]


def init_indexes():
    # One document per client; also makes the upsert safe.
    rate_limit.create_index("clientId", unique=True)
    # TTL index: MongoDB deletes the document once expiresAt has passed.
    rate_limit.create_index("expiresAt", expireAfterSeconds=0)

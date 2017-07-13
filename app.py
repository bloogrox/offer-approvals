import pymongo

import settings


mongo_client = pymongo.MongoClient(settings.MONGO_URI)
mongo_database = mongo_client.get_default_database()

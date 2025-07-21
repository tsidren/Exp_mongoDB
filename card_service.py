from pymongo import MongoClient, errors

class MongoDB:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="cardgame", collection_name="playing_cards"):
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except errors.ConnectionFailure:
            raise Exception("Could not connect to MongoDB.")



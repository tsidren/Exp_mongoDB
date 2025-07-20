from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create database and collection
db = client["cardgame"]
cards = db["playing_cards"]

# Clear previous data
cards.delete_many({})

# Sample playing cards
sample_cards = [
    {"suit": "Hearts", "rank": "Ace", "color": "Red", "value": 1},
    {"suit": "Hearts", "rank": "King", "color": "Red", "value": 13},
    {"suit": "Spades", "rank": "Queen", "color": "Black", "value": 12},
    {"suit": "Clubs", "rank": "10", "color": "Black", "value": 10},
    {"suit": "Diamonds", "rank": "7", "color": "Red", "value": 7},
    {"suit": "Hearts", "rank": "5", "color": "Red", "value": 5},
]

# CREATE
cards.insert_many(sample_cards)

# READ
print("All Cards:")
for card in cards.find():
    print(card)

# UPDATE
cards.update_one({"rank": "5", "suit": "Hearts"}, {"$set": {"value": 15}})
print("\nUpdated Card:")
print(cards.find_one({"rank": "5", "suit": "Hearts"}))

# DELETE
cards.delete_one({"rank": "7", "suit": "Diamonds"})
print("\nRemaining Cards After Deletion:")
for card in cards.find():
    print(card)

from flask import Flask, jsonify, request
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from bson.errors import InvalidId
# from card_service import MongoDB

app = Flask(__name__)
VALID_SUITS = {"Spades", "Hearts", "Clubs", "Diamonds"}
VALID_RANKS = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"}

# mongo = MongoDB()
# collection = mongo.collection
#
#
# def connect_db(uri="mongodb://localhost:27017/"):
#     try:
#         client = MongoClient(uri)
#     except errors.ConnectionFailure:
#         raise Exception("Could not connect to MongoDB.")
#     return client
#
#
# def get_all_databases(client):
#     """Returns a list of all database names."""
#     try:
#         return client.list_database_names()
#     except Exception as e:
#         raise Exception(f"Failed to retrieve databases: {e}")
#
#
# def get_all_collections(client, db_name):
#     """Returns a list of all collection names in the given database."""
#     try:
#         db = client[db_name]
#         return db.list_collection_names()
#     except Exception as e:
#         raise Exception(f"Failed to retrieve collections from '{db_name}': {e}")

# Connect to your MongoDB instance
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["cardgame"]
    collection = db["playing_cards"]
except errors.ConnectionFailure:
    raise Exception("Could not connect to MongoDB.")


def validate_card(data):
    if not data:
        return "No data provided"
    if "rank" not in data or "suit" not in data:
        return "Missing required fields: 'rank' and 'suit'"
    if data["rank"] not in VALID_RANKS:
        return f"Invalid rank: {data['rank']}"
    if data["suit"] not in VALID_SUITS:
        return f"Invalid suit: {data['suit']}"
    return None


def enrich_card(data):
    # Only add color if not provided
    if "suit" in data and "color" not in data:
        if data["suit"] in {"Hearts", "Diamonds"}:
            data["color"] = "Red"
        elif data["suit"] in {"Spades", "Clubs"}:
            data["color"] = "Black"

    rank = data.get("rank", "").upper()
    rank_mapping = {
        "A": 14,
        "K": 13,
        "Q": 12,
        "J": 11,
        "10": 10,
        "9": 9,
        "8": 8,
        "7": 7,
        "6": 6,
        "5": 5,
        "4": 4,
        "3": 3,
        "2": 2
    }

    if rank in rank_mapping and "value" not in data:
        data["value"] = rank_mapping[rank]


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Playing Cards API!",
        "endpoints": ["/cards [GET, POST]", "/cards/<id> [PUT, PATCH, DELETE]"]
    })


@app.route("/cards", methods=["GET"])
def get_all_cards():
    try:
        all_cards = list(collection.find())
        for card in all_cards:
            card["_id"] = str(card["_id"])
        return jsonify(all_cards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET: Get a card by ID
@app.route('/cards/<string:card_id>', methods=['GET'])
def get_card_by_id(card_id):
    try:
        card = collection.find_one({"_id": ObjectId(card_id)})
        if card:
            card["_id"] = str(card["_id"])
            return jsonify(card), 200
        return jsonify({"error": "Card not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400


# GET: Search cards by field (e.g., /cards/search?suit=Spades)
@app.route('/cards/search', methods=['GET'])
def search_cards():
    try:
        query = dict(request.args)
        result = list(collection.find(query))
        for card in result:
            card['_id'] = str(card['_id'])
        if not result:
            return jsonify({"Message": "no data found"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cards", methods=["POST"])
def add_card():
    try:
        data = request.json
        error = validate_card(data)
        if error:
            return jsonify({"error": error}), 400
        enrich_card(data)
        result = collection.insert_one(data)
        return jsonify({"inserted_id": str(result.inserted_id)}), 201
    except errors.DuplicateKeyError:
        return jsonify({"error": """Duplicate card entry: This card already exists in the database. 
                        Duplicates are not allowed."""}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cards/<string:card_id>", methods=["PUT"])
def replace_card(card_id):
    try:
        data = request.json
        error = validate_card(data)
        if error:
            return jsonify({"error": error}), 400
        enrich_card(data)
        result = collection.replace_one({"_id": ObjectId(card_id)}, data)
        if result.matched_count == 0:
            return jsonify({"error": "Card not found"}), 404
        return jsonify({"modified_count": result.modified_count}), 200
    except errors.DuplicateKeyError:
        return jsonify({"error": "the card already exist, cannot update this card with the same data"}), 409
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cards/<string:card_id>", methods=["PATCH"])
def update_card(card_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        result = collection.update_one({"_id": ObjectId(card_id)}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "Card not found"}), 404
        return jsonify({"modified_count": result.modified_count}), 200
    except errors.DuplicateKeyError:
        return jsonify({"error": "the card already exist, cannot update this card with the same data"}), 409
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cards/<string:card_id>", methods=["DELETE"])
def delete_card(card_id):
    try:
        result = collection.delete_one({"_id": ObjectId(card_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Card not found"}), 404
        return jsonify({"deleted_count": result.deleted_count}), 200
    except InvalidId:
        return jsonify({"error": "Invalid ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cards', methods=['DELETE'])
def delete_all_cards():
    try:
        result = collection.delete_many({})
        return jsonify({"message": f"All cards deleted ({result.deleted_count})"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

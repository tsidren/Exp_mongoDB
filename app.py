from flask import Flask, jsonify, request
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)

# Connect to your MongoDB instance
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["cardgame"]
    cards = db["playing_cards"]
except errors.ConnectionFailure:
    raise Exception("Could not connect to MongoDB.")


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Playing Cards API!",
        "endpoints": ["/cards [GET, POST]", "/cards/<id> [PUT, PATCH, DELETE]"]
    })


@app.route("/cards", methods=["GET"])
def get_all_cards():
    try:
        all_cards = list(cards.find())
        for card in all_cards:
            card["_id"] = str(card["_id"])
        return jsonify(all_cards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET: Get a card by ID
@app.route('/cards/<string:card_id>', methods=['GET'])
def get_card_by_id(card_id):
    try:
        card = cards.find_one({"_id": ObjectId(card_id)})
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
        result = list(cards.find(query))
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
        if not data:
            return jsonify({"error": "No data provided"}), 400
        result = cards.insert_one(data)
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
        if not data:
            return jsonify({"error": "No data provided"}), 400
        result = cards.replace_one({"_id": ObjectId(card_id)}, data)
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
        result = cards.update_one({"_id": ObjectId(card_id)}, {"$set": data})
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
        result = cards.delete_one({"_id": ObjectId(card_id)})
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
        result = cards.delete_many({})
        return jsonify({"message": f"All cards deleted ({result.deleted_count})"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

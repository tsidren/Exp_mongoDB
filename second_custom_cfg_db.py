import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
"""
to run this file first create a new instance of the DB server 

mongod --config custom-mongo.cfg

"""
def connect_to_mongodb(host='localhost', port=27017):
    """
    Establishes a connection to the MongoDB server.
    """
    try:
        client = MongoClient(host, port)
        # The ping command is cheap and does not require auth.
        # It's a good way to check if the connection is alive.
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB at {host}:{port}")
        return client
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during connection: {e}")
        return None

def get_database_and_collection(client, db_name, collection_name):
    """
    Gets a specific database and collection from the MongoDB client.
    """
    if not client:
        return None, None
    db = client[db_name]
    collection = db[collection_name]
    print(f"Using database: '{db_name}' and collection: '{collection_name}'")
    return db, collection

# --- CREATE Operations ---
def create_document(collection, document):
    """
    Inserts a single document into the collection.
    """
    try:
        result = collection.insert_one(document)
        print(f"Inserted document with ID: {result.inserted_id}")
        return result.inserted_id
    except PyMongoError as e:
        print(f"Error inserting document: {e}")
        return None

def create_many_documents(collection, documents):
    """
    Inserts multiple documents into the collection.
    """
    try:
        result = collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} documents. IDs: {result.inserted_ids}")
        return result.inserted_ids
    except PyMongoError as e:
        print(f"Error inserting multiple documents: {e}")
        return None

# --- READ Operations ---
def find_one_document(collection, query):
    """
    Finds and returns a single document matching the query.
    """
    try:
        document = collection.find_one(query)
        if document:
            print(f"Found one document: {document}")
        else:
            print(f"No document found for query: {query}")
        return document
    except PyMongoError as e:
        print(f"Error finding one document: {e}")
        return None

def find_documents(collection, query={}):
    """
    Finds and returns all documents matching the query.
    If query is empty, returns all documents in the collection.
    """
    try:
        documents = collection.find(query)
        print(f"Found documents for query {query}:")
        found_count = 0
        for doc in documents:
            print(f"  {doc}")
            found_count += 1
        if found_count == 0:
            print("  No documents found.")
        return list(collection.find(query)) # Return as a list for easier handling outside
    except PyMongoError as e:
        print(f"Error finding documents: {e}")
        return []

# --- UPDATE Operations ---
def update_one_document(collection, query, new_values):
    """
    Updates a single document matching the query with new values.
    """
    try:
        # $set operator is used to update specific fields
        result = collection.update_one(query, { "$set": new_values })
        print(f"Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error updating one document: {e}")
        return False

def update_many_documents(collection, query, new_values):
    """
    Updates multiple documents matching the query with new values.
    """
    try:
        result = collection.update_many(query, { "$set": new_values })
        print(f"Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error updating many documents: {e}")
        return False

# --- DELETE Operations ---
def delete_one_document(collection, query):
    """
    Deletes a single document matching the query.
    """
    try:
        result = collection.delete_one(query)
        print(f"Deleted {result.deleted_count} document(s).")
        return result.deleted_count > 0
    except PyMongoError as e:
        print(f"Error deleting one document: {e}")
        return False

def delete_many_documents(collection, query):
    """
    Deletes multiple documents matching the query.
    """
    try:
        result = collection.delete_many(query)
        print(f"Deleted {result.deleted_count} document(s).")
        return result.deleted_count > 0
    except PyMongoError as e:
        print(f"Error deleting many documents: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    client = connect_to_mongodb("mongodb://localhost", 27018)

    if client:
        db, collection = get_database_and_collection(client, "mydatabase", "mycollection")

        # Corrected check for database and collection objects
        if db is not None and collection is not None:
            # --- Clean up previous data (optional, for fresh start) ---
            print("\n--- Cleaning up existing documents ---")
            delete_many_documents(collection, {}) # Delete all documents

            # --- CREATE Examples ---
            print("\n--- CREATE Operations ---")
            # Create a single document
            doc1 = {"name": "Alice", "age": 30, "city": "New York"}
            create_document(collection, doc1)

            # Create multiple documents
            docs_to_insert = [
                {"name": "Bob", "age": 24, "city": "Los Angeles", "status": "active"},
                {"name": "Charlie", "age": 35, "city": "Chicago", "status": "inactive"},
                {"name": "David", "age": 29, "city": "New York", "status": "active"},
                {"name": "Eve", "age": 40, "city": "Houston", "status": "pending"}
            ]
            create_many_documents(collection, docs_to_insert)

            # --- READ Examples ---
            print("\n--- READ Operations ---")
            # Find one document by name
            find_one_document(collection, {"name": "Alice"})

            # Find all documents
            print("\nAll documents in collection:")
            find_documents(collection)

            # Find documents with a specific city
            print("\nDocuments from New York:")
            find_documents(collection, {"city": "New York"})

            # Find documents with age greater than 30
            print("\nDocuments with age > 30:")
            find_documents(collection, {"age": {"$gt": 30}})

            # --- UPDATE Examples ---
            print("\n--- UPDATE Operations ---")
            # Update Alice's age
            update_one_document(collection, {"name": "Alice"}, {"age": 31, "status": "active"})
            find_one_document(collection, {"name": "Alice"}) # Verify update

            # Update status for all active users to 'online'
            update_many_documents(collection, {"status": "active"}, {"status": "online"})
            print("\nDocuments with updated status (online):")
            find_documents(collection, {"status": "online"})

            # --- DELETE Examples ---
            print("\n--- DELETE Operations ---")
            # Delete Bob
            delete_one_document(collection, {"name": "Bob"})
            find_one_document(collection, {"name": "Bob"}) # Verify deletion

            # Delete all documents from New York
            delete_many_documents(collection, {"city": "New York"})
            print("\nRemaining documents after deletion:")
            find_documents(collection)

            # --- Final check ---
            print("\nFinal state of the collection:")
            find_documents(collection)

        # Close the connection
        client.close()
        print("\nMongoDB connection closed.")

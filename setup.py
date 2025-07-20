from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
admin_db = client.admin

# Run serverStatus command to get storage info
server_status = admin_db.command("serverStatus")

# The storage path is in the "process" section
print("MongoDB process info:", server_status.get("process", "N/A"))

# Run getCmdLineOpts to get the full config including dbPath
cmd_line_opts = admin_db.command("getCmdLineOpts")

# Extract dbPath
db_path = cmd_line_opts.get("parsed", {}).get("storage", {}).get("dbPath", "Not Found")

print("MongoDB is storing data at:", db_path)

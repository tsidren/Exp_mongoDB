## Playing around in MongoDB
by default the data is store in this place. 
`C:\Program Files\MongoDB\Server\X.X\data`<br>
but to save the DB someplace else you have to change the path in the `mongod.cfg`
stored in `C:\Program Files\MongoDB\Server\X.X\bin\mongod.cfg`
```
storage:
  dbPath: C:\Program Files\MongoDB\Server\X.X\data
  
  // change this path to whatever you want
```
restart MongoDB service after changing the path 
```
net stop MongoDB
net start MongoDB
```
but remember this will change the path for all of your DB instances 
so other projects which are already made on the previous path will not be able to access their instances

a safer solution would be 
#### option 1: Start a Separate MongoDB Instance with Custom Path
```
mongod --dbpath "D:\MyProject\mongo-data" --port 27018
```
#### option 2: Run Different Config Files for Different Projects
```
# custom-mongo.cfg
storage:
  dbPath:   # new storage path

# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path:  # new log path 

# network interfaces
net:
  port: 27018   # new port to run the DB instance
  bindIp: 127.0.0.1
```
then run to open a MongoDB instance with that config file (either give Absolute path to the config file or `cd` to that dir) 
```
mongod --config custom-mongo.cfg
```

the database server will keep on running (for the normal config file, until OS restart)
to check if it is running
```
tasklist /FI "IMAGENAME eq mongod.exe"
```
to close any task running 
```
taskkill /F /IM mongod.exe
```

---

## Playing around in Mongosh CLI
<code> show dbs</code> this lists all the Databases in your system<br>
<code> use cardgame</code> this will switch to your DB "cardgame"<br>
<code> show collections </code> list collections in current DB<br>
<code> db.playing_cards.find()</code> to print all documents stored in the collection "playing_cards"<br>
<code>db.createCollection("name")</code> Creates a new collection<br>
<code>db.playing_cards.drop()</code> Drops the collection<br>
<code>db.dropDatabase()</code> Drops the current database<br>
<code> db.playing_cards.getIndexes()</code> Lists all indexes on a collection

### Read
```
db.collection.find()
db.collection.findOne({ key: "value" })
db.collection.find({ key: "value" }).pretty()


//To limit or skip results:
db.collection.find().limit(5)
db.collection.find().skip(10).limit(5)

//Case-insensitive regex example:
db.collection.find({ field: { $regex: "^abc$", $options: "i" } })
```
### Aggregate
```
// Group and count by field
db.collection.aggregate([
  { $group: { _id: "$field", count: { $sum: 1 } } }
])

// Match, sort, limit
db.collection.aggregate([
  { $match: { status: "active" } },
  { $sort: { createdAt: -1 } },
  { $limit: 10 }
])
```


#### Group by Color
```
db.playing_cards.aggregate([
  { $group: { _id: "$color", count: { $sum: 1 } } }
])
```
output 
``` output
{
  _id: 'Black',
  count: 2
}
{
  _id: 'Red',
  count: 3
}
```
### Insert New Card
```
db.playing_cards.insertOne({
  suit: "Spades",
  rank: "3",
  color: "Black",
})
```
### Update a Card

```
db.playing_cards.updateOne(
  { suit: "spades", rank: "3" },
  { $set: { value: "3" } }
)
```

similarly we have <code>updateMany()</code>

so after adding duplicate documents<br>
building index will give an error <br>
<code>MongoServerError[DuplicateKey]: Index build failed: 1775b928-62a2-4062-b74b-908f973c762a: Collection cardgame.playing_cards ( 973957dc-16ae-4f3a-b0f2-bd8c4ec61cc5 ) :: caused by :: E11000 duplicate key error collection: </code>

this can be used to remove duplicates and keep only one


```
db.playing_cards.aggregate([
  {
    $group: {
      _id: { suit: "$suit", rank: "$rank", color: "$color" },
      ids: { $addToSet: "$_id" },
      count: { $sum: 1 }
    }
  },
  { $match: { count: { $gt: 1 } } }
]).forEach(function(doc) {
  doc.ids.shift(); // remove first (keep one)
  db.playing_cards.deleteMany({ _id: { $in: doc.ids } });
});
```

### To prevent duplicate logical entries, create a composite unique index:
```
db.playing_cards.createIndex(
  { suit: 1, rank: 1, color: 1 },
  { unique: true }
)
```
now adding duplicate entries will give an error<br>
<code> MongoServerError: E11000 duplicate key error collection: cardgame.playing_cards </code>

### print all of the duplicate entries 
```
db.playing_cards.aggregate([
  {
    $group: {
      _id: { suit: "$suit", rank: "$rank", color: "$color" },
      count: { $sum: 1 },
      docs: { $push: "$_id" }
    }
  },
  { $match: { count: { $gt: 1 } } }
])
```
### Delete
#### Delete Queen of Spades:
```
db.playing_cards.deleteOne({ rank: "Queen", suit: "Spades" })
```
#### Delete all red cards:
```
db.playing_cards.deleteMany({ color: "Red" })
```

### indexes
```
// Create Index
db.collection.createIndex({ field: 1 })        // ascending index
db.collection.createIndex({ field: -1 })       // descending index
db.collection.createIndex({ field1: 1, field2: 1 })  // compound index

// View indexes
db.collection.getIndexes()

// Drop index
db.collection.dropIndex("indexName")
```

###  Maintenance & Info
```
db.stats()                         // DB stats
db.collection.stats()              // Collection stats
db.currentOp()                    // Current running ops
db.serverStatus()                 // Server status overview
db.collection.validate()          // Validate collection integrity
```

### Data Validation & Analysis
| Command                      | What It Does                              |
| ---------------------------- | ----------------------------------------- |
| `db.<collection>.validate()` | Validates the structure of the collection |
| `db.stats()`                 | Gives stats on the current database       |
| `db.<collection>.stats()`    | Collection-specific statistics            |
| `db.serverStatus()`          | Returns an overview of server health      |

### User Management 
```
use admin
db.createUser({                // to create a User with only readWrite access to cardgame db
  user: "myUsername",
  pwd: "myPassword",
  roles: [
    { role: "readWrite", db: "cardgame" }
  ]
})
db.getUsers()                  // View All Users
db.dropUser("name")            // Delete a User
db.grantRolesToUser("username", [...])      // Grants roles to a user
db.updateUser("myUsername", {     // Update an Existing User
  pwd: "newPassword",
  roles: [ { role: "read", db: "cardgame" } ]
})

```
| Role                                      | Description                                 |
| ----------------------------------------- | ------------------------------------------- |
| `read`                                    | Read-only access to a database              |
| `readWrite`                               | Read & write access                         |
| `dbAdmin`                                 | DB administrative operations                |
| `userAdmin`                               | Manage users/roles                          |
| `clusterAdmin`                            | Administer the entire MongoDB cluster       |
| `readAnyDatabase`, `readWriteAnyDatabase` | Access to all databases (requires admin DB) |


## MongoDB Regex Guide

{ field: { $regex: `pattern`, $options: "`flags`" } }
- $regex: regex pattern
- $options: optional flags (case-insensitive, multiline, etc.)

### Common Regex Rules
| Pattern | Description                     | Example Match       |
| ------ | ------------------------------- |---------------------|
| `^abc` | Starts with `abc`               | `abc123`, `abcde`   |
| `abc$` | Ends with `abc`                 | `123abc`, `deabc`   |
| `.`    | Any single character            | `a`, `1`, `#`       |
| `a*`   | 0 or more of `a`                | `  `, `a`, `aaa`    |
| `a+`   | 1 or more of `a`                | `a`, `aa`           |
| `a?`   | 0 or 1 of `a`                   | ` `, `a`            |
| `[abc]` | Match any one of a, b, or c     | `a`, `b`, `c`       |
| `[^abc]` | Match anything except a, b, or c | `d`, `1`            |
| `[a-z]` | Match any lowercase letter      | `f`, `z`            |
| `(abc)` | Grouping                        |                     |
| `a{2}` | Exactly 2 of `a`                | `aa`                |
| `a{2,}` | At least 2 of `a`               | `aa`, `aaa`, `aaaa` |
| `a{2,4}` | Between 2 and 4 `a`             | `aa`, `aaa`, `aaaa` |
### Regex Flags (`$options`)
| Flag | Meaning                    | Example                      |
| ---- | -------------------------- | ---------------------------- |
| `i`  | Case-insensitive           | `^a` with `i` matches `A`    |
| `m`  | Multi-line                 | Affects `^` and `$` matching |
| `x`  | Ignore whitespace/comments | Less common in Mongo usage   |
| `s`  | Dot matches newline        | `.` matches `\n` too         |
#### Examples 
```
// Find names starting with A or a
db.people.find({ name: { $regex: "^a", $options: "i" } })

// Find ranks ending in "0"
db.playing_cards.find({ rank: { $regex: "0$" } })

// Find suits with exactly 5 characters
db.playing_cards.find({ suit: { $regex: "^.{5}$" } })

// Cards with "a" or "e" in rank
db.playing_cards.find({ rank: { $regex: "[ae]" } })

// Case-sensitive exact match (regex form)
db.playing_cards.find({ suit: { $regex: "^Hearts$" } })
```

---

## Optimising the MongoDB query 

**1. Use Indexes**
```
# Create an index on "suit" field
collection.create_index("suit")

# Compound index for multiple fields
collection.create_index([("suit", 1), ("rank", 1)])
```
**2. Use Projection to Limit Fields**\
By default, MongoDB returns full documents. That’s wasteful for large documents.
```
cards.find({"suit": "Hearts"}, {"rank": 1, "_id": 0}
# Only returns rank of cards with suit = Hearts.
```

**3. Avoid `$where` and Regex Without Anchors**\
$where executes JavaScript on each document — very slow.
```
# Bad
cards.find({"$where": "this.suit == 'Spades'"})
# Good
cards.find({"suit": "Spades"})
```
**4.  Use `$in` Instead of Multiple `$or`**
```
# Bad
cards.find({"$or": [{"suit": "Spades"}, {"suit": "Hearts"}]})
# Good
cards.find({"suit": {"$in": ["Spades", "Hearts"]}})
```
**5. Paginate Instead of Returning Everything**\
- **Why?**\
Loading entire collections into memory is a killer.\
- **Use skip + limit:**
```
cards.find().skip(0).limit(10)  # Page 1
cards.find().skip(10).limit(10)  # Page 2
```
**6. Use Covered Queries**\
 **covered query** is one where **all fields used** are in the index and **no documents are fetched**.
```
# Index: suit + rank
collection.create_index([("suit", 1), ("rank", 1)])

# Query and projection use only indexed fields
cards.find({"suit": "Spades"}, {"suit": 1, "rank": 1, "_id": 0})
```
**7. Avoid Negation and Inequality Where Possible**
```
# This can't use index efficiently
cards.find({"suit": {"$ne": "Spades"}})

# Instead, filter in app code if you must
```
**8. Keep Your Documents Lightweight**\
MongoDB loads full documents even if you return partial fields.\
➡️ Avoid:
   - Deep nesting
   - Very large arrays
   - Excessive embedded documents

**9. Use Aggregation Pipeline When Appropriate**
```
pipeline = [
    {"$match": {"suit": "Hearts"}},
    {"$group": {"_id": "$rank", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]

cards.aggregate(pipeline)
```
**10. Use Connection Pooling & Batch Operations**
    
    If using Python or backend language:
    
    - Reuse MongoClient instead of creating it repeatedly
    
    - Use insert_many, bulk_write instead of many insert_one
    
**Note:**

Use `explain()` to Analyze Your Query Plan
```
cards.find({"suit": "Spades"}).explain("executionStats")
or 
db.playing_cards.find({ suit: "Spades" }).explain("executionStats")
```
output: 
```
// for no index 
"winningPlan": {
  "stage": "COLLSCAN"
},
"executionStats": {
  "totalDocsExamined": 10000,
  "totalKeysExamined": 0
}
// Means it scanned all documents — no index.

// with indexes 
"winningPlan": {
  "stage": "FETCH",
  "inputStage": {
    "stage": "IXSCAN",
    "keyPattern": { "suit": 1 }
  }
},
"executionStats": {
  "totalDocsExamined": 100,
  "totalKeysExamined": 100
}
// This shows MongoDB used an index scan (IXSCAN) — much faster.
```

---

## Flask API

- run the MongoDB server `net start MongoDB` this will run the server in default port `27017`
- run the API (i.e. execute `app.py`)
- open `Postman`

### Checking the API 
- select `GET` method 
- type the link for the API `http://127.0.0.1:5000/`
- click `send` 

in Response, you will see 
```
{
    "endpoints": [
        "/cards [GET, POST]",
        "/cards/<id> [PUT, PATCH, DELETE]"
    ],
    "message": "Welcome to the Playing Cards API!"
}
```

### running GET method

- select `GET` method 
- type the link for the API `http://127.0.0.1:5000/cards`
- click `send` 

in Response, you will see all the data stored in `playing_cards` DB

**OR**
- type the link for the API `http://127.0.0.1:5000/cards/<_id>`  where <_id> is  document id 
(i.e. `687cefcae6934e8424e0a845`)
    ```
    http://localhost:5000/cards/687cefcae6934e8424e0a845
    ```
- click `send` 

in Response, you will see only if there is a match
```
{
    "_id": "687cefcae6934e8424e0a845",
    "color": "Red",
    "rank": "4",
    "suit": "Hearts",
    "value": 4
}
// when the specified ID document is not found 
{
    "error": "Card not found"
}
// when the specified is totally wrong (ID format)
{
    "error": "Invalid ID format"
}
```

**OR**

to specifically use two queries use `http://127.0.0.1:5000/cards/search?suit=Hearts&color=Red`
or a one `http://127.0.0.1:5000/cards/search?color=Black`
- type the link for the API `http://127.0.0.1:5000/cards/search?color=Black`
- click `send` 

in Response, you will see a List containing all the documents matching the criteria
```
[
    {
        "_id": "687cb55dc10863b0d6a9507e",
        "color": "Black",
        "rank": "Queen",
        "suit": "Spades",
        "value": 12
    },
    {
        "_id": "687cb55dc10863b0d6a9507f",
        "color": "Black",
        "rank": "10",
        "suit": "Clubs",
        "value": 10
    }
]
// for no matched, an empty list 
{
    "Message": "no data found"
}
```



### running POST method

- select `POST` method 
- type the link for the API `http://127.0.0.1:5000/cards`
- select `body` then `raw` and then `JSON` Specifying that you want to send a JSON file to create document
- type 
```
{
  "suit": "Hearts",
  "rank": "2",
  "color": "Red",
  "value": 2
}
```
- click `send` 

in Response, you will see the _id of the document (and this is used to reference data stored in the document)
```
{
    "inserted_id": "687cefcae6934e8424e0a845"
}

// and yes you will see an error message if you again try to insert the same data into an indexed Database.
{
    "error": "Duplicate card entry: This card already exists in the database. Duplicates are not allowed."
}
```
### running PUT method

- select `PUT` method
- type the link for the API `http://localhost:5000/cards/<_id>`   where <_id> is  document id 
(i.e. `687cefcae6934e8424e0a845`)
    ```
    http://localhost:5000/cards/687cefcae6934e8424e0a845
    ```
- select `body` then `raw` and then `JSON` Specifying that you want to send a JSON file to Replace document
- type 
```
{
  "suit": "Hearts",
  "rank": "3",
  "color": "Red",
  "value": 3
}
```
- click `send` 

in Response for success, you will see the modified count (all the documents modified in that query).
```
// this will also be displayed if the same ID is being replaced with the same data
{
    "modified_count": 1
}
// if the card details already exist in other documents. then the response will be 
{
    "error": "the card already exist, cannot update this card with the same data"
}
// if ID does'nt match with any stored IDs
{
    "error": "Card not found"
}
```

### running PATCH method

- select `PATCH` method 
- type the link for the API `http://localhost:5000/cards/<_id>`   where <_id> is  document id 
(i.e. `687cefcae6934e8424e0a845`)
    ```
    http://localhost:5000/cards/687cefcae6934e8424e0a845
    ```
- select `body` then `raw` and then `JSON` Specifying that you want to send a JSON file to update document
- type 
```
{
  "rank": "4",
  "value": 4
}
```
- click `send` 

in Response for success, you will see the modified count (all the documents modified in that query).
```
// the modified_count will become 0, if you try to again change it to the same value(it's already been done)
{
    "modified_count": 1
}
// if the card details already exist in other documents. then the response will be 
{
    "error": "the card already exist, cannot update this card with the same data"
}
// if ID does'nt match with any stored IDs
{
    "error": "Card not found"
}
```
and for doing this again the count in the Response will be 0


### running DELETE method

- select `DELETE` method 
- type the link for the API `http://localhost:5000/cards/<_id>`   where <_id> is  document id 
(i.e. `687cbc72f365deb1ce4b3843`)
    ```
    http://localhost:5000/cards/687cbc72f365deb1ce4b3843
    ```
- click `send` 

in Response for success, you will see the modified count (all the documents modified in that query).
```
{
    "deleted_count": 1
}
// if ID does'nt match with any stored IDs
{
    "error": "Card not found"
}
```
and for doing this again the count in the Response will be 0 (because no ID is found)


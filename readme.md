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
<code> db.playing_cards.aggregate([
  { $group: { _id: "$color", count: { $sum: 1 } } }
])</code>

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
<code>
db.playing_cards.insertOne({
  suit: "Spades",
  rank: "3",
  color: "Black",
})</code>

### Update a Card
<code>
db.playing_cards.updateOne(
  { suit: "spades", rank: "3" },
  { $set: { value: "3" } }
)
</code>
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
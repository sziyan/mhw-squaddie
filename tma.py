from pymongo import MongoClient

URI = 'mongodb+srv://ndg:P%40ssw0rd@ndg-3djuk.gcp.mongodb.net/tma?retryWrites=true&w=majority'


conn = MongoClient(URI)
db = conn['tma']

#get list of collection names in connected db
# collection_name = db.list_collection_names()

#set the collection name to connect to
collection = db.tma_test

#count number of items in collection
# result = collection.count_documents({})
# print(result)

#search collection
# result = collection.find({'plays':'5'})
# print(list(result))

#Insert single entry into collection
# collection.insert_one({'song':'Wanna One', 'plays':'5'})
# print(list(collection.find({'song':'Wanna One'})))

#Insert multiple entries into collection
# song_list = [{'song':'Wanna Cry','plays':'5'}, {'song':'Wanna Shy','plays':'10'}]
# collection.insert_many(song_list)
# print(list(collection.find({'song':'Wanna Cry'})))

#find and update entry
# collection.find_one_and_update({'song':'Wanna One'}, {'$set': {'plays':'10'}})

#insert entry with new database feature
# collection.insert_one({'song':'Wanna Jump', 'plays':'5', 'publisher':'Wanna Inc'})
# for d in collection.find():
#     print(d)

#delete entry
collection.delete_many({'plays':'5'})
for d in collection.find():
    print(d)
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['FireWatcher']
nodes_collection = db['nodes']
data_collection = db['data']
def insert_node(node_data):
    return nodes_collection.insert_one(node_data).inserted_id



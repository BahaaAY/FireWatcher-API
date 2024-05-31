import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = client.FireWatcher
nodes_collection = db.get_collection('nodes')
data_collection = db.get_collection('data')




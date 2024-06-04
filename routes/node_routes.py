import secrets
from fastapi import APIRouter
from models.node import Node
from database import nodes_collection
from schemas.data import get_last_reading
from passlib.hash import bcrypt

router = APIRouter()

@router.post("/nodes/")
async def register_node( node_data: Node):
    # if not authenticate_token(access_token):
    #     raise HTTPException(status_code=401, detail="Invalid access token")

    # secret_key = secrets.token_urlsafe(32)
        # Generate 32 bytes of random data
    token_bytes = secrets.token_bytes(32)
    # Convert the bytes to a hexadecimal string
    hex_token = token_bytes.hex()
    hashed_secret_key = bcrypt.hash(hex_token)

    node_id = await nodes_collection.insert_one({
        "latitude": node_data.latitude,
        "longitude": node_data.longitude,
        "node_type": node_data.node_type.value,
        "secret_key": hashed_secret_key
    })

    return {"node_id": str(node_id.inserted_id), "secret_key": hex_token}

@router.get("/nodes/")
async def get_nodes():
    nodes = await nodes_collection.find({},{ "secret_key" : 0}).to_list(None)  # Exclude secret_key from response
    nodes_list = []
    for node in nodes:
        node["_id"] = str(node["_id"]) # Convert ObjectId to string
        # get last reading from data collection for this node
        node["last_reading"] = await get_last_reading(node["_id"])
        nodes_list.append(node)
    return {"nodes": nodes_list}

@router.get("/testn")
async def testn():
    print("Test Node req")
    return {"test": "testn"}
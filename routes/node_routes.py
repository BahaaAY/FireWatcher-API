from fastapi import APIRouter, HTTPException
from models.node import Node
from database import nodes_collection, insert_node
import secrets
from passlib.hash import bcrypt

router = APIRouter()

@router.post("/register-node/")
async def register_node( node_data: Node):
    # if not authenticate_token(access_token):
    #     raise HTTPException(status_code=401, detail="Invalid access token")

    secret_key = secrets.token_urlsafe(16)
    hashed_secret_key = bcrypt.hash(secret_key)

    node_id = insert_node({
        "latitude": node_data.latitude,
        "longitude": node_data.longitude,
        "node_type": node_data.node_type.value,
        "secret_key": hashed_secret_key
    })

    return {"node_id": str(node_id), "secret_key": secret_key}

@router.get("/nodes/")
async def get_nodes():
    nodes = nodes_collection.find({},{ "secret_key" : 0})  # Exclude secret_key from response
    nodes_list = []
    for node in nodes:
        node["_id"] = str(node["_id"]) # Convert ObjectId to string
        nodes_list.append(node)
    return {"nodes": nodes_list}

@router.get("/testn")
async def testn():
    print("Test Node req")
    return {"test": "testn"}
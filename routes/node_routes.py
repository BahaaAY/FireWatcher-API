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

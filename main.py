from fastapi import FastAPI
from routes.node_routes import router as node_router

app = FastAPI()

app.include_router(node_router)
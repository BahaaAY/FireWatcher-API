from fastapi import FastAPI
from routes.node_routes import router as node_router
from routes.data_routes import router as data_router

app = FastAPI()

app.include_router(node_router)
app.include_router(data_router)
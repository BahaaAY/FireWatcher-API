import datetime

from pydantic import BaseModel, root_validator

from bson import ObjectId as BsonObjectId
from typing import Any, List

from database import data_collection

class ObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if not BsonObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return BsonObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string', pattern=r'^[0-9a-fA-F]{24}$')

class DataSchema(BaseModel):
    node_id: ObjectId
    humidity:float
    temperature:float
    smoke_value:float
    wind_kph:float
    rain_mm:float
    ffmc:float
    dmc:float
    dc:float
    isi:float
    bui:float
    fwi:float
    fire_risk:bool
    fire: bool
    updated_FWI:bool = False
    timestamp: datetime.datetime = None
    @root_validator(pre=True)  # Use a root validator to set the timestamp
    def set_timestamp(cls, values):
        if values.get('timestamp') is None:
            values['timestamp'] = datetime.datetime.now()
        return values

    
async def insert_data(data: DataSchema):
    data_dict = data.dict()
    data_id = await data_collection.insert_one(data_dict)
    return {"id": str(data_id.inserted_id), "timestamp": data_dict['timestamp']}

async def get_last_reading(node_id: str):
    data = await data_collection.find_one({"node_id": node_id}, sort=[("timestamp", -1)])
    return data


async def get_last_10_readings(node_id: str) -> List[Any]:
    print("123123  1 ",node_id)
    try:
        # Convert node_id to ObjectId
        node_id_obj = ObjectId(node_id)
    except Exception as e:
        print(f"Failed to convert node_id to ObjectId: {e}")
        return []
    print("123123  2 ",type(node_id_obj),node_id_obj)
    print(f"Querying data_collection with node_id: {node_id_obj}")
    nodes = await data_collection.find({},{}).to_list(None)
    print("123123 3 ",nodes)
    return nodes
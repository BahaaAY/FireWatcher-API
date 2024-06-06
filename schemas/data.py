import datetime

from pydantic import BaseModel, root_validator

from bson import ObjectId as BsonObjectId
from typing import Any

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

    
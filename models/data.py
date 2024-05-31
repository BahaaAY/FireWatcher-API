from pydantic import BaseModel, Field


class Data(BaseModel):
    node_id: str = Field(pattern=r"^[0-9a-f]{24}$")
    secret_key: str
    humidity:float
    temperature:float
    smoke_value:float
    
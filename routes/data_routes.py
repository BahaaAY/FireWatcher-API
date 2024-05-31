import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pymongo
from models.node import Node
from database import nodes_collection, insert_node,data_collection
import secrets
from passlib.hash import bcrypt
from utils.fwi_calc import FWIClass 
from dotenv import load_dotenv
from utils.weather_api import fetch_weather_data
from bson.objectid import ObjectId
from joblib import load
import numpy as np
import pandas as pd


# Load environment variables from .env file
load_dotenv()
model_path = '../ml_model/voting_classifier.joblib'
router = APIRouter()

class Data(BaseModel):
    node_id: str = Field(pattern=r"^[0-9a-f]{24}$")
    secret_key: str
    humidity:float
    temperature:float
    smoke_value:float
    

@router.post('/data/')
async def save_readings(node_data: Data):
    print("hello ")
    node = nodes_collection.find_one({"_id": ObjectId(node_data.node_id)})

    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")

    # Check if the provided secret key matches the hashed secret key in the database
    if not bcrypt.verify(node_data.secret_key.encode('utf-8'), node['secret_key'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid secret key")

    last_node_reading = data_collection.find_one(
    {"_id": ObjectId(node_data.node_id)},
    sort=[("timestamp", pymongo.DESCENDING)]  # Replace 'timestamp' with your actual timestamp field
)
    ffmc0 = 85.0
    dmc0 = 6.0
    dc0 = 15.0
    current_date = datetime.datetime.now()

    if last_node_reading:
        # get the last FFMC readings
        x=1
    print("node ",node)
    weather_data = await fetch_weather_data(node["latitude"], node["longitude"])
    print(weather_data)
    mth = int(current_date.month)
    fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],weather_data["current"]["precip_mm"])
    ffmc = fwisystem.FFMCcalc(ffmc0)
    dmc = fwisystem.DMCcalc(dmc0,mth)
    dc = fwisystem.DCcalc(dc0,mth)
    isi = fwisystem.ISIcalc(ffmc)
    bui = fwisystem.BUIcalc(dmc,dc)
    fwi = fwisystem.FWIcalc(isi,bui)
    ffmc0 = ffmc
    dmc0 = dmc
    dc0 = dc


    voting_clf = load(model_path)

    data = {
    'month': [current_date.month],
    'Temperature':[node_data.temperature],
    'RH': [node_data.humidity],
    'Ws': [weather_data["current"]["wind_kph"]],
    'Rain': [weather_data["current"]["precip_mm"]],
    'FFMC': [ffmc],
    'DMC': [dmc],
    'DC': [dc],
    'ISI': [isi],
    'BUI': [bui],
    'FWI': [fwi]
}
    
    print("data 123123",data)
    df = pd.DataFrame(data)

    # Make a prediction
    predicted_output = voting_clf.predict(df).tolist()
    print("Predicted Output:", predicted_output)
    return (
        {"ffmc":ffmc,
         "dmc":dmc,
         "dc":dc,
         "isi":isi,
         "bui":bui,
         "fwi":fwi,
         "predicted_output":predicted_output    
         }
        )
    
        

    # If authentication is successful, insert or update additional data
    # update_result = nodes_collection.update_one(
    #     {"_id": pymongo.ObjectId(node_data.node_id)},
    #     {"$set": {"additional_data": node_data.additional_data}}
    # )

    # if update_result.modified_count == 1:
    #     return {"status": "Data updated successfully"}
    # else:
    #     return {"status": "No changes made to the data"}

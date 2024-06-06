from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pymongo
from models.node import Node
from models.data import Data
from schemas.data import DataSchema, insert_data
from database import nodes_collection, data_collection
import secrets
from passlib.hash import bcrypt
from utils.fwi_calc import FWIClass 
from dotenv import load_dotenv
from utils.weather_api import fetch_weather_data
from bson.objectid import ObjectId
from joblib import load
import numpy as np
import pandas as pd
import os



# Load environment variables from .env file
load_dotenv()

# Get the current  directory
curr_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute path to the model
model_path = os.path.join(curr_dir, '..', 'ml_model', 'voting_classifier.joblib')

router = APIRouter()



@router.post('/data/')
async def save_readings(node_data: Data):
    node = await nodes_collection.find_one({"_id": ObjectId(node_data.node_id)})

    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")

    # Check if the provided secret key matches the hashed secret key in the database
    if not bcrypt.verify(node_data.secret_key.encode('utf-8'), node['secret_key'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid secret key")
    

    search_id = ObjectId(node_data.node_id)
    last_node_reading = await data_collection.find_one({"node_id": search_id,"updated_FWI":True}, sort=[("timestamp", -1)])
    print("last node reading: ", last_node_reading)
    
    
    date_string = "2024-06-04 12:10:54.512963"

    # Parse the string into a datetime object using the corresponding format
    # current_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()
    print("current_date 123 ",current_date)
    noon_time = current_date.replace(hour=12, minute=0, second=0, microsecond=0)
    start_window = noon_time - timedelta(minutes=30)
    end_window = noon_time + timedelta(minutes=30)
    updated_fwi = False
    weather_data = await fetch_weather_data(node["latitude"], node["longitude"])
    if last_node_reading is not None:
        last_reading_time = last_node_reading["timestamp"]  # Ensure this is a datetime object
        time_difference = current_date - last_reading_time
        print("time difference : ",time_difference, " ",current_date, " ",last_reading_time)
    # Check if 24 hours have passed since the last update and if current time is around 12 noon
        if time_difference > timedelta(days=1) and (start_window <= current_date <= end_window):
        # Conditions met, proceed with updating
        # USE FFMC0 from the last reading to calculate new FFMC, DMC, DC

            ffmc0 = last_node_reading["ffmc"]
            dmc0 = last_node_reading["dmc"]
            dc0 = last_node_reading["dc"]
            # weather_data = await fetch_weather_data(node["latitude"], node["longitude"])
            print("weather data testing : 1",weather_data)
            mth = int(current_date.month)
            fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],weather_data["current"]["precip_mm"])
            # fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],12)
            ffmc = fwisystem.FFMCcalc(ffmc0)
            dmc = fwisystem.DMCcalc(dmc0,mth)
            dc = fwisystem.DCcalc(dc0,mth)
            isi = fwisystem.ISIcalc(ffmc)
            bui = fwisystem.BUIcalc(dmc,dc)
            fwi = fwisystem.FWIcalc(isi,bui)
            updated_fwi = True
            
    
        else:
        # Conditions not met, do not update FFMC, DMC, DC -> dont calculate ffm, dmc, dc and isi, bui, fwi
        # You can continue to use the last stored values
            print("found reading with timestamp: ", last_node_reading["timestamp"])
            ffmc = last_node_reading["ffmc"]
            dmc = last_node_reading["dmc"]
            dc = last_node_reading["dc"]
            isi = last_node_reading["isi"]
            bui = last_node_reading["bui"]
            fwi = last_node_reading["fwi"]
            updated_fwi = False

    else:
        # No previous reading, check if it's around 12 noon to proceed
        if start_window <= current_date <= end_window:
        # it is around noon, calculate new FFMC, DMC, DC that will be saved (using default values)
            ffmc0 = 85.0
            dmc0 = 6.0
            dc0 = 15.0
            # weather_data = await fetch_weather_data(node["latitude"], node["longitude"])
            print("weather data testing : 2",weather_data)
            mth = int(current_date.month)
            fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],weather_data["current"]["precip_mm"])
            # fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],12)
            ffmc = fwisystem.FFMCcalc(ffmc0)
            dmc = fwisystem.DMCcalc(dmc0,mth)
            dc = fwisystem.DCcalc(dc0,mth)
            isi = fwisystem.ISIcalc(ffmc)
            bui = fwisystem.BUIcalc(dmc,dc)
            fwi = fwisystem.FWIcalc(isi,bui)
            updated_fwi = True
            

        else:
        # Not around noon  calculate new FFMC, DMC, DC that  will be used for calculations but not saved
            ffmc0 = 85.0
            dmc0 = 6.0
            dc0 = 15.0
            # weather_data = await fetch_weather_data(node["latitude"], node["longitude"])
            print("weather data testing : 3",weather_data)
            mth = int(current_date.month)
            fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],weather_data["current"]["precip_mm"])
            # fwisystem = FWIClass(node_data.temperature,node_data.humidity,weather_data["current"]["wind_kph"],12)
            ffmc = fwisystem.FFMCcalc(ffmc0)
            dmc = fwisystem.DMCcalc(dmc0,mth)
            dc = fwisystem.DCcalc(dc0,mth)
            isi = fwisystem.ISIcalc(ffmc)
            bui = fwisystem.BUIcalc(dmc,dc)
            fwi = fwisystem.FWIcalc(isi,bui)
            updated_fwi = False
   
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
    df = pd.DataFrame(data)

    # Make a prediction
    predicted_output = voting_clf.predict(df).tolist()
    #convert to boolean
    predicted_output = [bool(x) for x in predicted_output]

     
    # Insert the data into the database

    data = DataSchema(
        node_id=node_data.node_id,
        humidity=node_data.humidity,
        temperature=node_data.temperature,
        smoke_value=node_data.smoke_value,
        wind_kph=weather_data["current"]["wind_kph"],
        rain_mm=weather_data["current"]["precip_mm"],
        ffmc=ffmc,
        dmc=dmc,
        dc=dc,
        isi=isi,
        bui=bui,
        fwi=fwi,
        fire_risk=predicted_output[0],
        fire=True if node_data.smoke_value >= 1100 else False,
        updated_FWI=updated_fwi
    )

    await insert_data(data)

    return (
        {"FFMC":ffmc,
         "DMC":dmc,
         "DC":dc,
         "ISI":isi,
         "BUI":bui,
         "FWI":fwi,
         "Fire Risk":predicted_output[0],
         "Fire": True if node_data.smoke_value >= 1100 else False

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

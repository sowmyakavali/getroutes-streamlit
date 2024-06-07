# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:47:33 2024

@author: ManojSingh

"""

import os
import requests
from file_save import save_file 


def weather_prediction(df, leg, TAG):
    df['alert']=""
    df['condition'] = ""
    
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY") 
    DAYS = 1   
    
    #We want to avoid unnecessory calls to weatherapi 
    prev_area = ""
    prev_alert = ""
    prev_condition = ""
        
    for idx, row in df.iterrows():                
        if row["Area"] != prev_area:               
            prev_area = row["Area"]
            location = f"{row['latitude']},{row['longitude']}"
            URL = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days={DAYS}&aqi=no&alerts=yes"           
            # REST API to call  
            response = requests.get(URL)
            alert = 'No Alert' 
            condition = 'Not available'
            if response.status_code == 200:
                if response.json()['alerts']['alert']:
                    alert = response.json()['alerts']['alert'][0]['event']                    
                if response.json()['forecast']['forecastday']:
                    condition = response.json()['forecast']['forecastday'][0]['day']['condition']['text']
            else:
                print('!!! WEATHER API FAILED TO RETURN DATA !!!' + URL)
            prev_alert = alert
            prev_condition = condition            
        else:
            alert = prev_alert
            condition = prev_condition
            
        df.at[idx, 'alert'] = alert
        df.at[idx, 'condition'] = condition
    
    #save data to file
    save_file(df, file_name = f"ROUTE_{TAG}_LEG{leg}_all_routes_directions_weather.csv", file_type="csv")
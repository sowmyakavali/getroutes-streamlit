# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:49:24 2024

@author: ManojSingh
"""
import os
import re 
from ibm_watson_machine_learning.foundation_models import Model

from dotenv import load_dotenv
load_dotenv()

#LLM model instance is created as a global object, because it takes 8 seconds to create model object
model_id = os.environ.get("LLM_MODEL_ID")
decoding_method = os.environ.get("LLM_DECODING_METHOD")
if decoding_method == "greedy":
    parameters = { "decoding_method": "greedy", "min_new_tokens": 100, "max_new_tokens": 500, "repetition_penalty": 1 }
else:
    parameters = { "decoding_method": "sample", "min_new_tokens": 100, "max_new_tokens": 500, "repetition_penalty": 1, 
                   "temperature": 0.6, "top_p": 1}

project_id = os.environ.get("WATSONX_PROJECT_ID") 
credentials = {"url" : "https://us-south.ml.cloud.ibm.com",
               "apikey" : os.environ.get("WATSONX_API_KEY")} 

model = Model(  model_id = model_id,
                params = parameters,
                credentials = credentials,
                project_id = project_id
             )


def get_prompt_context(df):
    prompt_context = ""
    
    for routeNo, group in df.groupby("Route No"):
        tt = group.iloc[-1]["cum_duration(sec)"]
        td = group.iloc[-1]["cum_distance(m)"]
        
        a = f"Route Name: {routeNo}\n{routeNo} Travel time: {tt} seconds\n{routeNo} Distance travelled: {td} meters\n{routeNo} locations:\n"
        b = f"{routeNo} Weather:\n"
        
        prev_area = ""
        
        for idx, row in group.iterrows():
            if row["Area"] != prev_area:               
                prev_area = row["Area"]                
                a = a + f"    {row['Area']}" + "\n"                
                b = b + f"    weather alert for {row['Area']} is {row['alert']}\n    weather forecast for {row['Area']} is {row['condition']}\n"
        prompt_context = prompt_context + a +"\n"+ b + "\n"
        
    return prompt_context


def prepare_prompt(routes_weather): 
    
    """input: Takes weather information
        output : Creates end-to-end prompt
    """
    #This high level instruction and question has given best results, with greedy mixtral model
    instruction = """You are route optimization expert. Read below route paths, and weather conditions. 
If only one route name is provided, then give that one route name as the best route, and provide commentary on weather alert and forecast.
Use only the information provided in below text. Don't convert given time and distance to any other unit of measurement like hours and minutes.
Less travel time, and less travel distance are good. Rainy weather, snowy weather, stormy weather are bad. Use folloiwng logic to decide better
travel time and better travel distance. If first route has travel time 3212 seconds and second route has travel time 3322 seconds, then first route is better.
If first route has travel distance 55285 meters and second route has travel distance 57484 meters, then first route is better.
Because 3212 is less than 3322, and 55285 is less than 57484.""" 

    question = """Tell me which route name is better in terms of weather condition, travel time, and travel distance?    
Give reasons for your route selection, under 3 headings 1. Travel Time: 2. Travel Distance: 3. Weather Conditions: . 
Give best route name inside angle brackets like <Route N>. Dont give further explanation after providing conclusion."""

    return f"""<s>[INST]<<SYS>>\n{instruction}\n<</SYS>>\n\n{routes_weather}\n{question}\n[/INST]"""


def get_best_route(input_prompt):
    """input: required prompt to llm
       output: llm  predicted best route reasons and route Number
    """
    #default best route is 0, sometimes when there is only Route 0, the llm response does not conain <Route 0> 
    best_route = '0'
    # model response    
    llm_response = model.generate_text(prompt=input_prompt, guardrails=True)
    # Extract route Number
    matches = re.findall(r'<([^>]+)>', llm_response)
    if len(matches):
        #after split, the last part is best route number 
        best_route = matches[0].split(" ")[-1]
           
    return llm_response, best_route
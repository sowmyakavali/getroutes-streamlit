# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 12:23:27 2024
Sample input data
route_data = {
	"freight_order_number": "6100000501",
	"route_stops": [
		{"stop": 1, "latitude": 0, "longitude": 0, "name": "Leugenestrasse,Biel,Bern,Switzerland"},
		{"stop": 2, "latitude": 0, "longitude": 0, "name": "40 W. Switzerland,Lausanne,Switzerland"},
		{"stop": 3, "latitude": 0, "longitude": 0, "name": "Rue de Lausanne,Geneve,Geneva,Switzerland"},
		{"stop": 4, "latitude": 0, "longitude": 0, "name": "110  Canton of Ticino,Lugano,Switzerland"},
		{"stop": 5, "latitude": 0, "longitude": 0, "name": "Waaghaus-Passage,Interlaken,Bern,Switzerland"}
	]
}
@author: ManojSingh
"""

import os
from googlemap_api import get_routes
from weather_forecasting import weather_prediction
from map_display import display_routes, display_all_bestRoutes
from watsonx_llm import get_prompt_context, prepare_prompt, get_best_route
from file_save import save_file

from streamlit_folium import st_folium, folium_static
import streamlit as st




def convert_route_to_legs(route_data):
    # Sort the list based on the 'stop' value
    route_data['route_stops'] = sorted(route_data['route_stops'], key=lambda x: x['stop'])
    sap_route_stops = route_data['route_stops']
    sap_route_stops
    print('\nORIGINAL ROUTE DATA ==>', sap_route_stops)    
    #Prepare leg list for route
    leg_list = []    
    for idx, stop in enumerate(sap_route_stops):    
        if idx < len(sap_route_stops)-1:
            leg_list.append({'leg': idx+1, 'origin': sap_route_stops[idx]['name'], 'destination': sap_route_stops[idx+1]['name']})
    print('\nLEG LIST ==>', leg_list) 
    return leg_list
         
    
def process_route(route_data, TAG):
    leg_list = convert_route_to_legs(route_data)
    #Run steps to produce best route for each leg 
    #Watsonx LLM Model used in process
    model_id = os.environ.get("LLM_MODEL_ID")
    decoding_method = os.environ.get("LLM_DECODING_METHOD")
    
    #this list will be used to plot all best routes om single map
    routesData_list = []
    
    #Process each leg. Initially each leg has three datapoints (leg, origin,destination)
    #But during below processing 3 more data points will be added (recommendation, map_html, map_all_html)
    for leg in leg_list: 
        origin = leg['origin']
        destination = leg['destination']
        #Get multiple possible routes
        print('\n','*'*10, 'LEG', leg['leg'], '==>', origin, '==>', destination,'*'*10)
        #routesData has this structure {leg:integer, origin:string, destination:string, 
        # org_lat:integer, org_lng:integer, dst_lat:integer, dst_lng:integer, directions_df:dataframe, decoded_routes:{1:list, 2:list}}
        routesData = get_routes(leg['leg'], origin, destination, TAG)    
        
        #Do weather forecast for the routes. Below function call will add two new columns in passed dataframe - alert, condition
        weather_prediction(routesData["directions_df"], leg['leg'], TAG)
        
        #Display possible routes on map
        print('\n','*'*10, 'LEG', leg['leg'], '==>', origin, '==>', destination,'*'*10)
        map_all_html = display_routes(routesData, origin, destination, TAG)
            
        #Prepare prompt to select best route
        prompt_context = get_prompt_context(routesData["directions_df"])
        input_prompt = prepare_prompt(prompt_context)
        print('\n','*'*10, 'LEG', leg['leg'], '==>', origin, '==>', destination,'*'*10)
        print('input_prompt==>', input_prompt)
        
        #Call LLM to select best route 
        llm_response, bestRouteNumber = get_best_route(input_prompt)
        print('\n','*'*10, 'LEG', leg['leg'], '==>', origin, '==>', destination,'*'*10)
        print('bestRouteNumber==>', bestRouteNumber)
        print('llm_response==>', llm_response)
        #Save to file
        final_text = f"Origin : {origin}\nDestination : {destination}\n\n{'_'*100}\nPrompt :\n    {input_prompt}\n\n{'_'*100}\nModel : {model_id}\nDecoding Method: {decoding_method}\n\n{'_'*100}\nLLM response : \n     {llm_response}"
        file_name = f"ROUTE_{TAG}_LEG{str(leg['leg'])}_prompt_and_response.txt"
        save_file(final_text, file_name=file_name, file_type="txt")
        
        #keep outpur in soure data for plotting at the end
        routesData['best_route'] = bestRouteNumber
        routesData['recommendation'] = llm_response
        routesData_list.append(routesData)
        #Display best route on map
        map_html = display_routes(routesData, origin, destination, TAG, bestRouteNumber)
        #Store llm response and map in leg
        leg['recommendation'] = llm_response.replace('<', '&lt;').replace('>', '&gt;') #otherise <> will not be displayed on html
        leg['map_html'] = map_html
        leg['map_all_html'] = map_all_html
    
        # st_folium(map_html, width=250)
        st.subheader('Available routes are...', divider='rainbow')
        folium_static(map_all_html)
        st.subheader('Recommended best route is...', divider='rainbow')
        # st.divider()
        st.info(llm_response)
        st.divider()
        folium_static(map_html)
    
    #all legs are processed, so we know best route for each leg
    #final_map_html is not a full html, but a div element having map object
    # final_map_html = display_all_bestRoutes(routesData_list, TAG)
    # #This response will be returned by rest api
    # #leg_list has items having this structure {leg:integer, origin:string, destination:string, recommendation:string, map_html:divstring, map_all_html:divstring }
    # response = {
    #     "input": route_data,
    #     "llm_model_id": model_id,
    #     "output": leg_list,
    #     "final_output": final_map_html
    # }
    # #save response to file
    # file_name = f"ROUTE_{TAG}_restapi_response.json"
    # # save_file(response, file_name=file_name, file_type="json")

    return True 
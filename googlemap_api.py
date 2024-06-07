# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:52:19 2024

@author: ManojSingh
"""
import os
import requests
import googlemaps
import polyline
import pandas as pd
from file_save import save_file


def compute_routes(or_lat, or_lng, dt_lat, dt_lng):    
    """ inputs : api_key-->google maps api key
                 or_lat = origin place latitude 
                 or_lng = origin place longitude
                 dt_lat = destination place latitude
                 dt_lng = destination place langitude
                 
        output : gives routes information in json format.
    """
    
    base_url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': os.environ.get("GOOGLE_API_KEY"), 
        'X-Goog-FieldMask': 'routes.legs,routes.distanceMeters,routes.duration,routes.polyline.geoJsonLinestring'
    }

    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": or_lat,
                    "longitude": or_lng
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": dt_lat,
                    "longitude": dt_lng
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": True,
        "languageCode": "en-US",
    }

    response = requests.post(base_url, 
                             json=payload, 
                             headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
    

def extract_directions(data, origin, destination, gmaps):    
    """inputs: data = route api response in json format
               or_lat = origin place latitude 
               or_lng = origin place longitude
               gmaps = client instance
               
       output : df, decodedroutes_list                 
    """
    
    directions_list = []
    
    if data:        
        decoded_routes = {}
        for rtNo, route in enumerate(data.get('routes', [])):
            cum_dist = 0 
            cum_dur = 0
            
            # plot the route
            encoded_polyline = route['legs'][0]['polyline']['encodedPolyline']
            decoded_polyline = polyline.decode(encoded_polyline)
            latitude_list, longitude_list = zip(*decoded_polyline)

            decoded_routes[f"{rtNo}"] = decoded_polyline
            
            for idx, step in enumerate(route['legs'][0]['steps'], 1):
                if 'navigationInstruction' in step:
                    instruction = step['navigationInstruction']['instructions']
                    direction = step['navigationInstruction']['maneuver']
                    output_text = instruction.replace("\n", " - ")
                    # latitude and longitude values
                    latitude, longitude = step['startLocation']['latLng']['latitude'], step['startLocation']['latLng']['longitude']
                    # Get place name from lat&long values
                    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))

                    search_types = ['administrative_area_level_3',
                                    'administrative_area_level_2',
                                    'administrative_area_level_1',
                                    'country']
                    area = []
                    for tag in reverse_geocode_result[0]['address_components']:
                        if any(i in tag['types'] for i in search_types):
                            area.append(tag['long_name'])
                    areaName = ",".join(area)
                    
                    distance = int(step['distanceMeters'])
                    duration = step['staticDuration']
                    
                    duration = eval(duration.replace('s', ''))
                    
                    cum_dist = cum_dist + distance
                    cum_dur = cum_dur + duration
                        
                    row = [f"Route {rtNo}", f"{origin} to {destination}", direction, output_text, 
                               latitude, longitude, distance, duration, cum_dur, cum_dist, areaName]
                    directions_list.append(row)
         
        #store in dataframe
        df = pd.DataFrame(directions_list, columns=["Route No", 'Route', "Direction", "Route Instruction", 
                                                    "latitude", "longitude", "distance(m)", "duration(sec)", 
                                                    "cum_duration(sec)", "cum_distance(m)", "Area"])       

        return df, decoded_routes
    else:
        return None        
    
def get_routes(leg, origin, destination, TAG):
    """ inputs: Origin, Destination
        output: origin latitude and longitude
                destination latitude and longitude
                directions dataframe
                decoded_routes dictionary
    """

    gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_API_KEY"))
    
    # Get Origin geocodes
    geocode_result_org = gmaps.geocode(origin)
    location_data_org = geocode_result_org[0]['geometry']['location']
    org_lat, org_lng = location_data_org['lat'], location_data_org['lng']
    
    # Get destination geocodes
    geocode_result_dst = gmaps.geocode(destination)
    location_data_dst = geocode_result_dst[0]['geometry']['location']
    dst_lat, dst_lng = location_data_dst['lat'], location_data_dst['lng']
    
    # Call routes API
    routes_response = compute_routes(org_lat, org_lng, dst_lat, dst_lng)
    if routes_response == None:
        print("compute_routes returned None responce, check with API once.")
    else:
        # Extract the json response
        directions_df, decoded_routes = extract_directions(routes_response, origin, destination, gmaps)        
        save_file(directions_df, file_name = f"ROUTE_{TAG}_LEG{leg}_all_routes_directions.csv", file_type="csv")
                    
    routesData = {"leg": leg,
                  "origin": origin,
                  "destination": destination,
                  "org_lat":org_lat, 
                  "org_lng":org_lng, 
                  "dst_lat":dst_lat, 
                  "dst_lng":dst_lng, 
                  "directions_df":directions_df, 
                  "decoded_routes":decoded_routes}
    
    return routesData
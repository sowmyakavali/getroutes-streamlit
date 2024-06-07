# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 12:42:46 2024

@author: ManojSingh
"""

import os
import pandas as pd
import difflib
import folium
from file_save import save_file

from streamlit_folium import st_folium


#keep icon file info in a global variable datafarme
icon_folder = file_name = './icons_resource/'
conditions_df = pd.read_csv( os.path.join(icon_folder, 'weather_conditions.csv'))
cond_list = conditions_df['day'].tolist()


def get_icon_weatherapi(condition):
    close_matches = difflib.get_close_matches(condition, cond_list)
    if close_matches:
        matched_condition = close_matches[0]           
        icon_row = conditions_df.loc[conditions_df['day'] == matched_condition]        
        iconID = icon_row['icon'].iloc[0]     
        icon_url = os.path.join(icon_folder, str(iconID) + '.png') 
        return folium.features.CustomIcon(icon_url, icon_size=(40,40)) 
    else:
        return None 

    
#improve this further for more condition values
def get_icon_fontawesome(condition):
    icon_name = ""
    if condition.lower() in ['blizzard', 'snowfall', 'moderate or heavy snow showers', 'patchy moderate snow', 'light sleet']:
        icon_name = 'snowflake'
    elif condition.lower() in ['patchy rain nearby', 'moderate rain', 'heavy rain', 'light freezing rain' ]:
        icon_name = 'cloud-showers-heavy'
 
    if icon_name:
        return folium.Icon(color='lightgray', icon=icon_name, prefix='fa')
    else:
        return None


def add_weather_icons(map_plot, directions_df):
    for idx,row in directions_df.iterrows():
        condition = row['condition']
        #icon = get_icon_fontawesome(condition)
        icon = get_icon_weatherapi(condition)
        if icon:
            # Add a marker
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                icon=icon,
                popup=condition,
                fill_opacity=0.2,
                width='10%', 
                height='10%'
            ).add_to(map_plot)
        else:
            # Add Text marker
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                icon=folium.DivIcon(html=f"<div style='font-family: Arial; color: maroon; font-size: 15px;'><b>{condition}</b></div>")        
            ).add_to(map_plot)
        

def get_color(idx):
    vals =  ['blue', 'green', 'orange', 'purple', 'pink']  #0...4 index
    index = abs(idx)%len(vals)
    return vals[index]


def display_routes(routesData, origin, destination, TAG, routeNumber= None):
    org_lat = routesData['org_lat']
    org_lng = routesData['org_lng']
    dst_lat = routesData['dst_lat']
    dst_lng = routesData['dst_lng']
    decoded_routes = routesData['decoded_routes']
        
    # plot the routes on map
    map_plot = folium.Map(location=[org_lat, org_lng], zoom_start=3)

    #Add a drop marker
    folium.Marker(location=[org_lat, org_lng], popup=origin, icon=folium.Icon(color='blue')).add_to(map_plot)
    # Add a TEXT marker
    folium.Marker(
        location=[org_lat, org_lng],
        icon=folium.DivIcon(html="""<div style="font-family: Arial; color: maroon; font-size: 15px;"><b>Start</b></div>""")        
    ).add_to(map_plot)
    # Add a circle marker
    folium.CircleMarker(
        location=[org_lat, org_lng],
        radius=30,
        color='lightgray',
        fill=True,
        fill_color='teal',
        fill_opacity=0.4
    ).add_to(map_plot)


    #Add a drop marker
    folium.Marker(location=[dst_lat, dst_lng], popup=destination, icon=folium.Icon(color='red')).add_to(map_plot)    
    # Add a TEXT marker
    folium.Marker(
        location=[dst_lat, dst_lng],
        icon=folium.DivIcon(html="""<div style="font-family: Arial; color: maroon; font-size: 15px;"><b>End</b></div>""")        
    ).add_to(map_plot)
    # Add a circle marker
    folium.CircleMarker(
        location=[dst_lat, dst_lng],
        radius=30,
        color='lightgray',
        fill=True,
        fill_color='teal',
        fill_opacity=0.4
    ).add_to(map_plot)
    
    if routeNumber:
        routeValues = decoded_routes[routeNumber]
        folium.PolyLine(locations=routeValues, color=get_color(int(routeNumber)), weight=5, opacity=0.7).add_to(map_plot)           
        directions_df = routesData['directions_df'][routesData['directions_df']['Route No']=='Route ' + routeNumber]
        add_weather_icons(map_plot, directions_df)
        map_plot.fit_bounds(map_plot.get_bounds(), padding=(30, 30))     
        save_file(map_plot, file_name = f"ROUTE_{TAG}_LEG{routesData['leg']}_best_route.html", file_type="html")
    else:
        for routeNo, routeValues in decoded_routes.items():
            folium.PolyLine(locations=routeValues, color=get_color(int(routeNo)), weight=5, opacity=0.7).add_to(map_plot)
        add_weather_icons(map_plot, routesData['directions_df'])
        map_plot.fit_bounds(map_plot.get_bounds(), padding=(30, 30))
        save_file(map_plot, file_name = f"ROUTE_{TAG}_LEG{routesData['leg']}_all_routes.html", file_type="html")    
    
    
    #Get html div for display in iframe
    map_html = map_plot._repr_html_()
    
    # Return map_html variable
    return map_plot


# routesData has this structure, leg value starts from 1 {leg:integer, origin:string, destination:string, 
# org_lat:integer, org_lng:integer, dst_lat:integer, dst_lng:integer, directions_df:dataframe, decoded_routes:{1:list, 2:list},
# best_route:string, recommendation:string }
def display_all_bestRoutes(routesData_list, TAG):
    org_lat, org_lng = routesData_list[0]['org_lat'], routesData_list[0]['org_lng']
    map_plot = folium.Map(location=[org_lat, org_lng], zoom_start=3)
        
    for No, each_legData in enumerate(routesData_list):
        best_Route = each_legData['best_route']
        route_coords = each_legData['decoded_routes'][best_Route]
        direction_data = each_legData['directions_df']
        route_directions = direction_data[direction_data['Route No'] == f'Route {int(best_Route)}']

        org_lat, org_lng = each_legData['org_lat'], each_legData['org_lng']
        dst_lat, dst_lng = each_legData['dst_lat'], each_legData['dst_lng']
        origin, destination = each_legData['origin'], each_legData['destination']
        print(origin, "=====>", destination)

        #plot best route
        folium.PolyLine(locations=route_coords, color=get_color(No), weight=7, opacity=0.7).add_to(map_plot)
        #add weather icons for best route
        add_weather_icons(map_plot, route_directions)
        
        # Add a drop marker
        folium.Marker(location=[org_lat, org_lng], popup=origin, icon=folium.Icon(color='blue'), max_width=100).add_to(map_plot)
        # Add a TEXT marker
        folium.Marker(
            location=[org_lat, org_lng],
            icon=folium.DivIcon(html=f"""<div style="font-family: Arial; color: maroon; font-size: 15px;"><b>LEG:{each_legData['leg']}</b></div>""")
        ).add_to(map_plot)
        # Add a circle marker
        folium.CircleMarker(
            location=[org_lat, org_lng],
            radius=30,
            color='lightgray',
            fill=True,
            fill_color='teal',
            fill_opacity=0.4
        ).add_to(map_plot)

    #Since destination of previous leg is same as origin of current leg, the destination marker is outside the loop
    # Add a drop marker
    folium.Marker(location=[dst_lat, dst_lng], popup=destination, icon=folium.Icon(color='red'), max_width=100).add_to(map_plot)   
    # Add a TEXT marker
    folium.Marker(
        location=[dst_lat, dst_lng],
        icon=folium.DivIcon(html="""<div style="font-family: Arial; color: maroon; font-size: 15px;"><b>End</b></div>""")        
    ).add_to(map_plot)
    # Add a circle marker
    folium.CircleMarker(
        location=[dst_lat, dst_lng],
        radius=30,
        color='lightgray',
        fill=True,
        fill_color='teal',
        fill_opacity=0.4
    ).add_to(map_plot)

    map_plot.fit_bounds(map_plot.get_bounds(), padding=(30, 30))    
    save_file(map_plot, file_name = f"ROUTE_{TAG}_all_best_routes.html", file_type="html") 
    #Get html div for display in iframe
    final_html = map_plot._repr_html_()
    return final_html
import streamlit as st
import time
from route_optimization import *
from pytz import timezone 
from datetime import datetime
from streamlit_folium import st_folium

import streamlit.components.v1 as components

from streamlit_folium import folium_static


from dotenv import load_dotenv
load_dotenv()


start_location = "Leugenestrasse,Biel,Bern,Switzerland"
dest_location = "40 W. Switzerland,Lausanne,Switzerland"


with st.sidebar: 
    st.selectbox(
        "select your current location",
        ["Leugenestrasse,Biel,Bern,Switzerland", "40 W. Switzerland,Lausanne,Switzerland"]
    )

    st.selectbox(
        "select your next drop location",
        ["40 W. Switzerland,Lausanne,Switzerland", "Leugenestrasse,Biel,Bern,Switzerland"]
    )

    # st.button("Get routes")
col1, col2, col3 = st.columns([1,1,1])

# with col1:
#     st.sidebar.button('Yes')
# with col2:
#     st.sidebar.button('No')


# if st.sidebar.button('No'):
#     st.subheader("Sorry, I got wrong data.")
if st.sidebar.button("Get routes"):
    with st.spinner('**finding out the routes.....**'):
        # time.sleep(5) 

        payload = {
                "freight_order_number": "6100000501",
                "route_stops": [
                    {"stop": 1, "latitude": 0, "longitude": 0, "name": start_location},
                    {"stop": 2, "latitude": 0, "longitude": 0, "name": dest_location}
                                ]
                } 
        TAG = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%dT%H-%M-%S')

        
        data = process_route(payload, TAG)
    
 
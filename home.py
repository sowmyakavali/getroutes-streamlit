# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 11:47:18 2024

@author: ManojSingh
"""

import platform
from dotenv import load_dotenv
if platform.system() in ['Windows', 'Darwin']:
    print('Running on laptop')
    #Import your secrets from .env file
    load_dotenv()
else:
    print('Running on cloud')

import glob
import time
import json
from flask import Flask, request, render_template
from flask_cors import CORS
from pytz import timezone 
from datetime import datetime
from route_optimization import process_route
import traceback

#create application
app = Flask(__name__)
cors = CORS(app)


@app.route("/")
def hello_world():
    return '''<p><br>Access <b>'/demo'</b> to process a route.
<br>Access <b>'/mockup'</b> to see sample result.
<br><br>Make restapi call <b>'/processroutedata'</b> by passing JSON data with POST method.</p>'''


@app.route("/mockup")
def mockup():
    return render_template('index_mockup.html')


@app.route("/getmockupdata")
def getmockupdata():    
    time.sleep(5) #just to simulate processing time    
    #take latest output json file
    file_name = sorted(glob.glob('./sample_output/*.json'), reverse=True)[0]
    # Opening JSON file
    with open(file_name, 'r') as f: 
        # returns JSON object as 
        # a dictionary
        data = json.load(f)

    #set status
    data['ok'] = True
    data['message'] = 'Processed successfully'
    return data


@app.route("/demo")
def demo():
    return render_template('index_demo.html')


@app.route("/processroutedata", methods=['POST'])
def process_route_data():    
    try:
        #read input data fields in variable
        payload = request.get_json()    
        print("I received this number ==>", payload['freight_order_number']) 
        print("I received this json ==>", json.dumps(payload, indent=4)) 
            
        TAG = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%dT%H-%M-%S') #datetime.now().strftime('%d-%m-%yT%H-%M-%S')
        data = process_route(payload, TAG)
        #set status
        data['ok'] = True
        data['message'] = 'Processed successfully'
        return data, 200
    except Exception as err:
        print(f"process_route_data() failed with error message => {str(err)} => {traceback.format_exc()}")
        return {"ok": False, "message": f"{str(err)} ==> {traceback.format_exc()}"}, 200
        
    
if __name__ == '__main__':
    if platform.system() in ['Windows', 'Darwin']:
        print('Running on laptop')
        debug = True
    else:
        print('Running on cloud')
        debug = False
    #start flask server
    app.run(host='0.0.0.0', port=5000, debug=debug)  
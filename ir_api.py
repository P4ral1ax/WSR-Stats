# This is the file that will interact with the iRacing API and get the data
# It will operate similarly to the api_test file
# Author : Brayden Werner

import subprocess
import requests
import http.cookiejar
import json
import os
import csv


# Set our cookies so we are able to make iR API Calls
def set_cookies(session):
    jar = http.cookiejar.MozillaCookieJar("cookie-jar.txt") 
    jar.load()
    session.cookies = jar
    return


# iRacing API uses Temp Links, we need to get that new link
def get_real_link(session, link):
    response      = session.get(link)
    response_json = json.loads(response.text)
    new_link      = response_json["link"]
    return(new_link)


# Take a link or SID and return just the SID
def get_sid(URL):
    # Cut out Session ID
    if 'iracing.com' not in URL or 'http' not in URL:
        return URL
    if 'members-ng' in URL:
        subsession_str = URL[URL.rfind("subsession_id"):]
    else:
        subsession_str = URL[URL.rfind("subsessionid"):URL.rfind("&")]

    subsession_ID = subsession_str[subsession_str.rfind("=")+1:]
    return(subsession_ID)


# Download the Session Data
def download_get(link):
    # Create Session
    s = requests.Session()
    set_cookies(s)

    # Get new Link
    new_link = get_real_link(s, link)
    
    # Get JSON Data
    s2 = requests.session()
    raw_session_data = s2.get(new_link)
    return(raw_session_data.text)


# Download Lap Chart Data from iR API
def download_lap_chart(link):
    # Create Session
    s = requests.Session()
    set_cookies(s)

    # Get New Link
    new_link = get_real_link(s, link)

    # Get Real Data
    s2 = requests.session()
    lap_chart_file   = s2.get(new_link)
    lap_chart_object = json.loads(lap_chart_file.text)
    
    # Set JSON Objects
    chunk_info  = lap_chart_object['chunk_info']
    base_url    = chunk_info['base_download_url']
    files       = chunk_info['chunk_file_names'] 

    # Download each data chunk with the files iterating 0-N
    session_id = get_sid(link)
    counter = 0
    for file in files:
        f = open(f"data/{session_id}/lap_chart/{counter}.json", "w")
        data = s2.get(f"{base_url}{file}")
        f.write(data.text)
        f.close()
        counter += 1
        
    # Return the Original lap chart file text
    return(lap_chart_file.text)


# Takes the chunk files and writes them to a CSV for easier processing
def process_lap_chart(session_id):
    # Read in data about chunks
    f               = open(f"data/{session_id}/lap_chart/lap_chart.json", "r")
    data            = f.read()
    json_data       = json.loads(data)
    chunk_data      = json_data['chunk_info']
    chunks_count    = chunk_data['num_chunks']
    f.close()

    # Read all laps from chunk files into one big list of dicts
    laps = []
    for i in range(chunks_count):
        f_lap           = open(f"data/{session_id}/lap_chart/{i}.json", "r")
        lap_data        = f_lap.read()
        json_lap_data   = json.loads(lap_data)
        f_lap.close()
        
        for lap in json_lap_data:
            laps.append(lap)
        
    # Take all the laps from the list and add to phat CSV  
    f_csv = open(f"data/{session_id}/laps.csv", "w")
    csv_writer = csv.writer(f_csv)
    # (TODO) Write Fields

    # Write Laps
    for lap in laps:
        row = [lap['group_id'],lap['cust_id'],lap['name'],lap['lap_time'],lap['lap_number'],lap['lap_position']]
        csv_writer.writerow(row)
    
    f_csv.close()


# Create Data Directory and download session data + lap_chart data
def download_session(session_id):
    # Make Directory
    if os.path.isdir(f"data/{session_id}"):
        pass
    else:
        os.mkdir(f"data/{session_id}", mode = 0o755, dir_fd = None)

    # Download Get
    f        = open(f"data/{session_id}/get.json", "w")
    url      = generate_URL(session_id, "get")
    get_data = download_get(url)
    f.write(get_data)
    f.close()

    # Download Lap Chart
    f1  = open(f"data/{session_id}/lap_chart.json", "w")
    url = generate_URL(session_id, "lap_chart_data") 
    chart_info = download_lap_chart(url)
    f1.write(chart_info)
    f1.close()


# Throws Excpetion
# Generate an API URL to access data at
def generate_URL(session_id, call, session_num=0, cust_id=0, team_id=0):
    if call == "get":
        return(f"https://members-ng.iracing.com/data/results/get?subsession_id={session_id}")
    if call == "lap_chart_data":
        return(f"https://members-ng.iracing.com/data/results/lap_chart_data?subsession_id={session_id}&simsession_number={session_num}")
    if call == "driver":
        pass
    if call == "team":
        pass
    else:
        raise Exception("Unknown Call Type")



# "Main" Function
def get_session_laps():
    pass



### TODO ###

# Add Session Validation
# Make Cookie Stuff Better (Don't Update Cookie unless it is expired)
# Data Cleanup
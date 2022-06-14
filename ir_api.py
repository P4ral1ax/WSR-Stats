# This is the file that will interact with the iRacing API and get the data
# It will operate similarly to the api_test file
# Author : Brayden Werner

import requests
import http.cookiejar
import json
import os
import csv
import re
import subprocess

# Set our cookies so we are able to make iR API Calls
def set_cookies(session):
    jar = http.cookiejar.MozillaCookieJar("cookie-jar.txt") 
    jar.load()
    session.cookies = jar
    return


# If any of the cookies are expired return true
def cookies_expired():
    try:
        jar = http.cookiejar.MozillaCookieJar("cookie-jar.txt")
        jar.load()
        
        for cookie in jar:
            if cookie.name == "authtoken_members":
                return(False)
        return(True)
    
    except http.cookiejar.LoadError as e:
        return(True)
    except FileNotFoundError as e:
        return(True)

    
# iRacing API uses Temp Links, we need to get that new link
def get_real_link(session, link):
    response      = session.get(link)
    response_json = json.loads(response.text)
    new_link      = response_json["link"]
    return(new_link)


# Take a link or SID and return just the SID
def get_sid(URL):
    # Cut out Session ID
    if 'iracing.com' not in URL:
        return URL
    else:
        subsession_str = re.findall("subsession*.id=[0-9]+", URL)
        subsession_ID  = re.findall("[0-9]+",subsession_str[0])

    return(subsession_ID[0])


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
    f               = open(f"data/{session_id}/lap_chart.json", "r")
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
    
    # Write Fields
    key = [f'Group ID', 'Customer ID', 'Display Name', 'Laptime', 'Lap Number', 'Lap Position']
    csv_writer.writerow(key)

    # Write Laps
    for lap in laps:
        row = [lap['group_id'],lap['cust_id'],lap['display_name'],lap['lap_time'],lap['lap_number'],lap['lap_position']]
        csv_writer.writerow(row)
    
    f_csv.close()


# Create Data Directory and download session data + lap_chart data
def download_session(session_id):
    # Make Directory
    if os.path.isdir(f"data/{session_id}"):
        pass
    else:
        os.mkdir(f"data/{session_id}", mode = 0o755, dir_fd = None)

    if os.path.isdir(f"data/{session_id}/lap_chart"):
        pass
    else:
        os.mkdir(f"data/{session_id}/lap_chart", mode = 0o755, dir_fd = None)

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


def csv_to_json(csvFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath) as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    # Convert to json string
    # jsonString = json.dumps(jsonArray, indent=4)
    return(jsonArray)


# Clean up everything but the statistics + laps CSV files
# The CSVs are to be cached for better processing time
def file_cleanup_lapchart(sid):
    # Remove Lap Chart Data
    subprocess.call(["rm", "-r", f"data/{sid}/lap_chart"])
    subprocess.call(["rm", f"data/{sid}/lap_chart.json"])
    
    
# "Main" Function
def get_session_laps(link):
    # If Cookie Expired -> Update
    if cookies_expired():
        print("Updated Cookies")
        subprocess.run(["./get_cookie.sh"])
    
    # Get Session ID
    session_id = get_sid(link)

    # If File Not Cached, download new data
    if not(os.path.exists(f"data/{session_id}/laps.csv")):
        download_session(session_id)
        process_lap_chart(session_id)
        file_cleanup_lapchart(session_id)

    # Return Data in JSON form
    try:
        json = csv_to_json(f"data/{session_id}/laps.csv")
        return(json)
    except Exception as e:
        print(e)


def get_driver_laps(link, uid):
    # Check if laps are already cached (TODO)
    pass

def get_team_laps(link, gid):
    pass

def get_driver_name(uid):
    pass

def get_team_name(gid):
    pass

### TODO ###
# Add Session Validation
# Make DriverID/TeamID/Team Name/Driver Name/Class/Car LUT
# Implement Driver Laps
# Implement Team Laps
# Implement getting names
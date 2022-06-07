# Author : Brayden Werner
# Description : More complex test to try and support more API features and write CSV files for statistics
import subprocess
import requests
import http.cookiejar
import json
import os
import csv
import stats_test1
import re

# Get session ID from Link
# Please use regular expressions instead
def get_sid(URL):
    # Cut out Session ID
    if 'iracing.com' not in URL:
        return URL
    else:
        subsession_str = re.findall("subsession*.id=[0-9]+", URL)
        subsession_ID  = re.findall("[0-9]+",subsession_str[0])

    return(subsession_ID[0])


# Renew Session
def get_cookie():
    subprocess.run(["./get_cookie.sh"])


def set_cookies(session):
    jar = http.cookiejar.MozillaCookieJar("cookie-jar.txt") 
    jar.load()
    session.cookies = jar
    return


def get_real_link(session, link):
    response      = session.get(link)
    response_json = json.loads(response.text)
    new_link      = response_json["link"]
    return(new_link)


def generate_URL(session_id, call, session_num=0, cust_id=0, team_id=0):
    if call == "get":
        return(f"https://members-ng.iracing.com/data/results/get?subsession_id={session_id}")
    if call == "lap_chart_data":
        return(f"https://members-ng.iracing.com/data/results/lap_chart_data?subsession_id={session_id}&simsession_number={session_num}")
    if call == "lap_data":
        if cust_id != 0:
            return(f"https://members-ng.iracing.com/data/results/lap_data?subsession_id={session_id}&simsession_number={session_num}&cust_id={cust_id}")
        if team_id != 0:
            return(f"https://members-ng.iracing.com/data/results/lap_data?subsession_id={session_id}&simsession_number={session_num}&cust_id={team_id}")
        print("Error Generating URLs")
        exit(0)
    if call == "event_log":
        return(f"https://members-ng.iracing.com/data/results/event_log?subsession_id={session_id}&simsession_number={session_num}")
    if call == "driver":
        pass
    if call == "team":
        pass
    else:
        print("Unknown Call Type. Exiting")
        exit(0) 


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

    chunk_info  = lap_chart_object['chunk_info']
    base_url    = chunk_info['base_download_url']
    files       = chunk_info['chunk_file_names'] 

    session_id = get_sid(link)
    counter = 0
    for file in files:
        f = open(f"data/{session_id}/lap_chart/{counter}.json", "w+")
        data = s2.get(f"{base_url}{file}")
        f.write(data.text)
        f.close()
        counter += 1
        
    # Basically download all the files and stitch them together or write all the seperate files
    return(lap_chart_file.text)


def download_session_data(session_id):
    # Make Directories
    if os.path.isdir(f"data/{session_id}"):
        pass
    else:
        os.mkdir(f"data/{session_id}", mode = 0o755, dir_fd = None)

    if os.path.isdir(f"data/{session_id}/lap_chart"):
        pass
    else:
        os.mkdir(f"data/{session_id}/lap_chart", mode = 0o755, dir_fd = None)

    # Download Get
    f        = open(f"data/{session_id}/get.json", "w+")
    url      = generate_URL(session_id, "get")
    get_data = download_get(url)
    f.write(get_data)
    f.close()

    # Download Lap Chart
    f1  = open(f"data/{session_id}/lap_chart/lap_chart.json", "w+")
    url = generate_URL(session_id, "lap_chart_data") 
    chart_info = download_lap_chart(url)
    f1.write(chart_info)
    f1.close()


# Processes data in the Get json file. PLEASE refactor this code with more elegance
def process_get_data(session_id):
    f               = open(f"data/{session_id}/get.json", "r")
    data            = f.read()
    json_data       = json.loads(data)
    session_results = json_data['session_results']
    
    # Find Race Results Index (Refactor When you Aren't Stupid)
    index = 0
    for simsession in session_results:
        if simsession['simsession_number'] == 0:
            race_index = index
        index += 1

    race_subsession = session_results[race_index]
    race_results    = race_subsession['results']
        
    # Detect if Team or single Driver

    # If Single Driver Loop through drivers in Race and write CSV lines
    f_csv = open(f"data/{session_id}/drivers.csv", "w+")
    for driver in race_results:
        csv_writer = csv.writer(f_csv)
        
        # Write Fields (TODO)
        # ID, NAME, POSITION, START, IRATING, CAR 
        
        # Build Row String
        row = [driver['cust_id'],driver['display_name'],driver['finish_position'],driver['starting_position'],
            driver['newi_rating'],driver['best_lap_time'],driver['interval']]
        csv_writer.writerow(row)

    f_csv.close()
    f.close()
    

def process_lap_chart(session_id):
    # Read in data about chunks
    f               = open(f"data/{session_id}/lap_chart/lap_chart.json", "r")
    data            = f.read()
    json_data       = json.loads(data)
    chunk_data      = json_data['chunk_info']
    chunks_count    = chunk_data['num_chunks']
    f.close()

    # Read all laps from lists into one big list of dicts
    laps = []
    for i in range(chunks_count):
        f_lap           = open(f"data/{session_id}/lap_chart/{i}.json", "r")
        lap_data        = f_lap.read()
        json_lap_data   = json.loads(lap_data)
        f_lap.close()

        for lap in json_lap_data:
            laps.append(lap)
        
    # Take all the laps from the list and add of phat CSV    
    f_csv = open(f"data/{session_id}/laps.csv", "w")
    csv_writer = csv.writer(f_csv)
    # Write Fields

    # Write Laps
    for lap in laps:
        row = [lap['group_id'],lap['cust_id'],lap['name'],lap['lap_time'],lap['lap_number'],lap['lap_position']]
        csv_writer.writerow(row)
    
    f_csv.close()


def process_data(session_id):
    # Turn the JSON data into various CSV files
    # Process get Data
    # process_get_data(session_id)
    process_lap_chart(session_id)


def user_prompt():
    pass 



def main():
    # Reupdate Cookies
    subprocess.run(["./get_cookie.sh"])
    print("\n")

    event = input("Enter Session ID or Paste Result URL : ")
    session_id = get_sid(event)
    
    download_session_data(session_id)
    process_data(session_id)
    # Prompt to View / Download More data

if __name__ == "__main__":
    main()





## TODO ## (In Order)
# + Allow user input for Session ID or Link 
# - Output session ID data into labeled folder
# - Handle api/get
# - Handle api/lap_data
# - Handle api/lap_chart_data

# - Summarize data into CSV
# - Support Single Driver Events
# - Support Team Events
# - Automatically Download New Tokens if expired
# - Console Interface for Results
# - Connect to Front End
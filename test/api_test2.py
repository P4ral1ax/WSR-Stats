# Author : Brayden Werner
# Description : More complex test to try and support more API features and write CSV files for statistics
import subprocess
import requests
import http.cookiejar
import json
import os


# Get session ID from Link
def get_sid(URL):
    # Cut out Session ID
    if 'iracing.com' not in URL:
        return URL
    if 'members-ng' in URL:
        subsession_str = URL[URL.rfind("subsession_id"):]
    else:
        subsession_str = URL[URL.rfind("subsessionid"):URL.rfind("&")]

    subsession_ID = subsession_str[subsession_str.rfind("=")+1:]
    return(subsession_ID)


# Renew Session
def get_cookie():
    subprocess.run(["./get_cookie.sh"])


def set_cookies(session):
    jar = http.cookiejar.MozillaCookieJar("cookie-jar.txt") 
    jar.load()
    session.cookies = jar
    return


def get_real_link(session, link):
    response = session.get(link)
    response_json = json.loads(response.text)
    new_link = response_json["link"]
    return(new_link)


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
    lap_chart_file = s2.get(new_link)
    lap_chart_object = json.loads(lap_chart_file.text)

    chunk_info = lap_chart_object['chunk_info']
    base_url = chunk_info['base_download_url']
    files = chunk_info['chunk_file_names'] 

    big_data = ""
    for file in files:
        data = s2.get(f"{base_url}{file}")
        big_data += data.text
        
    # Basically download all the files and stitch them together

    return(lap_chart_file.text, big_data)


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
    else:
        print("Unknown Call Type. Exiting")
        exit(0) 


def download_session_data(session_id):
    # Make Directory
    if os.path.isdir(f"data/{session_id}"):
        pass
    else:
        os.mkdir(f"data/{session_id}", mode = 0o777, dir_fd = None)

    # Download Get
    f = open(f"data/{session_id}/get.json", "w")
    url = generate_URL(session_id, "get")
    get_data = download_get(url)
    f.write(get_data)
    f.close()

    # Download Lap Chart
    f1 = open(f"data/{session_id}/lap_chart.json", "w")
    f2 = open(f"data/{session_id}/lap_chart_data.json", "w")
    url = generate_URL(session_id, "lap_chart_data")
    chart_info, chart_data = download_lap_chart(url)
    f1.write(chart_info)
    f2.write(chart_data)
    f1.close()
    f2.close()


def process_data():
    pass


def download_driver_data(cust_id):
    pass


def user_prompt():
    pass




def main():
    # Reupdate Cookies
    # subprocess.run(["./get_cookie.sh"])
    print("\n")

    event = input("Enter Session ID or Paste Result URL : ")
    session_id = get_sid(event)
    
    download_session_data(session_id)
    # Process Data
    # Prompt to View

if __name__ == "__main__":
    main()





## TODO ## (In Order)
# - Allow user input for Session ID or Link 
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
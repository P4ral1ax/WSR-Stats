# Author : Brayden Werner
# Description : Just a simple iRacing API test using login creds from .env file

import os
import requests
import http.cookiejar
import json
import subprocess
from dotenv import load_dotenv

# Load in API credentials
load_dotenv()
EMAIL=os.getenv("email")
PASSWORD=os.getenv("password")
LOGIN="{\"email\": \"" + EMAIL + "\", \"password\": \"" + PASSWORD + "\"}"

# Get session ID from Link
def get_sid(URL):
    # Cut out Session ID
    if 'members-ng' in URL:
        subsession_str = URL[URL.rfind("subsession_id"):]
    else:
        subsession_str = URL[URL.rfind("subsessionid"):URL.rfind("&")]

    subsession_ID = subsession_str[subsession_str.rfind("=")+1:]
    return(subsession_ID)


# Convert a link in the normal format to one that can be used by the API
def convert_session_link(URL):
    ID = get_sid(URL)

    # Replace the Link
    API_link = f"https://members-ng.iracing.com/data/results/get?subsession_id={ID}"
    return(API_link)


# Reload Cookie Jar if Response is bad
def get_cookie():
    subprocess.run(["./get_cookie.sh"])


# Update Later to only pass in Session ID
def get_session_data(URL):
    converted_url = convert_session_link(URL)

    # Setup Connection 1
    s = requests.Session()
    jar = http.cookiejar.MozillaCookieJar("cookie-jar.txt")
    jar.load()
    s.cookies = jar
    
    # Get new Link
    response1 = s.get(converted_url)
    response1_json = json.loads(response1.text)
    new_url = response1_json["link"]

    # Get JSON Data
    s2 = requests.session()
    raw_session_data = s2.get(new_url)
    session_data = json.loads(raw_session_data.text)
    return(session_data, raw_session_data.text)



def main():
    # get_cookie()
    file1 = open("test_file.txt", "w")
    results, results_raw = get_session_data("https://members-ng.iracing.com/data/results/get?subsession_id=45954692")
    file1.write(results_raw)
    file1.close()


if __name__ == "__main__":
    main()
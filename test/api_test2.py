# Author : Brayden Werner
# Description : More complex test to try and support more API features and write CSV files for statistics
import subprocess


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


def main():
    pass

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
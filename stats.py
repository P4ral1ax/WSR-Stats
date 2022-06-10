# This will be where the functions for doing statistics will be
import csv
import os
import ir_api as ir

def load_driver_laps(id):
    f = open(f"data/{id}/laps.csv", 'r')
    csv_reader = csv.reader(f)
    driver_lap_dict = {}

    # Load in laps to driver dictionary (Ignore -1 laps)
    for lap in csv_reader:
        print(lap[1])
        if lap[0] != "Group ID": 
            if lap[3] != "-1":
                if lap[1] in driver_lap_dict:
                    driver_lap_dict[lap[1]].append(int(lap[3]))
                else:
                    driver_lap_dict[lap[1]] = [int(lap[3])]            

    # Sort laps for each driver from slow to fast
    for driver in driver_lap_dict:
        driver_lap_dict[driver].sort()

    return(driver_lap_dict)


# Add Error Checking
def generate_stats(lap_dict, session_id, top_lap=20):
    # Open Stats file
    f = open(f"data/{session_id}/stats.csv", 'w')
    csv_writer = csv.writer(f)

    # Write Key
    key = ['Driver ID', 'Fastest Lap', f'Top {top_lap} Laps', 'Top 50%', 'Median', 'Laps']
    csv_writer.writerow(key)


    for driver in lap_dict:
        try:
            temp_total=0
            list = lap_dict[driver]

            # Generate Median
            median_index = (len(list) // 2) - 1 
            median       = list[median_index]
            
            # Calculate Top 50%
            for i in range(0, median_index+1):
                temp_total += list[i]        
            top_50 = temp_total // (median_index + 1)

            # Top Laps
            temp_total = 0
            if top_lap > len(list):
                top_laps = "invalid"
            else:
                for i in range(0, top_lap):
                    temp_total += list[i]
                top_laps = temp_total // top_lap

            # Fastest Lap
            fast_lap = list[0]

            # Total Laps
            total = len(list)

            # Write to CSV
            row = [driver, fast_lap, top_laps, top_50, median, total]
            csv_writer.writerow(row)
        except Exception as e:
            row = [driver, "invalid", "invalid" ,"invalid", "invalid", len(list)]


def get_stats(session_id, top_laps=20):
    # Check if Laps already downloaded
    if not(os.path.exists(f"data/{session_id}/laps.csv")):
        ir.get_session_laps(session_id)
    
    lap_dict = load_driver_laps(session_id)    
    generate_stats(lap_dict, session_id, top_laps)

    # Return as JSON
    try:
        json = ir.csv_to_json(f"data/{session_id}/stats.csv")
        return(json)
    except Exception as e:
        print(e)


        

### TODO ###
# Do more team based Statistics
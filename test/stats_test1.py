# Author : Brayden Werner
# Description : First test to parse the CSV output of a specific subsession ID

# Idea : Load in all laps for each driver ID. Append laptimes to a list for each driver ID. so basically {123456 : [123.456, 123.567, 123.678]}. Sort Laps if possible.
# Use this dictionary to do all the stats. Maybe make a seperate dictionary for team stats by team ID and the same thing. 
# For displaying the actual name maybe make a LUT using yet another dictionary.
# I Loooooooooooooooooove Dictionaries

import csv

driver_lap_dict = {}
team_lap_dict   = {}


def load_driver_laps(id):
    f = open(f"data/{id}/laps.csv", 'r')
    csv_reader = csv.reader(f)

    # Load in laps to driver dictionary (Ignore -1 laps)
    for lap in csv_reader:
        if lap[4] != '-1':
            if lap[0] in driver_lap_dict:
                driver_lap_dict[lap[0]].append(int(lap[4]))
            else:
                driver_lap_dict[lap[0]] = [int(lap[4])]            

    # Sort laps for each driver from slow to fast
    for driver in driver_lap_dict:
        driver_lap_dict[driver].sort()

    return(driver_lap_dict)


# Do this reguardless of if team session or not. Just makes everything easier.
def load_team_laps():
    pass

def generate_stats(lap_dict, session_id, top_lap=5):
    # Open Stats file
    f = open(f"data/{session_id}/basic_stats.csv", 'w')
    csv_writer = csv.writer(f)

    # Write Key
    key = ['Driver', 'Fastest Lap', f'Top {top_lap} Laps', 'Top 50%', 'Median', 'Laps']
    csv_writer.writerow(key)


    for driver in lap_dict:
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
    


def main():
    session_id = input("Enter Session ID : ")
    lap_dict = load_driver_laps(session_id)
    generate_stats(lap_dict, session_id)


if __name__ == "__main__":
    main()
# Try and Make an easy to parse LUT for Driver ID -> Driver Name, Team ID. Team Name, Class, Car
# Or try and find a way to parse the get very quickly

import json

# Use a LUT File
def lookup_id_method1(driverID):
    pass

# Using the get.json File
def lookup_id_method2(driverID, sid):
    f = open(f"data/{sid}/get.json")
    data = json.load(f)
    print(data)


def main():
    session_id = input("Enter Session ID : ")
    driver_id = input("Enter Driver ID : ")
    lookup_id_method2(driver_id, session_id)

main()
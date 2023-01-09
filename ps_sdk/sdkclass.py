# Main Class for Cars
class Car:
    def __init__(self, id, driver, dist, time, laps):
        self.id = id
        self.driver = driver
        self.last_dist = dist
        self.last_time = time
        self.last_laps = laps

    def tick_update(self, driver, dist, time, laps):
        self.driver = driver
        self.last_dist = dist
        self.last_time = time
        self.last_laps = laps

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1
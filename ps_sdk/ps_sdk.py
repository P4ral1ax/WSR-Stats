import irsdk
import time
import sdkclass


# To reverse other products wireshark capture on http://127.0.0.1:32034/ 

SESSIONID = 0


def calc_distance(dist):
    pass

def calc_speed(dist1, dist2, time1, time2):
    pass


# here we check if we are connected to iracing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.last_car_setup_tick = -1
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')

# our main loop, where we retrieve data
def loop():
    # on each tick we freeze buffer with live telemetry
    # this way you will have consistent data from those vars inside one tick
    ir.freeze_var_buffer_latest()

    # retrieve live telemetry data
    t = ir['SessionTime']
    print('session time:', t)


if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = sdkclass.State()

    try:
        # infinite loop
        while True:
            check_iracing()
            if state.ir_connected:
                loop()
            time.sleep(0.25) # Refresh Rate
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass
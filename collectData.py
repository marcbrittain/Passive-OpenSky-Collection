from opensky_api import OpenSkyApi
import time
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--username", help="OpenSky Username")
parser.add_argument("--password", help="OpenSky Password")
parser.add_argument('--bbox', nargs='+', type=float)
args = parser.parse_args()


BBOX = tuple(args.bbox)
USERNAME = args.username
PASSWORD = args.password

# collecting lat/lon data
latitudes = []
longitudes = []
alt = []
heading = []
icao24 = []
velocity = []
vertical_rate = []

# hour represents the hour since the python script began, not the
# hour of the day
hour = 0

# counting the number of states collecting
counter = 0

while True:
    start = time.time()
    api = OpenSkyApi(username=USERNAME,password=PASSWORD)

    try:
        states = api.get_states(time_secs=time.time(),bbox=BBOX)
    except:
        ##OpenSky data is updated every 5 seconds so sleep for 5
        time.sleep(5)
        continue


    # collecting lat/lon data
    try:

        for s in states.states:
            latitudes.append(s.latitude)
            longitudes.append(s.longitude)
            alt.append(s.geo_altitude)
            heading.append(s.heading)
            icao24.append(s.icao24)
            velocity.append(s.velocity)
            vertical_rate.append(s.vertical_rate)



    # this will occur if there is no data in states
    except:
        timeinfo = time.gmtime()

        day = timeinfo.tm_mday
        month = timeinfo.tm_mon
        year = timeinfo.tm_year
        hr = timeinfo.tm_hour
        minute = timeinfo.tm_min
        sec = timeinfo.tm_sec

        print("Error collecting data for {}/{}/{}/{}:{}".format(year,month,day,hr,minute,sec))
        end = time.time()

        if not abs(end-start) > 5:
            time.sleep(5-abs(end-start))
        continue



    end = time.time()

    # We only want to collect data at most every 5 seconds
    if not abs(end-start) > 5:
        time.sleep(5-abs(end-start))

    counter += 1


    ## ~ 1 hour worth of data: 3600 seconds / 5 seconds data collection
    ## This could be updated based on the start time.time() and the current time.time()
    ## to make this exactly 1 hour instead of ~ 1 hour
    if counter == 720:


        timeinfo = time.gmtime()

        day = timeinfo.tm_mday
        month = timeinfo.tm_mon
        year = timeinfo.tm_year
        hr = timeinfo.tm_hour
        minute = timeinfo.tm_min
        sec = timeinfo.tm_sec

        # convert data to a matrix of (N, 2)
        latlon = np.vstack([latitudes,longitudes,alt,heading,icao24,velocity,vertical_rate]).T
        latitudes = []
        longitudes = []
        alt = []
        heading = []
        icao24 = []
        velocity = []
        vertical_rate = []

        # save data
        os.makedirs("data/{}/{}/{}/".format(year,month,day),exist_ok=True)

        if not os.path.isfile('data/{}/{}/{}/{}.npy'.format(year,month,day,hr)):
            np.savez_compressed('data/{}/{}/{}/{}.npz'.format(year,month,day,hr),data=latlon)

        else:
            np.savez_compressed('data/{}/{}/{}/{}_{}.npz'.format(year,month,day,hr,minute),data=latlon)

        hour += 1
        counter = 0

        print("Hours Processed: {}".format(hour))

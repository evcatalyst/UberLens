import time
from hexmath import generate_hexgrid
from datetime import datetime
from UberWrapper import UberWrapper
from GMapsWrapper import GMapsWrapper
# from drawing import drawMapWithGradient
import sys
import json


if __name__ == '__main__':

    # print sys.argv
    # sys.exit()
    # POIs in Puget Sound
    msft_seattle = '320 Westlake Ave N, Seattle, WA 98109'
    msft_studioG = '3950 148th Ave NE, Redmond, WA 98052'
    studio_D = '15030 NE 36th St, Redmond, WA 98052'
    center_seattle = '832 16th Ave, Seattle, WA 98122'
    molly_moons = '917 E Pine St, Seattle, WA 98122'
    msft_bellevue = '205 108th Ave NE, Bellevue, WA 98004'
    msft_redmond = '15010 Northeast 36th Street, Redmond, WA 98052'
    larkspur = '15805 SE 37th St, Bellevue, WA 98006'

    # # # # # USER INPUTS # # # # #
    origin_of_travel = studio_D #''
    destination = center_seattle#''
    APIKEY = ''
    print sys.argv
    if len(sys.argv) == 4:
        APIKEY = sys.argv[1]
        origin_of_travel = sys.argv[2] #studio_D
        destination = sys.argv[3] #center_seattle
    elif len(sys.argv) == 3:
        origin_of_travel = sys.argv[1] #studio_D
        destination = sys.argv[2] #center_seattle
    num_shells = 2 # a_n = 3n^2 - 3n + 1 (careful lol): 1, 7, 19, 37, 61, ...
    major = 200     # 200 suggested
    # # # # # # # # # # # # # # # #

    # Initialize wrappers
    Uber = UberWrapper()
    GMaps = GMapsWrapper(sys.argv[1])



    # Get origin lat,lng and Google place ID (for Uber API)
    origin_latlng = GMaps.get_latlng_from_address(origin_of_travel)
    origin_placeID = GMaps.get_placeID_from_latlng(origin_latlng)

    # print "\nOrigin:\t\t", origin_of_travel
    # print "Destination:\t", destination
    # print origin_of_travel
    # print destination
    OUTPUT = {}
    OUTPUT['origin_of_travel'] = origin_of_travel
    OUTPUT['destination'] = destination
    
    # Generate hexgrid for target area of destination
    dest_latlng = GMaps.get_latlng_from_address(destination)
    hexgrid = generate_hexgrid(list(dest_latlng), num_shells, major)

    num_hexs = len(hexgrid)
    # print "\n%d points generated\n" % (num_hexs)
    # print "Estimating fares to every point in destination area..."

    fares = []
    counter = 1
    for centroid in hexgrid:
        if GMaps.isWater(centroid):
            continue

        # TODO: MULTITHREAD THIS?
        proximity_dest_placeID = GMaps.get_placeID_from_latlng(centroid)
        fares_response = Uber.fare_estimator(origin_placeID, proximity_dest_placeID)
        if 'estimatesHasError' in fares_response.keys():
            # print 'ERROR, TRYING AGAIN'
            fares_response = Uber.fare_estimator(origin_placeID, proximity_dest_placeID)

        fare_string = Uber.get_UberX_from_fares(fares_response)

        fare_range = [ float(x) for x in fare_string[1:].split('-') ]
        fare = sum(fare_range) / len(fare_range)
        fares.append([fare, centroid[0], centroid[1]])

        # print "[%d/%d]:\t$%f" % (counter, num_hexs, fare)
        # hex_output = [proximity_dest_placeID, fare]
        print "%s # %d" % (GMaps.get_address_from_latlng(centroid), fare)
        OUTPUT[GMaps.get_address_from_latlng(centroid)] = fare
        counter += 1
        # time.sleep(1)
        # sys.exit()

    # OUTPUT = json.dumps(OUTPUT)
    print OUTPUT
    sys.exit()
    drawMapWithGradient(fares, list(origin_latlng), list(dest_latlng), 14)

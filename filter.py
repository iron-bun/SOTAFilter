#!/usr/bin/env python3
"""
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import csv

distance_filter = 0.13

def read_stops(stop_file):

    min_lat, max_lat, min_long, max_long = None, None, None, None
    stops = dict()
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")
        
    for stop in stop_reader:
        if stop["Latitude"] == "":
            continue

        lat = float(stop["Latitude"])
        if min_lat == None or lat < min_lat:
            min_lat = lat
        if max_lat == None or lat > max_lat:
            max_lat = lat
        lon = float(stop["Longitude"])
        if min_long == None or lon < min_long:
            min_long = lon
        if max_long == None or lon > max_long:
            max_long = lon

        lat = int(lat // distance_filter)
        lon = int(lon // distance_filter)
        if lat not in stops:
            stops[lat] = dict()
        if lon not in stops[lat]:
            stops[lat][lon] = []
        stops[lat][lon].append((stop["ATCOCode"], stop["CommonName"], float(stop["Latitude"]), float(stop["Longitude"])))

    return min_lat, max_lat, min_long, max_long, stops


def main():
    with open("Stops.csv") as stop_file:
        min_lat, max_lat, min_long, max_long, stops = read_stops(stop_file)

    with open("summitslist.csv", newline="") as summits_file:
        summits_file.readline()
        summit_reader = csv.DictReader(summits_file, delimiter=",", quotechar="\"")

        for summit in summit_reader:
            if float(summit["Latitude"]) < min_lat - 1 or float(summit["Latitude"]) > max_lat + 1 or float(summit["Longitude"]) < min_long - 1 or float(summit["Longitude"]) > max_long + 1:
                continue

            lat,lon = int(float(summit["Latitude"]) // distance_filter), int(float(summit["Longitude"]) // distance_filter)
            for i in range(lat-1, lat+2):
                for j in range(lon-1, lon+2):
                    if i in stops and j in stops[i]:
                        for stop in stops[i][j]:
                            dist = (stop[2] - float(summit["Latitude"]))**2 + (stop[3] - float(summit["Longitude"]))**2
                            dist **= 0.5
                            if dist <= distance_filter:
                                print(summit["SummitCode"], stop, dist)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2023 Chris Sinclair

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
import argparse
import json
import sys
from collections import defaultdict
from math import cos, asin, radians, degrees, atan2, pi
import logging
import bng_latlon

bucket_distance = 0.08
walking_distance = 5 #km

log = logging.getLogger(__name__)
logging.basicConfig()

def hav(theta):
    theta = radians(theta)
    return (1-cos(theta))/2

def hdist(lat1, lon1, lat2, lon2):

    earth_radius = 6371 #km
    dy = lat1 - lat2
    dx = lon1 - lon2
    
    h = hav(dy) + cos(radians(lat1)) * cos(radians(lat2)) * hav(dx)
    return 2*earth_radius*asin(h**0.5)

def hangle(lat1, lon1, lat2, lon2):
    dy = lat1 - lat2
    dx = lon1 - lon2

    angle = atan2(dy, cos(pi/180*lat1)*dx)
    return degrees(angle)

def read_gb_ni_stops(stop_file,has_status,global_id):

    stops = defaultdict(list)
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")

    for stop in stop_reader:
        if has_status and stop["Status"] == "inactive":
            log.debug(f"Stop {stop['CommonName']} ({stop[global_id]}) omitted because it is inactive")
            continue

        if stop["Latitude"] == "" or stop["Longitude"] == "":
            lat,lon = bng_latlon.OSGB36toWGS84(int(stop['Easting']), int(stop['Northing']))
            log.debug(f"Converted {stop['CommonName']} ({stop[global_id]}) from grid NT {stop['Northing']} {stop['Easting']} to {lat},{lon}")
        else:
            lat = float(stop["Latitude"])
            lon = float(stop["Longitude"])

        b_lat = round(lat / bucket_distance)
        b_lon = round(lon / bucket_distance)

        stops[b_lat, b_lon].append({"id":stop[global_id], "name":stop["CommonName"], "lat":lat, "lon":lon})

    return stops

def read_gb_stops(stop_file):
    return read_gb_ni_stops(stop_file, True, "ATCOCode")

def read_ni_stops(stop_file):
    return read_gb_ni_stops(stop_file, False, "AtcoCode")

def read_ie_stops(stop_file):

    stop_reader = json.load(stop_file)
    stops = defaultdict(list)

    for stop in stop_reader["features"]:
        if "isActive" in stop["properties"] and not stop["properties"]["isActive"]:
            continue

        lat = round(stop["geometry"]["coordinates"][1] / bucket_distance)
        lon = round(stop["geometry"]["coordinates"][0] / bucket_distance)

        stops[lat, lon].append({"id":stop["properties"]["AtcoCode"], "name":stop["properties"]["CommonName"], "lat":float(stop["geometry"]["coordinates"][1]), "lon":float(stop["geometry"]["coordinates"][0])})

    return stops

def read_no_stops(stop_file):

    stops = defaultdict(list)
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")

    for stop in stop_reader:

        lat = float(stop["stop_lat"])
        lon = float(stop["stop_lon"])

        b_lat = round(lat / bucket_distance)
        b_lon = round(lon / bucket_distance)

        stops[b_lat, b_lon].append({"id":stop["stop_id"], "name":stop["stop_name"], "lat":lat, "lon":lon})

    return stops


stops_parsers = {'gb':read_gb_stops, 'ni':read_ni_stops, 'ie':read_ie_stops, 'no':read_no_stops}

def print_csv_results(stations, args):

    print("SummitCode, SummitLatitude, SummitLongitude, StationCode, StationName, StationLatitude, StationLongitude")
    for summit, data in stations.items():
        stops = sorted(data["stops"], key=lambda x:x[0])
        for stop in stops:
            print(f"{summit}, {data['lat']}, {data['lon']}, {stop[1]['id']}, {stop[1]['name']}, {stop[1]['lat']}, {stop[1]['lon']}")

def print_json_results(stations, args):
    results = []
 
    for summit in stations:
        tmp = {"id": summit, "name": stations[summit]["name"], "coordinates":[stations[summit]["lat"], stations[summit]["lon"]], "stops":[]}

        angles = defaultdict(list)
        for stop in stations[summit]["stops"]:
            dist = stop[0]
            stop = stop[1]

            angle = hangle(stations[summit]["lat"], stations[summit]["lon"], stop["lat"], stop["lon"])/10
            angle = round(angle)

            angles[angle].append((dist, {"name": stop["name"], "coordinates":[stop["lat"], stop["lon"]]}))

        for k, v in angles.items():
            v = sorted(v, key=lambda x:x[0])
            tmp["stops"].append(v[0][1])
        results.append(tmp)

    print(json.dumps(results))
    
results_printers = {'csv':print_csv_results, 'json':print_json_results}

def main(args):

    stops = stops_parsers[args.stop_file_type](args.stop_file)

    args.summit_file.readline()
    summit_reader = csv.DictReader(args.summit_file, delimiter=",", quotechar="\"")

    stations = dict()

    for summit in summit_reader:
        summit_code = summit["SummitCode"]
        region_code = summit_code[:summit_code.find("/")]
        if region_code != args.region:
            continue

        lat,lon = float(summit["Latitude"]), float(summit["Longitude"])

        b_lat, b_lon = round(lat/bucket_distance), round(lon/bucket_distance)

        for i in range(b_lat-1, b_lat+2):
            for j in range(b_lon-1, b_lon+2):
                if (i, j) in stops:
                    for stop in stops[i, j]:

                        dist = hdist(lat, lon, stop["lat"], stop["lon"])

                        if dist <= walking_distance:
                            if summit["SummitCode"] not in stations:
                                stations[summit["SummitCode"]] = {"name": summit["SummitName"], "lat":lat, "lon":lon, "stops":[]}
                            stations[summit["SummitCode"]]["stops"].append((dist, stop))
    results_printers[args.f](stations, args)

def get_arguments():
    parser = argparse.ArgumentParser(
                    prog = "SOTAfilter.py",
                    description = "Return a list of SOTA summits near public transport sites ordered by distance to the user",
                    epilog = "Text at the bottom of help")

    parser.add_argument("stop_file_type", choices=["gb","ni","ie","no"], help="gb for Great Britain. ni for Northern Ireland. ie for Republic of Ireland")
    parser.add_argument("stop_file", type=argparse.FileType("r", encoding="latin-1"))
    parser.add_argument("summit_file", type=argparse.FileType("r", encoding="latin-1"))
    parser.add_argument("region")
    parser.add_argument("-f", choices=["json", "csv"], default="csv", help="Output format. Either csv or geoJSON")
    parser.add_argument("-v", default=0, action="count", help="Print debug statements. Omit for no debug. -v for info. -vv for debug")

    args = parser.parse_args()

    log.setLevel(logging.WARNING - 10 * args.v)

    return args


if __name__ == "__main__":
    args = get_arguments()
    main(args)


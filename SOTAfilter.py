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
import json_stream
import sys
from collections import defaultdict
from math import cos, asin, radians, degrees, atan2, pi
import logging
import bng_latlon
from datetime import date

bucket_distance = 0.08
walking_distance = 5 #km
cycling_distance = 10
cycling_stop_types = ['RSE','RLY','RPL']

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

def read_gb_ni_stops(stop_file,summits, merge_stop, has_status, global_id):

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

        stop_id = stop[global_id]
        stop_name = stop["CommonName"]
        stop_type = stop["StopType"]

        merge_stop(summits, {"id":stop_id, "name":stop_name, "StopType": stop_type, "lat":lat, "lon":lon})

def read_gb_stops(stop_file, summits, merge_stop):
    return read_gb_ni_stops(stop_file, summits, merge_stop, True, "ATCOCode")

def read_ni_stops(stop_file, summits, merge_stop):
    return read_gb_ni_stops(stop_file, summits, merge_stop, False, "AtcoCode")

def read_ie_stops(stop_file, summits, merge_stop):

    stop_reader = json.load(stop_file)
    stops = defaultdict(list)

    for stop in stop_reader["features"]:
        if "isActive" in stop["properties"] and not stop["properties"]["isActive"]:
            continue

        lat = round(stop["geometry"]["coordinates"][1] / bucket_distance)
        lon = round(stop["geometry"]["coordinates"][0] / bucket_distance)
        stop_type = stop["properties"]["StopType"]

        merge_stop(summits, {"id":stop["properties"]["AtcoCode"], "name":stop["properties"]["CommonName"], "StopType": stop_type, "lat":float(stop["geometry"]["coordinates"][1]), "lon":float(stop["geometry"]["coordinates"][0])})

def read_de_no_stops(stop_file, summits, merge_stop):

    stops = defaultdict(list)
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")

    for stop in stop_reader:

        lat = float(stop["stop_lat"])
        lon = float(stop["stop_lon"])

        b_lat = round(lat / bucket_distance)
        b_lon = round(lon / bucket_distance)

        merge_stop(summits, {"id":stop["stop_id"], "name":stop["stop_name"], "lat":lat, "lon":lon})

def read_je_stops(stop_file, summits, merge_stop):

    stops = defaultdict(list)
    stop_reader = json.load(stop_file)

    for stop in stop_reader["stops"]:
        lat = float(stop["Latitude"])
        lon = float(stop["Longitude"])

        b_lat = round(lat / bucket_distance)
        b_lon = round(lon / bucket_distance)

        merge_stop(summits, {"id":stop["StopNumber"], "name":stop["StopName"], "lat":lat, "lon":lon})

def read_im_stops(stop_file, summits, merge_stop):
    stops = defaultdict(list)
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")

    for stop in stop_reader:

        lat = float(stop["Latitude"].replace(',','.'))
        lon = float(stop["Longitude"].replace(',','.'))
        stop_type = stop["StopType"]

        merge_stop(summits, {"id":stop["Stop No"], "name":stop["Location"], "StopType": stop_type, "lat":lat, "lon":lon})

def read_fr_stops(stop_file, summits, merge_stop):
    stops = defaultdict(list)
    stop_reader = json_stream.load(stop_file)

    for stop in stop_reader["features"]:
        properties = stop["properties"]
        stop_id = properties["id"]
        stop_name = properties["name"]
        geometry = stop["geometry"]
        if geometry == None:
            continue
        lat, lon = geometry["coordinates"]
        lat, lon = float(lat), float(lon)

        merge_stop(summits, {"id":stop_id, "name":stop_name, "lat":lat, "lon":lon})

stops_parsers = {'gb':read_gb_stops, 'ni':read_ni_stops, 'ie':read_ie_stops, 'no':read_de_no_stops, 'de':read_de_no_stops, 'je':read_je_stops, 'im':read_im_stops, 'fr':read_fr_stops}

def print_csv_results(summit_squares, args):

    print("SummitCode, SummitLatitude, SummitLongitude, StationCode, StationName, StationLatitude, StationLongitude")
    for k, summits in summit_squares.items():
        for summit in summits:
            for angle, (distance, stop) in summit["walking_stops"].items():
                print(f"{summit['summit_code']}, {summit['lat']}, {summit['lon']}, {summit['points']}, {stop['id']}, {stop['name']}, {stop['lat']}, {stop['lon']}, {distance}")
            for angle, (distance, stop) in summit["cycling_stops"].items():
                print(f"{summit['summit_code']}, {summit['lat']}, {summit['lon']}, {summit['points']}, {stop['id']}, {stop['name']}, {stop['lat']}, {stop['lon']}, {distance}")

def print_json_results(summit_squares, args):
    results = []
 
    for k, summits in summit_squares.items():
        for summit in summits:
            if len(summit["cycling_stops"]) + len(summit["walking_stops"]) == 0:
                pass
                continue

            tmp = dict()
            tmp["id"] = summit["summit_code"]
            tmp["name"] = summit["name"]
            tmp["points"] = summit["points"]
            tmp["coordinates"] = [summit["lat"], summit["lon"]]
            tmp["stops"] = []

            for angle, (dist, stop) in summit["cycling_stops"].items():
                tmp["stops"].append({"id": stop["id"], "name": stop["name"], "coordinates":[stop["lat"], stop["lon"]]})
            for angle, (dist, stop) in summit["walking_stops"].items():
                tmp["stops"].append({"id": stop["id"], "name": stop["name"], "coordinates":[stop["lat"], stop["lon"]]})

            results.append(tmp)

    print(json.dumps(results))
    
results_printers = {'csv':print_csv_results, 'json':print_json_results}

def read_summits(summit_file):
    summit_file.readline()
    summit_reader = csv.DictReader(summit_file, delimiter=",", quotechar="\"")

    summit_squares = defaultdict(list)

    for summit in summit_reader:
        summit_code = summit["SummitCode"]
        region_code = summit_code[:summit_code.find("/")]
        if region_code != args.region:
            log.debug(f"discarding {summit['SummitCode']} as not in selected region ({args.region})")
            continue

        day, month, year = list(map(int, summit["ValidTo"].split("/")))
        if date(year, month, day) < date.today():
            log.info(f"discarding {summit['SummitCode']} as no longer valid ({summit['ValidTo']})")
            continue

        lat,lon = float(summit["Latitude"]), float(summit["Longitude"])
        b_lat, b_lon = round(lat/bucket_distance), round(lon/bucket_distance)

        points = summit["Points"]

        summit_squares[(b_lat, b_lon)].append({"summit_code":summit_code, "name": summit["SummitName"], "points":points, "lat":lat, "lon":lon, "cycling_stops":{}, "walking_stops":{}})

    log.info(f"loaded {len(summit_squares)} squares of data")
    return summit_squares

def merge_stations(summits, stop):

    b_lat = round(stop["lat"]/bucket_distance)
    b_lon = round(stop["lon"]/bucket_distance)

    if "StopType" in stop:
        stop_type = stop["StopType"]
    else:
        stop_type = ""

    if stop_type in cycling_stop_types:
        filter_distance = cycling_distance
    else:
        filter_distance = walking_distance

    for i in range(b_lat-2, b_lat+3):
        for j in range(b_lon-2, b_lon+3):
            for summit in summits[(i, j)]:
                log.info(f"testing summit {summit} against stop {stop}")

                dist = hdist(summit["lat"], summit["lon"], stop["lat"], stop["lon"])
                if dist > filter_distance:
                    continue

                if stop_type in cycling_stop_types:
                    stops = summit["cycling_stops"]
                else:
                    stops = summit["walking_stops"]

                angle = hangle(summit["lat"], summit["lon"], stop["lat"], stop["lon"])
                angle = round(angle/10)
                if angle not in stops:
                    stops[angle] = (dist, stop)
                elif dist < stops[angle][0]:
                    stops[angle] = (dist, stop)

def main(args):

    summit_file = open(args.summit_file, "r", encoding=args.e)
    summits = read_summits(summit_file)

    stop_file = open(args.stop_file, "r", encoding=args.e)
    stops = stops_parsers[args.stop_file_type](stop_file, summits, merge_stations)

    results_printers[args.f](summits, args)

def get_arguments():
    parser = argparse.ArgumentParser(
                    prog = "SOTAfilter.py",
                    description = "Return a list of SOTA summits near public transport sites ordered by distance to the user",
                    epilog = "Text at the bottom of help")

    parser.add_argument("stop_file_type", choices=stops_parsers.keys())
    parser.add_argument("-e", default="latin-1", help="File encoding for stop and summit files")
    parser.add_argument("stop_file")
    parser.add_argument("summit_file")
    parser.add_argument("region")
    parser.add_argument("-f", choices=["json", "csv"], default="csv", help="Output format. Either csv or geoJSON")
    parser.add_argument("-v", default=0, action="count", help="Print debug statements. Omit for no debug. -v for info. -vv for debug")

    args = parser.parse_args()

    log.setLevel(logging.WARNING - 10 * args.v)

    return args


if __name__ == "__main__":
    args = get_arguments()
    main(args)


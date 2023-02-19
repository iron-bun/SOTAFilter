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
import argparse
import json

distance_filter = 0.0625

def read_gb_ni_stops(stop_file,has_status,global_id):

    stops = dict()
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")

    for stop in stop_reader:
        if has_status and (stop["Latitude"] == "" or stop["Status"] == "inactive"):
            continue
    
        lat = float(stop["Latitude"])
        lon = float(stop["Longitude"])
        lat = round(lat / distance_filter)
        lon = round(lon / distance_filter)
        if lat not in stops:
            stops[lat] = dict()
        if lon not in stops[lat]:
            stops[lat][lon] = []
        stops[lat][lon].append((stop[global_id], stop["CommonName"], float(stop["Latitude"]), float(stop["Longitude"])))

    return stops

def read_gb_stops(stop_file):
    return read_gb_ni_stops(stop_file, True, "ATCOCode")

def read_ni_stops(stop_file):
    return read_gb_ni_stops(stop_file, False, "AtcoCode")

def read_ie_stops(stop_file):

    stop_reader = json.load(stop_file)
    stops = dict()

    for stop in stop_reader["features"]:
        if "isActive" in stop["properties"] and not stop["properties"]["isActive"]:
            continue

        lat = round(stop["geometry"]["coordinates"][1] / distance_filter)
        lon = round(stop["geometry"]["coordinates"][0] / distance_filter)

        if lat not in stops:
            stops[lat] = dict()
        if lon not in stops[lat]:
            stops[lat][lon] = []
        stops[lat][lon].append((stop["properties"]["AtcoCode"], stop["properties"]["CommonName"], stop["geometry"]["coordinates"][1], stop["geometry"]["coordinates"][0]))

    return stops

stops_parsers = {'gb':read_gb_stops, 'ni':read_ni_stops, 'ie':read_ie_stops}

def print_csv_results(stations):

    print("SummitCode, SummitLatitude, SummitLongitude, StationCode, StationName, StationLatitude, StationLongitude")
    stations = sorted(stations.items(), key=lambda x:x[1]["origin_dist"])
    for summit, data in stations:
        stops = sorted(data["stops"], key=lambda x:x[0])
        for stop in stops:
            print(f"{summit}, {data['lat']}, {data['lon']}, {stop[1][0]}, {stop[1][1]}, {stop[1][2]}, {stop[1][3]}")

def print_json_results(stations):
    results = []
    
    for summit in stations:
        tmp = {"name": summit, "coordinates":[stations[summit]['lat'], stations[summit]['lon']]}

        stops = []
        for stop in stations[summit]['stops']:
            stops.append({"name": stop[1][1], "coordinates":[stop[1][2], stop[1][3]]})
        tmp["stops"] = stops

        results.append(tmp)

    print(json.dumps(results))
    
results_printers = {'csv':print_csv_results, 'json':print_json_results}

def main(args):

    stops = stops_parsers[args.stop_file_type](args.stop_file)

    args.summit_file.readline()
    summit_reader = csv.DictReader(args.summit_file, delimiter=",", quotechar="\"")

    stations = dict()

    for summit in summit_reader:

        lat,lon = round(float(summit["Latitude"]) / distance_filter), round(float(summit["Longitude"]) / distance_filter)
        for i in range(lat-1, lat+2):
            for j in range(lon-1, lon+2):
                if i in stops and j in stops[i]:
                    for stop in stops[i][j]:
                        dist = (stop[2] - float(summit["Latitude"]))**2 + (stop[3] - float(summit["Longitude"]))**2
                        dist **= 0.5
                        if dist <= distance_filter:
                            origin_dist = (args.user_latitude - float(summit["Latitude"]))**2 + (args.user_longitude - float(summit["Longitude"]))**2
                            origin_dist **= 0.5
                            if args.r == None or args.r > origin_dist:
                                if summit["SummitCode"] not in stations:
                                    stations[summit["SummitCode"]] = {"lat":summit["Latitude"], "lon":summit["Longitude"], "origin_dist":origin_dist, "stops":[]}
                                stations[summit["SummitCode"]]["stops"].append((dist, stop))
    results_printers[args.f](stations)

def get_arguments():
    parser = argparse.ArgumentParser(
                    prog = "SOTAfilter",
                    description = "Return a list of SOTA summits near public transport sites ordered by distance to the user",
                    epilog = "Text at the bottom of help")

    parser.add_argument("stop_file_type", choices=["gb","ni","ie"], help="gb for Great Britian. ni for Northern Ireland. ie for Republic of Ireland")
    parser.add_argument("stop_file", type=argparse.FileType("r", encoding="latin-1"))
    parser.add_argument("summit_file", type=argparse.FileType("r", encoding="latin-1"))
    parser.add_argument("-r", type=float, default=None, help="Results range in distance from user lat/long")
    parser.add_argument("user_latitude", type=float)
    parser.add_argument("user_longitude", type=float)
    parser.add_argument("-f", choices=["json", "csv"], default="csv", help="Output format. Either csv or geoJSON")

    return parser.parse_args()


if __name__ == "__main__":
    args = get_arguments()
    main(args)


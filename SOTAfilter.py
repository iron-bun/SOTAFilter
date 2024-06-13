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
import xml.etree.ElementTree as ET
from collections import defaultdict
from math import cos, asin, radians, degrees, atan2, pi
import logging
from pyproj import CRS, Transformer
from datetime import date, datetime

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
    wgs84 = CRS("WGS84")
    bng = CRS("EPSG:27700")
    transformer = Transformer.from_crs(bng,wgs84)

    stops = defaultdict(list)
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")

    for stop in stop_reader:
        if has_status and stop["Status"] == "inactive":
            log.debug(f"Stop {stop['CommonName']} ({stop[global_id]}) omitted because it is inactive")
            continue

        if stop["Latitude"] == "" or stop["Longitude"] == "":
            lat,long = transformer.transform(int(stop['Easting']),int(stop['Northing']))
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

def read_gtfs_stops(stop_file, summits, merge_stop,transformer=None):
    read_csv_stops(stop_file, summits, merge_stop, "stop_id", "stop_name", "stop_lat", "stop_lon", None, transformer)

def read_kr_stops(stop_file, summits, merge_stop):
    read_csv_stops(stop_file, summits, merge_stop, "\ufeff정류장번호", "정류장명", "위도", "경도", None)

def read_csv_stops(stop_file, summits, merge_stop, ID="stop_id", NAME="stop_name", LAT="stop_lat", LON="stop_lon", TYPE=None, transformer=None):
    stops = defaultdict(list)
    stop_reader = csv.DictReader(stop_file, delimiter=",", quotechar="\"")
    log.info(stop_reader.fieldnames)
    read_stops(stop_reader, summits, merge_stop, ID, NAME, LAT, LON, TYPE, transformer)

def read_stops(stop_reader, summits, merge_stop, ID="stop_id", NAME="stop_name", LAT="stop_lat", LON="stop_lon", TYPE=None, transformer=None):
    for stop in stop_reader:

        if TYPE != None:
            stop_type = stop[TYPE]
        else:
            stop_type = ""

        if transformer == None:
            lat, lon = float(stop[LAT]), float(stop[LON])
        else:
            lat, lon = transformer.transform(float(stop[LAT]), float(stop[LON]))
            log.debug(f"Converted {stop[NAME]} ({stop[ID]}) from {stop[LAT]}, {stop[LON]} to {lat}, {lon}")

        merge_stop(summits, {"id":stop[ID], "name":stop[NAME], "lat":lat, "lon":lon, "StopType": stop_type})

def read_je_stops(stop_file, summits, merge_stop):
    stops = defaultdict(list)
    stop_reader = json.load(stop_file)
    read_stops(stop_reader["stops"], summits, merge_stop, "StopNumber", "StopName", "Latitude", "Longitude")

def read_im_stops(stop_file, summits, merge_stop):
    read_csv_stops(stop_file, summits, merge_stop, "Stop No", "Location", "Latitude", "Longitude", "StopType")

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
        lon, lat = geometry["coordinates"]
        lat, lon = float(lat), float(lon)

        merge_stop(summits, {"id":stop_id, "name":stop_name, "lat":lat, "lon":lon, "StopType": ""})

def read_netex_stops(stop_file, summits, merge_stop):
    stops = defaultdict(list)
    stop_reader = ET.parse(stop_file).getroot()

    ns = {'ns': 'http://www.netex.org.uk/netex'}

    for stop in stop_reader.findall("./ns:dataObjects/ns:SiteFrame/ns:stopPlaces/ns:StopPlace", namespaces=ns):
      validFrom = stop.find("./ns:ValidBetween/ns:FromDate", namespaces=ns).text
      validTo = stop.find("./ns:ValidBetween/ns:ToDate", namespaces=ns)

      if validTo == None or datetime.strptime(validFrom,"%Y-%m-%dT%H:%M:%S").date() < date.today() < datetime.strptime(validTo.text,"%Y-%m-%dT%H:%M:%S").date():
        stop_id = stop.attrib["id"]
        stop_name = stop.find("./ns:Name", namespaces=ns)
        stop_name = stop_name.text
        mode = stop.find("./ns:TransportMode", namespaces=ns).text
        if mode == "rail":
          mode = "RSE"

        lon, lat = stop.find("./ns:Centroid/ns:Location/ns:Longitude", namespaces=ns).text, stop.find("./ns:Centroid/ns:Location/ns:Latitude", namespaces=ns).text
        lon, lat = float(lon), float(lat)

        merge_stop(summits, {"id":stop_id, "name":stop_name, "lat":lat, "lon":lon, "StopType": mode})

def read_VT_stops(stop_file, summits, merge_stop):
    wgs84 = CRS("EPSG:4326")
    vspm = CRS("EPSG:32145")
    transformer = Transformer.from_crs(vspm,wgs84)
    read_csv_stops(stop_file, summits, merge_stop, "stop_id", "stop_name", "x", "y", None, transformer)

stops_parsers = {'kr':read_kr_stops,
                 'gb':read_gb_stops,
                 'ni':read_ni_stops,
                 'ie':read_ie_stops,
                 'gtfs':read_gtfs_stops,
                 'je':read_je_stops,
                 'im':read_im_stops,
                 'fr':read_fr_stops,
                 'netex':read_netex_stops,
                 'VT':read_VT_stops}

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
            tmp["bonusPoints"] = summit["bonusPoints"]
            tmp["coordinates"] = [summit["lat"], summit["lon"]]
            tmp["stops"] = []

            for angle, (dist, stop) in summit["cycling_stops"].items():
                tmp["stops"].append({"id": stop["id"], "name": stop["name"], "coordinates":[stop["lat"], stop["lon"]]})
            for angle, (dist, stop) in summit["walking_stops"].items():
                tmp["stops"].append({"id": stop["id"], "name": stop["name"], "coordinates":[stop["lat"], stop["lon"]]})

            results.append(tmp)

    print(json.dumps(results))
    
results_printers = {'csv':print_csv_results, 'json':print_json_results}

def filter_summits(summit, region):
    summit_code = summit["SummitCode"]
    region_code = summit_code[:summit_code.find("/")]
    if region_code != region:
        log.debug(f"discarding {summit['SummitCode']} as not in selected region ({args.region})")
        return False

    day, month, year = list(map(int, summit["ValidTo"].split("/")))
    if date(year, month, day) < date.today():
        log.debug(f"discarding {summit['SummitCode']} as no longer valid ({summit['ValidTo']})")
        return False
    return True

def read_summits(summit_file):
    summit_file.readline()
    summit_reader = csv.DictReader(summit_file, delimiter=",", quotechar="\"")

    summit_squares = defaultdict(list)

    for summit in filter(lambda s: filter_summits(s, args.region),summit_reader):

        lat,lon = float(summit["Latitude"]), float(summit["Longitude"])
        b_lat, b_lon = round(lat/bucket_distance), round(lon/bucket_distance)

        summit_squares[(b_lat, b_lon)].append({"summit_code":summit["SummitCode"], "name": summit["SummitName"], "points":summit["Points"], "bonusPoints":summit["BonusPoints"], "lat":lat, "lon":lon, "cycling_stops":{}, "walking_stops":{}})

    log.info(f"loaded {len(summit_squares)} squares of data")
    return summit_squares

def merge_stations(summits, stop):

    if stop["StopType"] in cycling_stop_types:
        filter_distance = cycling_distance
    else:
        filter_distance = walking_distance

    b_lat = round(stop["lat"]/bucket_distance)
    b_lon = round(stop["lon"]/bucket_distance)

    for i in range(b_lat-2, b_lat+3):
        for j in range(b_lon-2, b_lon+3):
            for summit in summits[(i, j)]:
                dist = hdist(summit["lat"], summit["lon"], stop["lat"], stop["lon"])
                if dist > filter_distance:
                    continue
                log.debug(f"testing summit {summit} against stop {stop}")

                if stop["StopType"] in cycling_stop_types:
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

    stop_file_type = ""
    for f in args.stop_files:
      if f in stops_parsers.keys():
        stop_file_type = f
        continue

      if stop_file_type == "":
          print("Specify at least one stop file type before any stop files")
          return

      stop_file = open(f, "r", encoding=args.e)
      stops_parsers[stop_file_type](stop_file, summits, merge_stations)

    results_printers[args.f](summits, args)

def get_arguments():
    parser = argparse.ArgumentParser(
                    prog = "SOTAfilter.py",
                    description = "Return a list of SOTA summits near public transport sites ordered by distance to the user",
                    epilog = "Text at the bottom of help")

    parser.add_argument("-e", default="latin-1", help="File encoding for stop and summit files")
    parser.add_argument("region")
    parser.add_argument("summit_file")
    parser.add_argument("stop_files", nargs="+")
    parser.add_argument("-f", choices=["json", "csv"], default="josn", help="Output format. Either csv or geoJSON")
    parser.add_argument("-v", default=0, action="count", help="Print debug statements. Omit for no debug. -v for info. -vv for debug")

    args = parser.parse_args()

    log.setLevel(logging.WARNING - 10 * args.v)

    return args


if __name__ == "__main__":
    args = get_arguments()
    main(args)


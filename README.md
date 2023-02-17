#### SOTA by Public Transport filter ####

This program is used to filter Summits on the Air locations against public transport infrastructure to find summits that are potentially accessible via public transport. The particular use case is journey planners will frequently fail to find a public transport route from you to the summit but if you can locate a nearby public transport stop and ask the planner to navigate to *that* everything works splendidly.

**Please note: The existence of a bus stop does not indicate the existence of a bus. It is vital to verify your travel plans before setting off**


### Usage ###

Dependencies are csv, json and argparse.

Download the stops data for the desired area:

* Great Britain: https://beta-naptan.dft.gov.uk/
* Northern Ireland: https://www.opendatani.gov.uk/dataset/translink-bus-stop-list
* Republic of Ireland: https://data.gov.ie/en\_GB/dataset/national-public-transport-access-nodes-naptan/resource/02871b06-937c-4232-a873-a3bc60e3d6ee

Download the summit data from SOTA as summitslist.csv: https://mapping.sota.org.uk/summitslist.csv

The program accepts an origin latitude and longitude (these are presently mandatory) and orders the list of summits by distance to that origin location, and then distance to stations in order of distance to that summit. For this mode run the script with:

`SOTAfilter [-h] [-r R] [-f {json,csv}] {gb,ni,ie} stop_file summit_file user_latitude user_longitude`

There is also a map.html file which uses leaflet (https://leafletjs.com/) to display results on an interactive map. To generate this run the script as follows:

`SOTAfilter.py -f json -r 1 <country code> <stops file> <summits file> <your latitude> <your longitude>  > stations.json`

Then open map.html in a browser and open the resulting stations.json file in the file browser. Navigate the map to your location. The -r argument is the range in which summits should be displayed in degrees. Too many results can make the map run slowly.

### To do list: ###

* Make the map auto-centre when a file is loaded.
* Make stations appear when a summit is clicked.

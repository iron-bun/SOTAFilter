## SOTA by Public Transport filter ##

This program is used to filter Summits on the Air locations against public transport infrastructure to find summits that are potentially accessible via public transport. The particular use case is my experience with journey planners that 
will frequently fail to find a public transport route from you to the summit, but if you can locate a nearby public transport stop and ask the planner to navigate to *that* everything works splendidly.

**Please note: The existence of a bus stop does not indicate the existence of a bus. It is vital to verify your travel plans before setting off**


### Usage ###

Download the stops data for the desired area:

* Great Britain: https://beta-naptan.dft.gov.uk/ licensed under the UK Open Government License (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
* Northern Ireland: https://www.opendatani.gov.uk/dataset/translink-bus-stop-list licensed under the UK Open Government Licence (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
* Republic of Ireland: https://data.gov.ie/en_GB/dataset/national-public-transport-access-nodes-naptan/resource/02871b06-937c-4232-a873-a3bc60e3d6ee with an unspecified license
* Norway: https://developer.entur.org/stops-and-timetable-data licensed under the NLOD 2.0 (https://data.norge.no/nlod/en/2.0)
* Germany: https://gtfs.de/en/feeds/de_full/ licensed under CC 4.0

Download the summit data from SOTA as summitslist.csv: https://mapping.sota.org.uk/summitslist.csv

The program can produce a CSV file from an origin latitude and longitude (these are presently mandatory) and orders the list of summits by distance to that origin location, and then distance to stations in order of distance to that summit. For this mode run the script with:

`SOTAfilter.py -f csv [-v] {gb,ni,ie,no} stop_file summit_file region`

There is also a index.html file which uses leaflet (https://leafletjs.com/) to display results on an interactive map. To generate the JSON for the map, run the script as follows:

`SOTAfilter.py -f json {gb,ni,ie,no} stop_file summit_file region > region.json`

Index.html will perform an AJAX request to load in the regions.json file, and from there allow the user to load in region specific data. Clicking on a summit will expand the associated stops.

### To do list: ###

* All these sources: https://www.transitwiki.org/TransitWiki/index.php/Publicly-accessible_public_transportation_data

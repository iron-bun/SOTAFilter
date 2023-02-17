SOTA by Public Transport filter

This program is used to filter Summits on the Air locations against public transport infrastructure to find summits that are potentially accessible via public transport.

**Please note: The existence of a bus stop does not indicate the existence of a bus. It is vital to verify your travel plans before setting off**

Dependencies are csv,json and argparse.

Download the stops data for the desired area:

* Great Britain: https://beta-naptan.dft.gov.uk/
* Northern Ireland: https://www.opendatani.gov.uk/dataset/translink-bus-stop-list
* Republic of Ireland: https://data.gov.ie/en\_GB/dataset/national-public-transport-access-nodes-naptan/resource/02871b06-937c-4232-a873-a3bc60e3d6ee

Download the summit data from SOTA as summitslist.csv: https://mapping.sota.org.uk/summitslist.csv

The program accepts an origin latitude and longitude (these are presently mandatory) and orders the list of summits by distance to that origin location, and then distance to stations in order of distance to that summit.

usage: SOTAfilter.py [-h] {gb,ni,ie} stop\_file summit\_file user\_latitude user\_longitude


SOTA by Public Transport filter

This program is used to filter Summits on the Air locations against public transport infrastructure to find summits that are potentially accessible via public transport.

Download the stops data for the desired area:

* Great Britain: https://beta-naptan.dft.gov.uk/
* Northern Ireland: https://www.opendatani.gov.uk/dataset/translink-bus-stop-list

Download the summit data from SOTA as summitslist.csv: https://mapping.sota.org.uk/summitslist.csv

The program accepts an oring latitude and longitude (these are presently mandatory) and orders the list of summits by distance to that origin location, and then distance to stations in order of distance to that summit.

usage: filter.py [-h] {gb,ni} stop\_file summit\_file user\_latitude user\_longitude


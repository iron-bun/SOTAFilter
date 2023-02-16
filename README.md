i

SOTA by Public Transport filter

This program is used to filter Summits on the Air locations against public transport infrastructure to find summits that are potentially accessible via public transport.

Download the stops data from the NapTAN website as Stops.csv: https://beta-naptan.dft.gov.uk/ Download the summit data from SOTA as summitslist.csv: https://mapping.sota.org.uk/summitslist.csv

run: 
    ./filter.py

Issues:

The stop data comes from the open Government data service and only covers Great Britain. Support for additional datasets from Northern Ireland and other countries are planned. Not every stop listed in the data has GPS co-ordinates. These are obviously excluded even though they may still be viable in reality.


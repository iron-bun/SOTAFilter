
if [[ ! -f sources/summitslist.csv ]] 
then 
  echo "summits list not found \(sources/summitslist.csv\)"
elif [[ ! -f sources/naptan.json ]]
then
  echo "Irish Naptan data not found \(sources/naptan.json\)"
elif [[ ! -f sources/gb_stops.csv ]]
then
  echo "GB stops data not found \(sources/gb_stops.csv\)"
elif [[ ! -f sources/09-05-2022busstop-list.csv ]]
then
  echo "NI stops data not found \(sources/09-05-2022busstop-list.csv\)"
elif [[ ! -f sources/no_stops.txt ]]
then
  echo "Norway stops data not found \(sources/no_stops.txt\)"
elif [[ ! -f sources/de_stops.txt ]]
then
  echo "Germany stops data not found \(sources/no_stops.txt\)"
else

time ./SOTAfilter.py -f json ie sources/naptan.json sources/summitslist.csv EI > data/EI.json
time ./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv G > data/G.json
time ./SOTAfilter.py -f json im sources/iom_stops.csv sources/summitslist.csv GD > data/GD.json
time ./SOTAfilter.py -f json ni sources/09-05-2022busstop-list.csv sources/summitslist.csv GI > data/GI.json
time ./SOTAfilter.py -f json je sources/jersey.json sources/summitslist.csv GJ > data/GJ.json
time ./SOTAfilter.py -f json -e utf-8 gb sources/gb_stops.csv sources/summitslist.csv GM > data/GM.json
time ./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv GW > data/GW.json
time ./SOTAfilter.py -f json -e utf-8 no sources/no_stops.txt sources/summitslist.csv LA > data/LA.json
time ./SOTAfilter.py -f json -e utf-8 de sources/de_stops.txt sources/summitslist.csv DM > data/DM.json
time ./SOTAfilter.py -f json -e utf-8 be sources/be_stops.txt sources/summitslist.csv ON > data/ON.json
time ./SOTAfilter.py -f json fr sources/public-transit.geojson sources/summitslist.csv F > data/F.json
time ./SOTAfilter.py -f json fr sources/public-transit.geojson sources/summitslist.csv FL > data/FL.json

fi

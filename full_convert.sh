
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
else

./SOTAfilter.py -f json ie sources/naptan.json sources/summitslist.csv EI > data/EI.json
./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv G > data/G.json
./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv GD > data/GD.json
./SOTAfilter.py -f json ni sources/09-05-2022busstop-list.csv sources/summitslist.csv GI > data/GI.json
./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv GJ > data/GJ.json
./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv GM > data/GM.json
./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv GU > data/GU.json
./SOTAfilter.py -f json gb sources/gb_stops.csv sources/summitslist.csv GW > data/GW.json
./SOTAfilter.py -f json no sources/no_stops.txt sources/summitslist.csv LA > data/LA.json

fi

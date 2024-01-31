
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

echo EI
time ./SOTAfilter.py -f json -e utf-8 ie sources/naptan.json sources/summitslist.csv EI > data/EI.json
echo G
time ./SOTAfilter.py -f json -e utf-8 gb sources/gb_stops.csv sources/summitslist.csv G > data/G.json
echo GD
time ./SOTAfilter.py -f json -e utf-8 im sources/iom_stops.csv sources/summitslist.csv GD > data/GD.json
echo GI
time ./SOTAfilter.py -f json ni sources/09-05-2022busstop-list.csv sources/summitslist.csv GI > data/GI.json
echo GJ
time ./SOTAfilter.py -f json -e utf-8 je sources/jersey.json sources/summitslist.csv GJ > data/GJ.json
echo GM
time ./SOTAfilter.py -f json -e utf-8 gb sources/gb_stops.csv sources/summitslist.csv GM > data/GM.json
echo GW
time ./SOTAfilter.py -f json -e utf-8 gb sources/gb_stops.csv sources/summitslist.csv GW > data/GW.json
echo LA
time ./SOTAfilter.py -f json -e utf-8 gtfs sources/no_stops.txt sources/summitslist.csv LA > data/LA.json
echo DM
time ./SOTAfilter.py -f json -e utf-8 gtfs sources/de_stops.txt sources/summitslist.csv DM > data/DM.json
echo ON
time ./SOTAfilter.py -f json -e utf-8 gtfs sources/be_stops.txt sources/summitslist.csv ON > data/ON.json
echo F
time ./SOTAfilter.py -f json -e utf-8 fr sources/public-transit.geojson sources/summitslist.csv F > data/F.json
echo FL
time ./SOTAfilter.py -f json -e utf-8 fr sources/public-transit.geojson sources/summitslist.csv FL > data/FL.json
echo HL
time ./SOTAfilter.py -f json -e utf-8 kr sources/2022년_전국버스정류장\ 위치정보_데이터.csv sources/summitslist.csv HL > data/HL.json
echo PA
time ./SOTAfilter.py -f json -e utf-8 gtfs sources/nl_stops.txt sources/summitslist.csv PA > data/PA.json
echo SM
time ./SOTAfilter.py -f json -e utf-8 xml sources/_stops.xml sources/summitslist.csv SM > data/SM.json

fi

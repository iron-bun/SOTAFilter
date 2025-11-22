function fetch () {
if [[ ! $(find sources/$1 -mtime -100 -print) ]]; then
  echo "File ${1} does not exist or is older than 100 days"

  cd sources
  wget -O $1 $2 
  cd ..
fi
}

function fetch_from_zip() {
if [[ ! $(find sources/$1 -mtime -100 -print) ]]; then
  echo "File ${1} does not exist or is older than 100 days"

  mkdir -p downloads
  rm downloads/*
  cd downloads
  wget $2 -O data.zip
  cd ..
  unzip -p downloads/data.zip $4 > sources/$1
fi
}

echo summits
fetch "summitslist.csv" "https://storage.sota.org.uk/summitslist.csv"

fetch_from_zip "de_stops.txt" "https://download.gtfs.de/germany/free/latest.zip" "lastest.zip" "stops.txt"
if [[ data/DM.json -ot sources/de_stops.txt ]] || [[ data/DM.json -ot sources/summitslist.csv ]]; then
  echo DM
  time ./SOTAfilter.py -f json -e utf-8 DM sources/summitslist.csv gtfs sources/de_stops.txt > data/DM.json
fi

fetch "NaPTAN.json" "https://www.transportforireland.ie/transitData/Data/NaPTAN.json"
if [[ data/EI.json -ot sources/NaPTAN.json ]] || [[ data/EI.json -ot sources/summitslist.csv ]]; then
  echo EI
  time ./SOTAfilter.py -f json -e utf-8 EI sources/summitslist.csv ie sources/NaPTAN.json > data/EI.json
fi

fetch_from_zip "public-transit.geojson" "https://www.data.gouv.fr/fr/datasets/r/ba635ef6-b506-4381-9dc9-b51ad3c482ab" "public-transit.geojson.zip" "public-transit.geojson"
if [[ data/F.json -ot sources/public-transit.geojson ]] || [[ data/F.json -ot sources/summitslist.csv ]]; then
  echo F
  time ./SOTAfilter.py -f json -e utf-8 F sources/summitslist.csv fr sources/public-transit.geojson > data/F.json
fi
if [[ data/FL.json -ot sources/public-transit.geojson ]] || [[ data/FL.json -ot sources/summitslist.csv ]]; then
  echo FL
  time ./SOTAfilter.py -f json -e utf-8 FL sources/summitslist.csv fr sources/public-transit.geojson > data/FL.json
fi

fetch "gb_stops.txt" "https://beta-naptan.dft.gov.uk/Download/National/csv"
if [[ data/G.json -ot sources/gb_stops.csv ]] || [[ data/G.json -ot sources/summitslist.csv ]]; then
  echo G
  time ./SOTAfilter.py -f json -e utf-8 G sources/summitslist.csv gb sources/gb_stops.csv > data/G.json
fi
if [[ data/GM.json -ot sources/gb_stops.csv ]] || [[ data/GM.json -ot sources/summitslist.csv ]]; then
  echo GM
  time ./SOTAfilter.py -f json -e utf-8 GM sources/summitslist.csv gb sources/gb_stops.csv > data/GM.json
fi

if [[ data/GW.json -ot sources/gb_stops.csv ]] || [[ data/GW.json -ot sources/summitslist.csv ]]; then
  echo GW
  time ./SOTAfilter.py -f json -e utf-8 GW sources/summitslist.csv gb sources/gb_stops.csv > data/GW.json
fi

if [[ data/GJ.json -ot sources/jersey.json ]] || [[ data/GJ.json -ot sources/summitslist.csv ]]; then
  echo GJ
  time ./SOTAfilter.py -f json -e utf-8 GJ sources/summitslist.csv je sources/jersey.json > data/GJ.json
fi

echo GI
time ./SOTAfilter.py -f json GI sources/summitslist.csv ni sources/bus-stop-list-january-2018.csv > data/GI.json

if [[ data/GD.json -ot sources/iom_stops.csv ]] || [[ data/GD.json -ot sources/summitslist.csv ]]; then
  echo GD
  time ./SOTAfilter.py -f json -e utf-8 GD sources/summitslist.csv im sources/iom_stops.csv > data/GD.json
fi

if [[ data/HL.json -ot sources/hl_stops.txt ]] || [[ data/HL.json -ot sources/summitslist.csv ]]; then
  echo HL
  time ./SOTAfilter.py -f json -e utf-8 HL sources/summitslist.csv kr sources/국토교통부_전국 버스정류장 위치정보_20241031.csv > data/HL.json
fi

fetch_from_zip "no_stops.txt" "https://storage.googleapis.com/marduk-production/outbound/gtfs/rb_norway-aggregated-gtfs.zip" "rb_norway-aggregated-gtfs.zip" "stops.txt"
if [[ data/LA.json -ot sources/no_stops.txt ]] || [[ data/LA.json -ot sources/summitslist.csv ]]; then
  echo LA
  time ./SOTAfilter.py -f json -e utf-8 LA sources/summitslist.csv gtfs sources/no_stops.txt > data/LA.json
fi

if [[ data/LX.json -ot sources/lx_stops.txt ]] || [[ data/LX.json -ot sources/summitslist.csv ]]; then
  echo LX
  time ./SOTAfilter.py -f json -e utf-8 LX sources/summitslist.csv gtfs sources/lx_stops.txt > data/LX.json
fi

fetch_from_zip be_stops.txt https://opendata.tec-wl.be/Current%20GTFS/TEC-GTFS.zip null stops.txt
if [[ data/ON.json -ot sources/be_stops.txt ]] || [[ data/ON.json -ot sources/summitslist.csv ]]; then
  echo ON
  time ./SOTAfilter.py -f json -e utf-8 ON sources/summitslist.csv gtfs sources/be_stops.txt > data/ON.json
fi

fetch_from_zip nl_stops.txt https://gtfs.ovapi.nl/nl/gtfs-nl.zip null stops.txt
if [[ data/PA.json -ot sources/nl_stops.txt ]] || [[ data/PA.json -ot sources/summitslist.csv ]]; then
  echo PA
  time ./SOTAfilter.py -f json -e utf-8 PA sources/summitslist.csv gtfs sources/nl_stops.txt > data/PA.json
fi

if [[ data/SM.json -ot sources/_stops.xml ]] || [[ data/SM.json -ot sources/summitslist.csv ]]; then
  echo SM
  time ./SOTAfilter.py -f json -e utf-8 SM sources/summitslist.csv netex sources/_stops.xml > data/SM.json
fi

fetch_from_zip vk7_stops.txt https://www.transport.tas.gov.au/__data/assets/file/0011/557615/tas_gtfs.zip null stops.txt
if [[ data/VK7.json -ot sources/vk7_stops.txt ]] || [[ data/VK7.json -ot sources/summitslist.csv ]]; then
  echo VK7
  time ./SOTAfilter.py -f json -e utf-8 VK7 sources/summitslist.csv gtfs sources/vk7_stops.txt > data/VK7.json
fi

if [[ data/W1.json -ot ./sources/FS_VCGI_OPENDATA_Trans_PUBLICTRANS_point_stops_SP_v1_4748420022732475507.csv ]] || [[ data/W1.json -ot ./sources/CT_STOPS.txt ]] || [[ data/W1.json -ot ./sources/RTA_Bus_Stops.csv ]] || [[ data/W1.json -ot ./sources/Intercity_Bus_Atlas_Stops_4418415565274310757.csv ]] || [[ data/W1.json -ot sources/summitslist.csv ]]; then
  echo W1
  time ./SOTAfilter.py W1 sources/summitslist.csv VT ./sources/Intercity_Bus_Atlas_Stops_4418415565274310757.csv gtfs ./sources/RTA_Bus_Stops.csv ./sources/CT_STOPS.txt VT ./sources/FS_VCGI_OPENDATA_Trans_PUBLICTRANS_point_stops_SP_v1_4748420022732475507.csv > data/W1.json
fi

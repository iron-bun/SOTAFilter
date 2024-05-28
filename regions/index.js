    let global_map;

    function init_map() {
        global_map = L.map('map', {center: [56.55285481198921, -4.0240158842363245], zoom:6});

        let osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '<a href="http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/">data &copy; Local Government Boundary Commission for Scotland, 2014, licensed under the Open Government Licence</a> | maps &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(global_map);

var regionLayer = L.layerGroup();
fetch("./borders_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./central_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./dumfries_and_galloway_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./fife_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./grampian_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./highland_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./lothian_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./orkney_islands_area_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./shetland_islands_area_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./strathclyde_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./tayside_region_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

fetch("./western_isles_islands_area_2nd.json")
  .then(response => response.json())
  .then(geojsonFeature => L.geoJSON(geojsonFeature).addTo(regionLayer));

regionLayer.addTo(global_map);

    }



    let global_map;

    function init_map() {
        global_map = L.map('map', {center: [56.55285481198921, -4.0240158842363245], zoom:6});

        let osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '<a href="http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/">data &copy; Local Government Boundary Commission for Scotland, 2014, licensed under the Open Government Licence</a> | maps &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(global_map);

        var layerControl = L.control.layers(null, null).addTo(global_map);

        //Wales
        var regions = ["Clywd", "Dyfed", "Gwent", "Gwynedd", "Mid Glamorgan", "Powys", "South Glamorgan", "West Glamorgan"];
        add_regions(regions, layerControl);

        //Scotland
        var regions = ["Borders", "Central", "Dumfries and Galloway", "Fife", "Grampian", "Highland", "Lothain", "Orkney", "Shetland", "Strathclyde", "Tayside", "Western Isles"];
        add_regions(regions, layerControl);

    }

    function add_regions(regions, layerControl) {
       regions.forEach((name) => {
          var region = L.geoJSON();
          layerControl.addOverlay(region, name)
          region.onAdd = () => {
          fetch(`./${name.toLowerCase().replace(' ', '_')}.json`)
             .then(response => response.json())
             .then(geojsonFeature => region.addData(geojsonFeature));
          };
       });
    }

    let global_map;
    let global_summits;
    let summits = {}
    let global_stops;

    var greenIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    function init_map() {
        global_map = L.map('map', {center: [55.910945, -3.201114], zoom:10});

        var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(global_map);

        global_summits = L.markerClusterGroup().addTo(global_map);
        global_stops = L.layerGroup().addTo(global_map);

        var client = new XMLHttpRequest();
        client.onreadystatechange = () => { if (client.readyState === 4 && client.status === 200) load_regions(client.responseText); };
        client.open('GET', './data/regions.json');
        client.send();
    }

    function load_regions(contents) {

        var results = JSON.parse(contents);

        var region_selector = document.getElementById('region_selector');
        region_selector.disabled = false;

        for (var i=0; i<results.length; i++) {
            var opt = document.createElement('option');

            opt.value = results[i].region;
            opt.innerHTML = results[i].description;
            region_selector.appendChild(opt);
        }
    }
    function get_features() {

        var region_selector = document.getElementById('region_selector');
        if (region_selector.value == 'null') { return; }

        var client = new XMLHttpRequest();

        client.onreadystatechange = () => { if (client.readyState === 4 && client.status === 200) load_features(client.responseText); };
        client.open('GET', `./data/${region_selector.value}.json`);
        client.send();
    }

    function load_features(contents) {

        global_summits.clearLayers();
        global_stops.clearLayers();
        summits = {}

        var features = JSON.parse(contents);

        var min_lat = null, max_lat = null, min_lon = null, max_lon = null;

        for (var i=0; i<features.length; i++) {

            var lat = features[i].coordinates[0], lon = features[i].coordinates[1];
            if (min_lat == null || min_lat > lat) { min_lat = lat; }
            if (max_lat == null || max_lat < lat) { max_lat = lat; }
            if (min_lon == null || min_lon > lon) { min_lon = lon; }
            if (max_lon == null || max_lon < lat) { max_lon = lon; }

            var popupText = "<a href='https://sotl.as/summits/" + features[i].id + "' target='_new'>" + features[i].id + "</a></br>" + features[i].name;
            var summit = L.marker(features[i].coordinates).bindPopup(popupText);

            stops = features[i].stops;
            var tmp = [];
            for (var j=0; j<stops.length; j++) {
                popupText = stops[j].name + "</br><a href='https://www.google.com/maps/dir/?api=1&destination=" + stops[j].coordinates[0] + "," + stops[j].coordinates[1] + "&travelmode=transit' target='_new'>directions</a>";
                tmp.push(L.marker(stops[j].coordinates, {icon:greenIcon}).bindPopup(popupText));
            }

            var lg = L.layerGroup(tmp);

            summit.on('click', getClickEvent(features[i].id, lg));
            summit.on('remove', getRemoveEvent(lg));

            global_summits.addLayer(summit);
            summits[features[i].id] = summit;
            
        }

        if (min_lat != null && min_lon != null)
            global_map.fitBounds([[min_lat, min_lon], [max_lat,max_lon]]);

    }
    function getRemoveEvent(thisLayerGroup) {
        return (e) => {
            global_stops.removeLayer(thisLayerGroup);
        }
    }

    function getClickEvent(summit_id, thisLayerGroup) {
        return (e) => {
            global_stops.eachLayer((layer) => { layer.remove(); });
            global_stops.addLayer(thisLayerGroup);
            get_routes(summit_id, thisLayerGroup);
        }
    }

    var cached_routes = {};
    function get_routes(summit_id, thisLayerGroup) {

        if (summit_id in cached_routes) { 
            display_routes(summit_id, thisLayerGroup);

        } else {
            var client = new XMLHttpRequest();

            client.onreadystatechange = () => { if (client.readyState === 4 && client.status === 200) load_routes(summit_id, thisLayerGroup, client.responseText); };
            client.open('GET', `https://api-db.sota.org.uk/smp/gpx/summit/${summit_id}`);
            client.send();
        }
    }

    function load_routes(summit_id, thisLayerGroup, contents) {
        cached_routes[summit_id] = [];

        var routes = JSON.parse(contents);
        for (var i = 0; i < routes.length; i++) {
            route = [];
            for (var j = 0; j < routes[i].points.length; j++) {
                route.push([routes[i].points[j].latitude, routes[i].points[j].longitude]);
            }
            cached_routes[summit_id].push(route);
        }
        display_routes(summit_id, thisLayerGroup);
    }

    function display_routes(summit_id, thisLayerGroup) {
        cached_routes[summit_id].forEach((route) => { L.polyline(route, {color: 'red'}).addTo(thisLayerGroup); });
    }


  function highlight_summit() {
      var id = document.getElementById("summit_ref").value.toUpperCase();
      if (id in summits) {
          global_summits.zoomToShowLayer(summits[id]);
          summits[id].fire('click');
      }
  }

  function check_search(e) {
    if (e && e.keyCode == 13) {
        highlight_summit()
    }
  }

  function show_hide_faq() {
    var faq = document.getElementById("faq");
    if (!faq.style.display || faq.style.display == "none") {
        faq.style.display = "block";
    } else {
        faq.style.display = "none";
    }
  }


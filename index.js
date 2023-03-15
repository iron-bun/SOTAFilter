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
        global_map = L.map('map', {center: [56.05331379149255, -9.889521032420252], zoom:10});

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

        results.forEach((result) => {
            var opt = document.createElement('option');

            opt.value = result.region;
            opt.innerHTML = result.description;
            region_selector.appendChild(opt);
        });


        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const summit_ref = urlParams.get('summit');
        if (summit_ref != null)
            highlight_summit(summit_ref);
    }

    function get_features(summit_ref=null) {

        var region_selector = document.getElementById('region_selector');
        if (region_selector.value == 'null') { return; }

        var client = new XMLHttpRequest();

        client.onreadystatechange = () => { if (client.readyState === 4 && client.status === 200) load_features(client.responseText, summit_ref); };
        client.open('GET', `./data/${region_selector.value}.json`);
        client.send();
    }

    function load_features(contents, summit_ref) {

        global_summits.clearLayers();
        summits = {}

        var features = JSON.parse(contents);

        features.forEach( (feature) => {

            var popupText = "<a href='https://sotl.as/summits/" + feature.id + "' target='_new'>" + feature.id + "</a></br>" + feature.name;
            var summit = L.marker(feature.coordinates).bindPopup(popupText);

            var lg = L.layerGroup();
            feature.stops.forEach( (stop) => {
                popupText = stop.name + "</br><a href='https://www.google.com/maps/dir/?api=1&destination=" + stop.coordinates[0] + "," + stop.coordinates[1] + "&travelmode=transit' target='_new'>directions</a>";
                L.marker(stop.coordinates, {icon:greenIcon}).bindPopup(popupText).addTo(lg);
            });


            summit.on('click', getClickEvent(feature.id, lg));
            summit.on('remove', getRemoveEvent(lg));

            global_summits.addLayer(summit);
            summits[feature.id] = summit;
            
        });

        if (summit_ref in summits)
            highlight_summit(summit_ref);
        else
            global_map.fitBounds(global_summits.getBounds());

    }

    function getRemoveEvent(thisLayerGroup) {
        return (e) => {
            thisLayerGroup.remove();
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
        routes.forEach( (route) => {
            tmp = [];
            route.points.forEach( (point) => {
                tmp.push([point.latitude, point.longitude]);
            });
            cached_routes[summit_id].push(tmp);
        });
        display_routes(summit_id, thisLayerGroup);
    }

    function display_routes(summit_id, thisLayerGroup) {
        cached_routes[summit_id].forEach((route) => { L.polyline(route, {color: 'red'}).addTo(thisLayerGroup); });
    }


  function highlight_summit(summit_ref) {

      summit_ref = summit_ref.toUpperCase();
      let search_region = summit_ref.split('/')[0];
      let region_selector = document.getElementById('region_selector');

      if (search_region != region_selector.value) {
          region_selector.value = search_region;
          get_features(summit_ref);
      }

      else if (summit_ref in summits) {
          global_summits.zoomToShowLayer(summits[summit_ref]);
          summits[summit_ref].fire('click');
      }
  }

  function check_search(e) {
    if (e && e.keyCode == 13) {
        highlight_summit(e.target.value);
    }
  }
  function go_search() {
    let summit_ref = document.getElementById('summit_ref').value;
    highlight_summit(summit_ref);
  }

  function show_hide_faq() {
    var faq = document.getElementById("faq");
    if (!faq.style.display || faq.style.display == "none") {
        faq.style.display = "block";
    } else {
        faq.style.display = "none";
    }
  }


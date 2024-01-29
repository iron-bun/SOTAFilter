    let global_map;

    let greenIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    let goldIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    function init_map() {
        global_map = L.map('map', {center: [56.05331379149255, -9.889521032420252], zoom:10});

        let osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(global_map);

        let regions = L.control({position: 'topright'});
        regions.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');
            div.innerHTML = '<select id="region_selector"></select>';
            div.firstChild.onmousedown = div.firstChild.ondblclick = L.DomEvent.stopPropagation;
            div.onchange = get_features;

            var client = new XMLHttpRequest();
            client.onreadystatechange = () => { if (client.readyState === 4 && client.status === 200) load_regions(client.responseText, div); };
            client.open('GET', './data/regions.json');
            client.send();

            return div;
        };
        regions.addTo(global_map);

        let points = L.control({position: 'topright'});
        points.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');
            div.innerHTML = '<select id="points_filter"><option value="All">All points</option><option>1</option><option>2</option><option>4</option><option>6</option><option>8</option><option>10</option></select>';
            div.firstChild.onmousedown = div.firstChild.ondblclick = L.DomEvent.stopPropagation;
            div.onchange = get_features;
            return div;
        };
        points.addTo(global_map);

	let markersLayer = new L.layerGroup(null, {type:"summits"});  //layer contain searched elements

	global_map.addLayer(markersLayer);

	let controlSearch = new L.Control.Search({
		position:'topright',
		layer: markersLayer,
		zoom: 12,
		marker: false
	});
        controlSearch.on('search:locationfound', (opts)=>{opts.layer.fire('click');});

	global_map.addControl( controlSearch );

    }

    function load_regions(contents, div) {

        let results = JSON.parse(contents);

        let region_selector = div.firstChild;
        region_selector.disabled = false;

        results.forEach((result) => {
            let opt = document.createElement('option');

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

        let region_selector = document.getElementById('region_selector');
        if (region_selector.value == 'null') { return; }

        let client = new XMLHttpRequest();

        client.onreadystatechange = () => { if (client.readyState === 4 && client.status === 200) load_features(client.responseText, summit_ref); };
        client.open('GET', `./data/${region_selector.value}.json`);
        client.send();
    }

    function load_features(contents, summit_ref) {

        var features = JSON.parse(contents);
        let points_filter = document.getElementById('points_filter').value;

        var summit_layer = null;
        global_map.eachLayer((layer) => {if (layer.options.type == "summits")
            summit_layer = layer;
        });
        summit_layer.eachLayer((layer) => { layer.remove(); });
        var marker_layer = L.markerClusterGroup();

        var found_summit = false;

        features.forEach( (feature) => {if (points_filter == "All" || points_filter == feature.points) {

            var popupText = "<a href='https://sotl.as/summits/" + feature.id + "' target='_new'>" + feature.id + "</a></br>" + feature.name + " (" + feature.points;
            if (feature.bonusPoints == "undefined" || feature.bonusPoints == "0"){
              popupText += ")";
              var summit = L.marker(feature.coordinates, {type:"summit", title:feature.id + " " + feature.name, name:feature.id, stops:feature.stops}).bindPopup(popupText).addTo(marker_layer);
            } else {
              popupText += "+" + feature.bonusPoints + ")";
              var summit = L.marker(feature.coordinates, {icon:goldIcon, type:"summit", title:feature.id + " " + feature.name, name:feature.id, stops:feature.stops}).bindPopup(popupText).addTo(marker_layer);
            }
            summit.on('click', summitClicked);
            summit.on('remove', summitRemoved);

            if (feature.id == summit_ref) found_summit = true;
            
        }});

        marker_layer.addTo(summit_layer);

        if (found_summit)
            highlight_summit(summit_ref)
        else {
            global_map.fitBounds(marker_layer.getBounds());
        }


    }

    function summitClicked(e) {
        global_map.eachLayer((layer) => {if (layer.options.type == "stops") layer.remove();});

        var lg = L.layerGroup(null, {parent:e.target.options.name, type:"stops"});
        e.target.options.stops.forEach( (stop) => {
            popupText = stop.name + "</br><a href='https://www.google.com/maps/dir/?api=1&destination=" + stop.coordinates[0] + "," + stop.coordinates[1] + "&travelmode=transit' target='_new'>directions</a>";
            L.marker(stop.coordinates, {icon:greenIcon}).bindPopup(popupText).addTo(lg);
        });

        get_routes(e.target.options.name, lg);
        lg.addTo(global_map);
    }

    function summitRemoved(e) {
        global_map.eachLayer((layer) => {if (layer.options.type == "stops" && layer.options.parent == e.target.options.name) layer.remove()});
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

      else {
          global_map.eachLayer((layer) => { if (layer.options.type == "summits") {
              layer.eachLayer((clusterLayer) => {clusterLayer.eachLayer((summit) => {if (summit.options.name == summit_ref) {
                  clusterLayer.zoomToShowLayer(summit);
                  summit.fire('click');
                  }
               });})
          }});
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


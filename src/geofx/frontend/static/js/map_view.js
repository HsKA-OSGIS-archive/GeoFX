var is_currently_inside = false;
var geofence_features = [];

function evaluatePosition(coordinates){
  var is_inside = false;
  for(var i=0; i < geofence_features.length; i++){
    is_inside = geofence_features[i].getGeometry().intersectsCoordinate(coordinates);
    if(is_inside){
      break;
    }
  }
  if(is_inside){
    if(!is_currently_inside){
      is_currently_inside = true;
      $('#fence_enter_message').show();
      $('#fence_leave_message').hide();
      $('#geofenceAlertModal').modal();
    }      
  } else {
    if(is_currently_inside){
      is_currently_inside = false;
      $('#fence_enter_message').hide();
      $('#fence_leave_message').show();
      $('#geofenceAlertModal').modal();
    }      
  }
}

function initMapView(){
  const map_data = JSON.parse(document.getElementById('map_data').textContent);

  var zoom = 7;
  var center = ol.proj.fromLonLat([10, 50]);
  if(map_data.map_center && map_data.map_zoom_level){
    zoom = map_data.map_zoom_level;
    var data = JSON.parse(map_data.map_center);
    center = ol.proj.fromLonLat([data.lon, data.lat]);
  }
  var map_view = new ol.View({
    center: center,
    zoom: zoom
  });

  var geolocation = new ol.Geolocation({
    trackingOptions: {
      enableHighAccuracy: true,
    },
    projection: map_view.getProjection(),
  });
  geolocation.setTracking(true);

  var accuracyFeature = new ol.Feature();
  geolocation.on('change:accuracyGeometry', function () {
    accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
  });

  var positionFeature = new ol.Feature();
  positionFeature.setStyle(
    new ol.style.Style({
      image: new ol.style.Circle({
        radius: 6,
        fill: new ol.style.Fill({
          color: '#3399CC',
        }),
        stroke: new ol.style.Stroke({
          color: '#fff',
          width: 2,
        }),
      }),
    })
  );

  // handle geolocation error.
  geolocation.on('error', function (error) {
    // todo: show error to user in message bar
    console.log(error);
  });

  geolocation.on('change:position', function () {
    var coordinates = geolocation.getPosition();
    positionFeature.setGeometry(coordinates ? new ol.geom.Point(coordinates) : null);
    evaluatePosition(coordinates);
  });

  var wfs_source = new ol.source.Vector({
    format: new ol.format.GeoJSON()
  });
  wfs_source.on('change', function(e){
    geofence_features = wfs_layer_geofence.getSource().getFeatures();
    evaluatePosition(geolocation.getPosition())
  });
  wfs_source.setUrl( '/geoserver/geofx/'
  + 'wfs?service=WFS&version=1.1.0&request=GetFeature&&typeName=geofx:geofence_'
  + map_data.url_name + '&outputFormat=application/json&srsname=EPSG:3857')

  var wfs_layer_geofence = new ol.layer.Vector({
    source : wfs_source,
    style: new ol.style.Style({
      fill: new ol.style.Fill({
        color: '#721c24aa',
      }),
      stroke: new ol.style.Stroke({
        color: '#721c24',
        width: 2,
      }),
    })
  });
  wfs_source.refresh();
  

  var map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      }),
      wfs_layer_geofence,
      new ol.layer.Vector({
        source: new ol.source.Vector({
          features: [accuracyFeature, positionFeature]
        })
      })
    ],
    view: map_view
  });

}

document.addEventListener('DOMContentLoaded', function() {
  initMapView();
});
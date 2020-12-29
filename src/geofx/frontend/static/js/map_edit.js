const map_data = JSON.parse(document.getElementById('map_data').textContent);
console.log(map_data)
var wms_layer_test = new ol.layer.Tile({
    source : new ol.source.TileWMS(({
        url : "http://localhost:8080/geoserver/geofx/wms?",
        params : {
            "LAYERS" : "geofence_" + map_data['url_name'],
            'VERSION' : "1.3.0",
            "TILED" : "true",
            "TYPE" : 'base'
        }
    }))
});

var map = new ol.Map({
    target: 'map',
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM()
        }),
        wms_layer_test
    ],
    view: new ol.View({
        center: ol.proj.fromLonLat([10, 50]),
        zoom: 7
    })
});

function initMapEdit(){
  $('#polygonUploadForm').submit(function(){
    var url = $(this).attr('action');
    var formData = new FormData();
    // append the geojson file
    formData.append('geofencing_polygon', document.getElementById('inputGeofencingFile').files[0]);
    // append the csrf token and layer name
    $('#polygonUploadForm').serializeArray().forEach(elem => {
      formData.append(elem.name, elem.value);
    });
   fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: formData // body data type must match "Content-Type" header
  }).then(response => {
    if(response.status === 200) {
      return response.json();
    }
  }).then(jsondata => {
    var alert =  $('.alert');
    console.log(jsondata)
    if(jsondata.success) {
      alert.removeClass('alert-danger');
      alert.addClass('alert-success');
      $('.alert-text').text('Geofencing file uploaded successfully');
    } else {
      alert.addClass('alert-danger');
      alert.removeClass('alert-success');
      $('.alert-text').text('Upload failed - error: ' + jsondata.error);
    }
    alert.show();
  });
    return false;
  })
}

document.addEventListener('DOMContentLoaded', function() {
  initMapEdit();
});
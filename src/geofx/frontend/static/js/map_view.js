var wms_layer_test = new ol.layer.Tile({
    source : new ol.source.TileWMS(({
        url : "http://localhost:8080/geoserver/geofx/wms?",
        params : {
            "LAYERS" : "geofx_app_geofencepoly",
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
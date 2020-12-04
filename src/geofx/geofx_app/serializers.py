from rest_framework import serializers

from .models import Map

class MapSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Map
        fields = ('url_name', 'display_name', 'description',\
            'title', 'geofencing_message', 'map_center',\
            'map_zoom_level', 'basemap', 'geofencing_layer_name')
        